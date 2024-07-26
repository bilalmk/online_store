**Product Microservice:**

The Product Microservice is responsible for managing product operations, including creating, updating, deleting, and reading product information. This microservice interacts with Kafka for asynchronous communication and with external services for authentication and data retrieval. It ensures that only authenticated system users can perform operations on product.

**Endpoints:**

- **/products/create**
  - This endpoint is protected and can only be accessed by authenticated users
  - Creates a new product
  - Produces a create message to Kafka.
  - This Kafka topic will be consumed by db-service, db-service process the create request and produce the status object to Kafka topic
  - The status response is consumed back by this microservice and returned to the caller.
- **/products/update/{guid}**
  - This endpoint is protected and can only be accessed by authenticated users
  - Checked user authorization via dependency injection
  - Validates the update request
  - Produces an update message to Kafka topic
  - This Kafka topic will be consumed by db-service, db-service process the update request and produce the status object to Kafka topic
  - The status response is consumed back by product microservice
  - Returns the status message to the client.
- **/products/delete/{guid}**
  - This endpoint is protected and can only be accessed by authenticated users
  - Checked user authorization via dependency injection
  - Validates the delete request
  - Produces a delete message to Kafka
  - This Kafka topic will be consumed by db-service, db-service process the update request and produce the status object to Kafka topic
  - The status response is consumed back by product microservice
  - Returns the status message to the client
- **/products**
  - This endpoint is protected and can only be accessed by authenticated users
  - Checked user authorization via dependency injection
  - Calls get_product_list, which call api **endpoint** from **db-service** to fetch the products list.
  - Returns the list of products.
- **/products/product/{product_id}**
  - This endpoint is protected and can only be accessed by authenticated users
  - Checked user authorization via dependency injection
  - Calls get_product with product_id, which call api **endpoint** from **db-service** to fetch the product based on provided product id.
  - Returns the product object.