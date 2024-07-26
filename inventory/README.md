**Inventory Microservice**

The Inventory Management Microservice is designed to handle inventory updates. It continuously listens to messages on a Kafka topic produced by the payment service. It retrieves order information from the topic and produces inventory object data to another Kafka topic for database operations. This data is consumed by the **db_service**, which records the payment information in the database. The microservice is built using FastAPI for handling HTTP requests and aiohttp for asynchronous HTTP client operations.

**Key Functions**

- **produce_inventory_update**

Produces an inventory update message to Kafka for given order information which will be consumed by db-service