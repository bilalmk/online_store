**Authentication Microservice**

The microservices handle token generation and token data extraction, enabling user authorization for accessing multiple endpoints across different microservices.

**EndPoints**

- **/generate_token**
  - This endpoint creates a token for the user, which is used to authorize the user and allow access to multiple endpoints in different microservices.
- **/get_token_data**
  - This endpoint extracts and return user data from an existing token