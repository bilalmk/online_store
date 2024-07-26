*Customer Microservice:**

The customer microservice is responsible for managing customer operations, including creating, updating and reading current logged in customer information, as well as authenticating customer. These users are authorized personnel who can update or view its information.

This microservice publishes data to a Kafka topic to initiate customer-related operations (create, update, delete) in the system.

The db-service microservice consumes this data and performs the necessary database operations. After completing the requested operations, the db-service produces an operation status message to Kafka. The customer microservice then consumes this status message, extracts the status, and sends the response back to the relevant endpoints

**Endpoints:**

- **/customers/customer/ create**
  - Creates a new customer
  - Produces a create message to Kafka.
  - Consumes the response from Kafka after **db-service** processes the create request.
  - Returns the status message to the client.
- **/ customers/customer/authentication**
  - Authenticates a customer and generates a token
  - Call the api endpoint from **db-service microservice** to validate the credentials from database
  - Call the api endpoint from **authentication microservice** to generate token for authorize customer to allow him call other protected endpoints
- **/ user/update/{guid}**
  - This endpoint is protected and can only be accessed by authenticated customer
  - Checked user authorization via dependency injection
  - Validates the update request
  - Produces an update message to Kafka
  - Consumes the response from Kafka after **db-service** processes the update request
  - Returns the status message to the client.
- **/ me_users**
  - This endpoint is protected and can only be accessed by authenticated users
  - Checked user authorization via dependency injection
  - Calls get_customer, which call api **endpoint** from **db-service** to fetch the logged in customer information.
  - Returns the customer information