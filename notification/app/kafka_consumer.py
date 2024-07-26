from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import smtplib
from aiokafka import AIOKafkaConsumer  # type: ignore
from app import config
from app.operations import update_order_notification_status
from shared.models.notification import CreateNotification

responses = {}

async def consume_events(topic, group_id):
    """
    This function consumes messages from a Kafka topic, processes the data, sends an
    email to the customer about the order confirmation, and 
    call update_order_notification_status() function from operations to
    updates the order notification status.
    """
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
            
            """ send email to the customer to notify about the order details """
            await send_email(data)
            
            """ call this function to update the order notification status"""
            await update_order_notification_status(
                data.get("order_information").get("order_id"), 1
            )
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
        pass