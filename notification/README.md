**Notification Microservice:**

The Notification Microservice continuously listens to messages on a Kafka topic which were produced by payment service and sends email notifications to customers when an order is completed and payment is made successfully.

This microservice is integrated with an authentication service for token validation and communicates with the **db-service microservice** endpoints to update order statuses.

It uses FastAPI for handling HTTP requests and aiokafka for Kafka message consumption

**Key Functions**

- **send_email**
  - This function will send email notification to user with the order information**.**
- **update_order_notification_status**
  - this function will call db-service end point to update the notification_status in order table to set the flag that notification has been sent for this particular order