from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import asyncio
import smtplib
import sys
from aiokafka import AIOKafkaConsumer  # type: ignore
from app import config
from app.operations import update_order_notification_status
from shared.models.notification import CreateNotification

responses = {}


async def consume_response_from_kafka(consumer, request_id):
    message_count = 0
    while True:
        try:
            message = await asyncio.wait_for(consumer.getone(), timeout=5)

            response = json.loads(message.value.decode("utf-8"))
            status = response.get("status").get("status")

            message = "Operation failed"

            if response.get("request_id") == request_id:
                if status == "success":
                    message = "Category created successfully"
                elif status == "duplicate":
                    message = "Category already exists"
                elif status == "exist":
                    message = "Category already exists"
                elif status == "failed":
                    message = "Failed to create category"
                elif status == "not-found":
                    message = "Category not found"
                elif status == "success-update":
                    message = "Category update successfully"
                elif status == "failed-update":
                    message = "Failed to update category"
                elif status == "success-delete":
                    message = "Category deleted successfully"
                elif status == "failed-delete":
                    message = "Failed to delete category"

                return {"message": message}
        except asyncio.TimeoutError:
            return {"message": "No messages received."}
            break  # or continue, based on your use case


async def consume_events(topic, group_id):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=str(config.BOOTSTRAP_SERVER),
        group_id=group_id,
        auto_offset_reset="earliest",
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            # create user
            response = json.loads(message.value.decode("utf-8"))
            request_id = response.get("request_id")
            data = response.get("data")
            await send_email(data)
            await update_order_notification_status(
                data.get("order_information").get("order_id"), 1
            )
            # update_order()
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()


async def send_email(info: CreateNotification):

    client_info = info.get("client_information")
    order_info = info.get("order_information")
    order_details = order_info.get("order_details")

    order_id = order_info.get("guid")
    order_date = order_info.get("order_date")
    total_amount = order_info.get("total_amount")
    order_date = order_info.get("order_date")

    to = client_info.get("email")
    name = client_info.get("first_name") + " " + client_info.get("last_name")
    email = client_info.get("email")
    # message = client_info.message
    subject = "Payment Confirmation and Order Details"

    sender_email = "piaicms@gmail.com"
    # password = "piaicms*6187"  # Use your App Password here
    password = "dpco wzfj ujod tzmm"

    body = f"""
    Dear {name},

    Thank you for your purchase from Our Company! We are pleased to confirm that we have received your payment and your order is now being processed.

    **Order Summary:**
    - **Order Number:** {order_id}
    - **Order Date:** {order_date}
    - **Total Amount Paid:** ${total_amount}
    - **Order Date:** ${order_date}

    **Items Ordered:**
    """
    for item in order_details:
        body += f"""- **Product Name:** {item.get("product_name")}, 
        **Quantity:** {item.get("quantity")}, 
        **Price per Item:** ${item.get("unit_price")}, 
        **Total Price:** ${item.get("total_price")}\n"""

    # body += f"""
    # **Payment Details:**
    # - **Transaction ID:** {details.transaction_id}
    # - **Payment Method:** {details.payment_method}
    # - **Payment Date:** {details.payment_date}

    body += f"""
    Your order will be shipped to your address as soon as possible. We hope you are satisfied with your purchase. Should you have any questions or require further assistance, please do not hesitate to contact our customer support.

    Best regards,

    Bilal Muhammad Khan
    Customer Service Team
    ABC Corporate Limited
    """

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = to
    message["Subject"] = subject

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    try:
        # server = smtplib.SMTP('smtp.gmail.com', 587)
        # server.starttls()
        # server.login(sender_email, password)
        # server.sendmail(sender_email, to,  message.as_string())
        # server.quit()
        # Connect to Gmail's SMTP server
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, to, message.as_string())
    except Exception as e:
        print(str(e))
        sys.stdout.flush()
        pass
        # can log the error
        # raise HTTPException(status_code=500, detail=str(e))
