**Category Microservice:**

The Category Microservice is responsible for managing category operations, including creating, updating, deleting, and reading category information. This microservice interacts with Kafka for asynchronous communication and with external services for authentication and data retrieval. It ensures that only authenticated system users can perform operations on category.

**Endpoints:**

- **/categories/create**
  - This endpoint is protected and can only be accessed by authenticated users
  - Creates a new category
  - Produces a create message to Kafka.
  - This Kafka topic will be consumed by db-service, db-service process the create request and produce the status object to Kafka topic
  - The status response is consumed back by this microservice and returned to the caller.
- **/categories/update/{guid}**
  - This endpoint is protected and can only be accessed by authenticated users
  - Checked user authorization via dependency injection
  - Validates the update request
  - Produces an update message to Kafka topic
  - This Kafka topic will be consumed by db-service, db-service process the update request and produce the status object to Kafka topic
  - The status response is consumed back by category microservice
  - Returns the status message to the client.
- **/categories/delete/{guid}**
  - This endpoint is protected and can only be accessed by authenticated users
  - Checked user authorization via dependency injection
  - Validates the delete request
  - Produces a delete message to Kafka
  - This Kafka topic will be consumed by db-service, db-service process the update request and produce the status object to Kafka topic
  - The status response is consumed back by category microservice
  - Returns the status message to the client
- **/categories**
  - This endpoint is protected and can only be accessed by authenticated users
  - Checked user authorization via dependency injection
  - Calls get_category_list, which call api **endpoint** from **db-service** to fetch the category list.
  - Returns the list of categories.
- **/categories/category/{category_id}**
  - This endpoint is protected and can only be accessed by authenticated users
  - Checked user authorization via dependency injection
  - Calls get_category with category_id, which call api **endpoint** from **db-service** to fetch the category based on provided category id.
  - Returns the category object.