**Brand Microservice:**

The Brand Microservice is responsible for managing brand operations, including creating, updating, deleting, and reading brand information. This microservice interacts with Kafka for asynchronous communication and with external services for authentication and data retrieval. It ensures that only authenticated system users can perform operations on brands.

**Endpoints:**

- **/brands/create**
  - This endpoint is protected and can only be accessed by authenticated users
  - Creates a new brand
  - Produces a create message to Kafka.
  - Consumes the response from Kafka after **db-service** processes the create request.
  - The response is consumed back by this microservice and returned to the caller.
- **/brands/update/{guid}**
  - This endpoint is protected and can only be accessed by authenticated users
  - Checked user authorization via dependency injection
  - Validates the update request
  - Produces an update message to Kafka topic
  - This Kafka topic will be consumed by db-service, db-service process the update request and produce the status object to Kafka topic
  - The status response is consumed back by brand microservice
  - Returns the status message to the client.
- **/brands/delete_user/{guid}**
  - This endpoint is protected and can only be accessed by authenticated users
  - Checked user authorization via dependency injection
  - Validates the update request
  - Produces an delete message to Kafka
  - This Kafka topic will be consumed by db-service, db-service process the update request and produce the status object to Kafka topic
  - The status response is consumed back by brand microservice
  - Returns the status message to the client
- **/brands**
  - This endpoint is protected and can only be accessed by authenticated users
  - Checked user authorization via dependency injection
  - Calls get_brand_list, which call api **endpoint** from **db-service** to fetch the brand list.
  - Returns the list of brands.
- **/brands/brand/{brand_id}**
  - This endpoint is protected and can only be accessed by authenticated users
  - Checked user authorization via dependency injection
  - Calls get_brand with brand_id, which call api **endpoint** from **db-service** to fetch the brand brand based on provided brand id.
  - Returns the brand object.