**User Microservice:**

The user microservice is responsible for managing system user operations, including creating, updating, deleting, and reading user information, as well as authenticating users. These users are authorized personnel who manage various service data such as categories, brands, and products, not the customers of the mart.

This microservice publishes data to a Kafka topic to initiate user-related operations (create, update, delete) in the system. The db-service microservice consumes this data and performs the necessary database operations. After completing the requested operations, the db-service produces an operation status message to Kafka. The user microservice then consumes this status message, extracts the status, and sends the response back to the relevant endpoints

**Endpoints:**

- **/ create**
  - Creates a new user
  - Produces a create message to Kafka.
  - Consumes the response from Kafka after **db-service** processes the create request.
  - Returns the status message to the client.
- **/ user/authentication**
  - Authenticates a user and generates a token
  - Call the api endpoint from **db-service microservice** to validate the credentials from database
  - Call the api endpoint from **authentication microservice** to generate token for authorize user to allow him call other protected endpoints
- **/ user/update/{guid}**
  - This endpoint is protected and can only be accessed by authenticated users
  - Checked user authorization via dependency injection
  - Validates the update request
  - Produces an update message to Kafka
  - Consumes the response from Kafka after **db-service** processes the update request
  - Returns the status message to the client.
- **/ delete_user**
  - This endpoint is protected and can only be accessed by authenticated users
  - Checked user authorization via dependency injection
  - Validates the update request
  - Produces an update message to Kafka
  - Consumes the response from Kafka after **db-service** processes the update request
  - Returns the status message to the client.
- **/ get_users**
  - This endpoint is protected and can only be accessed by authenticated users
  - Checked user authorization via dependency injection
  - Calls get_user_list, which call api **endpoint** from **db-service** to fetch the user list.
  - Returns the list of users.