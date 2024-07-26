**Payment Microservice**

The payment service microservice is responsible for handling payment-related operations.

This includes creating and processing payments, updating payment statuses, and interacting with external payment gateways Authorize.Net.

The service also produces and consumes messages via Kafka to facilitate communication with other microservices such as the **db-service**, **notification** and **inventory** management services

This microservice will send the payment data to Kafka topic, Consumer in the service will consume the data from topic and call **db-service endpoint** to save the payment information in database

Also send the order data to Kafka topic which will be consumed by notification and inventory microservices to send the notification to user about the order confirmation and update the inventory

**Endpoints:**

- **/payments/pay**
  - This endpoint is protected and can only be accessed by authenticated customer
  - Processes the payment via Authorize.Net.
  - Updates payment status in the database, call **db-service** end point to perform database operation.
  - Produces payment and order information to Kafka topics for notification and inventory management.

**Key Functions**

- **make_payment**
  - **Description:**
    - Handles the entire payment process including validation, retrieving order and customer details, and communicating with Authorize.Net.
  - **Operations:**
    - Validates user ID and order details.
    - Retrieves customer and product details.
    - Creates and sends payment transaction request to Authorize.Net.
    - Parses the response and returns the payment status.
- **produce_create_payment**
  - **Description:**
    - Produces a Kafka message with payment information to be consumed by the payment service for recording in the database.
  - **Operations:**
    - Converts payment information to JSON and sends it to the Kafka payment topic.
- **produce_notification_and_inventory**
  - **Description:**
    - Produces a Kafka message with notification and order information for notification and inventory management services.
  - **Operations:**
    - Converts order and customer information to JSON and sends it to the Kafka notification topic.
- **consume_events_payment**
  - **Description:**
    - Consumes payment messages from a Kafka topic, send the information to db-service endpoint to update the database with the payment information.
  - **Operations:**
    - Continuously listens for messages on the Kafka topic and processes each message by calling **insert_payment**. **Insert_payment** will call endpoint in db-service to perform database operation
