from datetime import datetime
from decimal import Decimal
import json
from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator
from aiohttp import ClientSession, TCPConnector
from fastapi import APIRouter, FastAPI, Depends, File, Form, HTTPException, UploadFile
from aiokafka import AIOKafkaProducer  # type: ignore
from app.kafka_producer import get_kafka_producer
from app.kafka_consumer import (
    consume_events,
    get_kafka_consumer,
    consume_response_from_kafka,
)

from app import config
from app.operations import get_customer_information, get_order_by_guid, get_order_by_id, get_products_by_ids, get_token

# from shared.models.brand import PublicBrand
# from shared.models.category import PublicCategory
# from shared.models.product import CreateProduct, Product, PublicProduct, UpdateProduct
from shared.models.order_detail_model import PublicOrderWithDetail
# from shared.models.order_detail import PublicOrderDetail
from shared.models.payment import PaymentFailure, PaymentInfo, PaymentSuccessStatus
from shared.models.token import Token, TokenData
from shared.models.user import User
import asyncio
from authorizenet import apicontractsv1
from authorizenet.apicontrollers import createTransactionController

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("starting lifespan process")
    config.client_session = ClientSession(connector=TCPConnector(limit=100))
    await asyncio.sleep(10)
    asyncio.create_task(
        consume_events(config.KAFKA_ORDER_TOPIC, config.KAFKA_ORDER_CONSUMER_GROUP_ID)
    )
    yield
    await config.client_session.close()


app = FastAPI(lifespan=lifespan, title="Hello World API with DB")

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
    dependencies=[Depends(get_token)],
    responses={404: {"description": "Not found"}},
)


@app.get("/")
def main():
    return {"message": "Hello World from paymentss"}


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super(CustomJSONEncoder, self).default(obj)


@router.post("/pay")
async def process_payment(
    payment_info: PaymentInfo,
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
    token: Annotated[TokenData, Depends(get_token)],
):
    if token.userid != payment_info.customer_id:
        raise HTTPException(status_code=422, detail="Invalid user id")

    # GET ORDER INFO WITH ORDER DETAIL HAVING PRODUCT ID
    order_info = await get_order_by_id(payment_info.order_id)

    if not order_info:
        raise HTTPException(status_code=422, detail="Invalid order1")

    # GET CUSTOMER INFORMATION
    customer_id = order_info.get("customer_id")
    customer_info = await get_customer_information(customer_id)
    customer_instance = User(**customer_info)
    customer_info = User.model_validate(customer_instance)
    
    # GET IDS OF PRODUCTS IN ORDER DETAIL
    product_ids = [str(product["id"]) for product in order_info.get("order_details")]
    product_ids_str = ",".join(product_ids)

    # GET PRODUCTS DETAIL USING IDS IN ORDER DETAIL
    products = await get_products_by_ids(product_ids_str)

    # GET DICTIONARY OF PRODUCT ID AND PRODUCT NAME
    product_dict = {product["id"]: product["name"] for product in products}

    # ATTACHED PRODUCT NAME WITH ORDER DETAIL USING PRODUCT ID
    # for order_detail in order_info.get("order_details"):
    #     order_detail["product_name"] = product_dict[order_detail["product_id"]]
    
    #order_detail_instance = PublicOrderDetail(order_detail[0])
    order_instance = PublicOrderWithDetail(**order_info)
    order_info = PublicOrderWithDetail.model_validate(order_instance)
    
    # ATTACHED PRODUCT NAME WITH ORDER DETAIL USING PRODUCT ID
    for order_detail in order_info.order_details:
        order_detail.product_name = product_dict[order_detail.product_id]
        
    # =========================================================================================
    # CREATE PAYMENT TRANSACTION
    # =========================================================================================
    # Create a merchantAuthenticationType object with authentication details
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = config.API_LOGIN_ID
    merchantAuth.transactionKey = config.TRANSACTION_KEY

    # Create the payment data for a credit card
    creditCard = apicontractsv1.creditCardType()
    creditCard.cardNumber = payment_info.card_number  # 370000000000002
    creditCard.expirationDate = payment_info.expiration_date  # 2035-12
    creditCard.cardCode = payment_info.card_code  # 123

    # Add the payment data to a paymentType object
    payment = apicontractsv1.paymentType()
    payment.creditCard = creditCard

    # Create order information
    order = apicontractsv1.orderType()
    order.invoiceNumber = str(payment_info.order_id)
    order.description = "User Order"

    # Set the customer's Bill To address
    customerAddress = apicontractsv1.customerAddressType()
    customerAddress.firstName = customer_info.first_name
    customerAddress.lastName = customer_info.last_name
    customerAddress.company = ""
    customerAddress.address = customer_info.address
    customerAddress.city = ""
    customerAddress.state = ""
    customerAddress.zip = ""
    customerAddress.country = ""

    # Set the customer's identifying information
    customerData = apicontractsv1.customerDataType()
    customerData.type = "individual"
    customerData.id = str(customer_info.id)
    customerData.email = customer_info.email
    
    # Add values for transaction settings
    duplicateWindowSetting = apicontractsv1.settingType()
    duplicateWindowSetting.settingName = "duplicateWindow"
    duplicateWindowSetting.settingValue = "600"
    settings = apicontractsv1.ArrayOfSetting()
    settings.setting.append(duplicateWindowSetting)

    # build the array of line items
    line_items = apicontractsv1.ArrayOfLineItem()
    # setup individual line items
    for order_detail in order_info.order_details:
        line_item_1 = apicontractsv1.lineItemType()
        line_item_1.itemId = str(order_detail.product_id)
        line_item_1.name = order_detail.product_name
        line_item_1.description = ""
        line_item_1.quantity = str(order_detail.quantity)
        line_item_1.unitPrice = str(order_detail.unit_price)
        line_items.lineItem.append(line_item_1)

    # line_item_2 = apicontractsv1.lineItemType()
    # line_item_2.itemId = "67890"
    # line_item_2.name = "second"
    # line_item_2.description = "Here's the second line item"
    # line_item_2.quantity = "3"
    # line_item_2.unitPrice = "7.95"

    # build the array of line items
    # line_items = apicontractsv1.ArrayOfLineItem()
    # line_items.lineItem.append(line_item_1)
    # line_items.lineItem.append(line_item_2)

    # Create a transactionRequestType object and add the previous objects to it.
    transactionrequest = apicontractsv1.transactionRequestType()
    transactionrequest.transactionType = "authCaptureTransaction"
    transactionrequest.amount = payment_info.amount
    transactionrequest.payment = payment
    transactionrequest.order = order
    transactionrequest.billTo = customerAddress
    transactionrequest.customer = customerData
    transactionrequest.transactionSettings = settings
    transactionrequest.lineItems = line_items

    # Create the payment transaction request
    # transactionrequest = apicontractsv1.transactionRequestType()
    # transactionrequest.transactionType = "authCaptureTransaction"
    # transactionrequest.amount = payment_info.amount
    # transactionrequest.payment = payment

    # Assemble the complete transaction request
    createtransactionrequest = apicontractsv1.createTransactionRequest()
    createtransactionrequest.merchantAuthentication = merchantAuth
    # createtransactionrequest.refId = "MerchantID-0001"
    createtransactionrequest.transactionRequest = transactionrequest

    # Create the controller
    controller = createTransactionController(createtransactionrequest)
    controller.execute()

    response = controller.getresponse()

    if response is not None:
        # Check to see if the API request was successfully received and acted upon
        if response.messages.resultCode == "Ok":
            # Since the API request was successful, look for a transaction response
            # and parse it to display the results of authorizing the card
            if hasattr(response.transactionResponse, "messages") is True:
                message = PaymentSuccessStatus()
                message.transaction_id = str(response.transactionResponse.transId)
                message.response_code = str(response.transactionResponse.responseCode) # type: ignore
                message.message_code = str(
                    response.transactionResponse.messages.message[0].code
                ) # type: ignore
                message.message = str(
                    response.transactionResponse.messages.message[0].description
                )

                return {"status": True, "message": message}
            else:
                message = PaymentFailure()
                message.message = "Failed Transaction"

                if hasattr(response.transactionResponse, "errors"):
                    message.is_error = True
                    message.error_code = response.transactionResponse.errors.error[
                        0
                    ].errorCode
                    message.error_message = response.transactionResponse.errors.error[
                        0
                    ].errorText

                return {"status": False, "message": message}
        # Or, print errors if the API request wasn't successful
        else:
            message = PaymentFailure()
            message.message = "Failed Transaction"
            message.is_error = True
            if hasattr(response, "transactionResponse") and hasattr(
                response.transactionResponse, "errors"
            ):
                message.error_code = str(
                    response.transactionResponse.errors.error[0].errorCode
                ) # type: ignore
                message.error_message = str(
                    response.transactionResponse.errors.error[0].errorText
                )
            else:
                message.error_code = str(response.messages.message[0]["code"].text) # type: ignore
                message.error_message = str(response.messages.message[0]["text"].text)

            return {"status": False, "message": message}
    else:
        raise HTTPException(status_code=400, detail="Transaction Failed")


@router.post("/pay1")
async def create(
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
    token: Annotated[TokenData, Depends(get_token)],
):
    # product = CreateProduct(
    #     name=name,
    #     price=price,
    #     stock_quantity=stock_quantity,
    #     category_id=category_id,
    #     brand_id=brand_id,
    #     created_by=token.userid,
    #     status=status
    # )

    # if file:
    #     product.image_name = f"{product.guid}_{file.filename}"

    # product_dict = product.dict()

    # message = {
    #     "request_id": product.guid,
    #     "operation": "create",
    #     "entity": "product",
    #     "data": product_dict,
    # }

    # try:
    #     obj = json.dumps(message, cls=CustomJSONEncoder).encode("utf-8")
    #     await producer.send(config.KAFKA_PRODUCT_TOPIC, value=obj)
    #     # await asyncio.sleep(10)
    # except Exception as e:
    #     return str(e)

    # consumer = await get_kafka_consumer()
    # try:
    #     status_message = await consume_response_from_kafka(consumer, product.guid)
    # finally:
    #     await consumer.stop()

    # if status_message:
    #     if file:
    #         await save_file(file, product.guid)
    #     return status_message

    status_message = {"message": "Created"}
    return status_message


app.include_router(router)
