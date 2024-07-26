This is online mart APIs using Event-Driven Microservice Architecture. I have used following technologies to develop the project

- **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python.
- **Docker**: For containerizing the microservices, ensuring consistency across different environments.
- **DevContainers**: To provide a consistent development environment.
- **Docker Compose**: For orchestrating multi-container Docker applications.
- **PostgreSQL**: A powerful, open-source relational database system.
- **SQLModel**: For interacting with the PostgreSQL database using Python.
- **Kafka**: A distributed event streaming platform for building real-time data pipelines and streaming applications.

**Following are the microservices involved in the architecture**

**Authentication Microservice:**

>Manages authentication services, create and decode tokens for users and customers

**User Microservice:**

>Responsible for managing system user operations such as creating, updating, deleting, and reading user information. These users can perform system level activates

**Brand Microservice:**

>Use to manage Brand operations such as creating, updating, deleting, and reading brand information

**Category Microservice:**

>Manages all operations related to product categories, including creation, updates, and deletions.

**Product Microservice:**

>Handles product-related activities such as adding new products, updating existing ones, and managing product details. Facilitates seamless product management.

**Customer Microservice:**

>Manages customer data and operations including customer registration, updates and authentication. These customers can create order and make payments and see his orders

**Order Microservice:**

>Oversees order processing, including order creation and retrieve order using order id. Ensures efficient and accurate order management.

**Payment Microservice:**

>Handles all payment transactions and processes, including payment validation, authorization, and processing. Ensures secure and efficient payment handling.

**Notification Microservice:**

>Manages sending notifications to customers via email right after user made payment for his order.

**Inventory Microservice:**

>Update product quantity In product table using order data produced in Kafka. This service will consume data when user made payment

**DB-service Microservice:**

>Provides database services and management, ensuring data storage, retrieval, and consistency. This service subscribes to different topics produced by multiple microservices in the architecture, which want to update their data in the database.

>These topics are consumed by the db-service microservice, which performs the respective database operations and produces responses back to Kafka. These responses are then consumed by different services to know the status of the database operations they requested.

>This service is solely responsible for handling all database operations involved in the system. No other microservice directly accesses the database except for the db-service microservice

![Image description](/flow.png)

