**db-service Microservice**

The Database Service Microservice is responsible for handling CRUD operations for various entities such as users, products, categories, brands, orders, payments, and customers. It integrates with Kafka for asynchronous message processing. The service is built using FastAPI for handling HTTP requests and SQLModel for ORM.

**Alembic:**

This Microservice uses Alembic for database migrations when this service is up it call the migration script and update the database schema

**Kafka Consumer:  
**It continuously listens to messages on a different Kafka topic produced by the different microservices for database operations, this consumer will get the message and send the data to the respective classes for db crud operations

**Operation Files:**

These are class files for each microservice. They receive an operation parameter and decide which operation (create, update, or delete) to perform. They create an instance of the respective CRUD class with a session object. This instance is then used to perform the actual database operations.

After a successful database operation, the CRUD class returns a status object. This status object is then used by the send_producer function asynchronously to send the response to a Kafka producer, which will be consumed by the respective microservice to know the status of the database operation they requested.

**Crud Files:**

These are CRUD class files for each microservice, used to perform database operations specific to that microservice. Each CRUD class contains four main functions: create, update, delete, and read, which interact with the database using SQLModel ORM.

**Router Files:**

These router files contain endpoints for each microservice, allowing them to read data from the database. While most write operations are performed through Kafka, read operations are handled using router endpoints in db-service microservice.