**Order Microservice**

The Order Management Microservice is responsible for handling operations related to orders, including creating and retrieving orders. It also facilitates communication with other microservices using Kafka for asynchronous operations. The endpoints provided by this microservice ensure that orders are created, updated, and fetched efficiently while maintaining data integrity and consistency.

This microservice publishes data to a Kafka topic to initiate order-related operations. The db-service microservice consumes this data and performs the necessary database operations. After completing the requested operations, the db-service produces an operation status message to Kafka. The Order Management Microservice then consumes this status message, extracts the status, and sends the response back to the relevant endpoints.

**Endpoints:**

- **/orders/create**
  - Creates a new order.
  - Protected and can only be accessed by authenticated customers.
  - Produces a create message to Kafka.
  - Consumes the response from Kafka after db-service processes the create request.
  - Returns the status message to the client.
- **/orders/order/{order_id}**
  - Retrieves order information based on the provided order ID.
  - Protected and can only be accessed by authenticated customers.
  - Calls the get_order function, which call api **endpoint** from **db-service** to fetch the order details.
  - Returns the order data.