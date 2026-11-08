# Architecture and Deployment Guide

## 1. Introduction

The High-Performance Application with Advanced Architecture is a Python-based backend application developed using FastAPI.

The application demonstrates backend development concepts, including REST API design, database management, caching, request validation, pagination, logging, concurrency-related techniques, and performance evaluation.

This document describes the application's architecture, its major components, the flow of requests, database and caching mechanisms, and the procedures required to set up and run the application.

## 2. System Architecture

The application follows a modular backend architecture in which different responsibilities are separated into individual modules.

### 2.1 Architecture Overview

The major components of the application are:

1. **API Layer:** Handles incoming HTTP requests and provides product management endpoints.
2. **Validation Layer:** Uses Pydantic schemas to validate incoming data and structure API responses.
3. **Business Logic Layer:** Handles product operations and coordinates database and caching interactions.
4. **Caching Layer:** Uses an in-memory TTL cache to store frequently requested data.
5. **Database Layer:** Uses SQLAlchemy to interact with the SQLite database.
6. **Logging Layer:** Provides application logging through Python's logging module.

### 2.2 Request Processing Flow

The general request processing flow is:

Client Request → FastAPI Endpoint → Request Validation → Application Logic → Cache / Database → Response

For product retrieval:

- The application receives a product retrieval request.
- FastAPI validates the request parameters.
- The application checks whether the requested information is available in the cache.
- If cached data is available, it can be returned without performing the corresponding database retrieval.
- If cached data is unavailable, the application retrieves the information through SQLAlchemy.
- The retrieved information is stored in the cache where applicable.
- The application returns the response to the client.

For product creation, modification, and deletion, the application performs the corresponding database operation and clears cached entries to prevent outdated information from being served.

## 3. Technology Stack

The following technologies are used in the application.

| Technology | Purpose |
|---|---|
| Python 3.12 | Primary programming language |
| FastAPI | REST API development |
| Uvicorn | ASGI server |
| SQLAlchemy | Database ORM and query management |
| SQLite | Database storage |
| Pydantic | Request validation and response schemas |
| cachetools | In-memory caching |
| threading.Lock | Synchronization of cache operations |
| pytest | Automated testing |
| HTTPX | API testing |
| pytest-cov | Test coverage measurement |
| Locust | Load testing |
| cProfile | Application profiling |

## 4. Application Components

### 4.1 API Module

The API module is implemented in `main.py`.

It provides endpoints for product management operations.

The supported operations include:

- Creating a product.
- Retrieving all products.
- Retrieving an individual product using its ID.
- Updating product information.
- Deleting a product.

The API uses HTTP methods such as GET, POST, PATCH, and DELETE.

FastAPI handles request processing and response generation.

### 4.2 Data Models

The `models.py` module defines the SQLAlchemy database model.

The application currently contains one primary model:

**Product**

| Field | Description |
|---|---|
| product_id | Unique product identifier |
| product | Product name |
| price | Product price |
| stock | Available stock quantity |
| stocked_date | Date and time associated with the product record |

The Product model represents the database structure used by the product management API.

### 4.3 Pydantic Schemas

The `schemas.py` module defines the data structures used for request validation and API responses.

The implemented schemas include:

- `ProductCreate`
- `ProductUpdate`
- `ProductResponse`
- `PaginatedProductResponse`

These schemas separate incoming request data from database model definitions.

They also help ensure that invalid data is rejected before the corresponding database operation is performed.

### 4.4 Database Module

The `database.py` module manages database connectivity and SQLAlchemy configuration.

The application uses SQLite as its development database.

**Database location:**

`data/products.db`

The database module provides:

- Database engine configuration.
- SQLAlchemy session management.
- Declarative model base configuration.
- Database session dependency for API requests.

Database sessions are managed through the application's dependency mechanism.

### 4.5 Configuration Module

The `config.py` module contains application configuration.

It provides a centralized location for configuration values used by the application.

### 4.6 Caching Module

The `cache.py` module implements the in-memory caching mechanism.

It uses `cachetools.TTLCache` with the following configuration:

| Property | Value |
|---|---|
| Cache type | TTLCache |
| Maximum entries | 1,000 |
| Expiration time | 30 seconds |
| Synchronization | threading.Lock |

The caching module provides four main operations:

- `get_cache()`
- `set_cache()`
- `delete_cache()`
- `clear_cache()`

Cache access operations are protected using a threading lock to coordinate concurrent access to the cache.

The cache supports product retrieval and paginated product listing.

Cache invalidation is performed after product write operations.

### 4.7 Logging Module

The application uses a shared logging module located at:

`configs/general_logger.py`

It provides a centralized logger configuration.

The logging module:

- Creates the logs directory when required.
- Configures loggers using Python's logging module.
- Uses the INFO logging level.
- Creates individual log files based on the logger source.
- Uses file handlers to record log messages.

This approach provides a consistent logging configuration across application modules.

## 5. Database Architecture

The application uses SQLite with SQLAlchemy.

SQLite stores product information in a local database file.

### Database Operations

The application supports the following database operations:

| Operation | Description |
|---|---|
| INSERT | Creates a new product record |
| SELECT | Retrieves product records |
| UPDATE | Modifies existing product information |
| DELETE | Removes a product record |
| COUNT | Retrieves the total number of product records |

### Pagination

The product listing endpoint supports pagination through two query parameters:

- `skip`: Specifies the number of records to skip.
- `limit`: Specifies the maximum number of records to retrieve.

The implemented configuration is:

| Parameter | Default | Minimum | Maximum |
|---|---:|---:|---:|
| skip | 0 | 0 | No fixed upper limit |
| limit | 10 | 1 | 50 |

The paginated response includes:

- `products`
- `skip`
- `limit`
- `total`
- `has_more`

This approach avoids returning the entire product collection in a single response.

## 6. Caching Architecture

Caching is used to reduce repeated database retrieval operations.

### Cache Key Strategy

The application uses different cache keys depending on the requested operation.

For paginated product listings, the cache key incorporates the pagination parameters.

Example:

- `product_0_10`
- `product_10_10`

Individual product retrieval uses a product-specific cache key.

### Cache Expiration

Each cached entry has a time-to-live of 30 seconds.

Expired entries are no longer considered valid cache entries.

### Cache Invalidation

Whenever a product is created, updated, or deleted, the application clears the cache.

This prevents previously cached product information from being returned after database modifications.

### Current Limitation

The cache is stored in application memory.

It is not a distributed cache and is not shared between separate application processes or server instances.

## 7. Application Execution Flow

The application follows these general execution stages:

1. Uvicorn starts the FastAPI application.
2. FastAPI initializes the application and its configured dependencies.
3. The application receives incoming HTTP requests.
4. Request data is validated using Pydantic schemas.
5. The relevant endpoint executes the requested operation.
6. The application interacts with the cache and database as required.
7. The resulting data is returned as an HTTP response.

Invalid requests are handled through FastAPI's request validation mechanism.

## 8. Project Testing Architecture

The application uses pytest and HTTPX for automated testing.

The testing structure separates application testing from the production database configuration.

### Database Testing

The product API tests use an in-memory SQLite database.

The test configuration includes:

- A separate testing database engine.
- `StaticPool` for maintaining the in-memory database connection.
- `check_same_thread=False` for the SQLite test configuration.
- A separate SQLAlchemy session factory.
- FastAPI dependency overrides for database access.
- Table creation and cleanup during testing.

This prevents automated tests from depending on the application's regular development database.

### Test Coverage Areas

The implemented tests cover:

- Product creation.
- Product retrieval.
- Product modification.
- Product deletion.
- Request validation.
- Pagination.
- Cache storage and retrieval.
- Cache deletion and clearing.

## 9. Development Environment Setup

The following steps describe how to prepare the application for local development.

### Prerequisites

Install the following:

- Python 3.12
- pip
- A code editor such as Visual Studio Code
- Git (optional, for version control)

### Step 1: Obtain the Project

Open the project directory in a terminal or code editor.

### Step 2: Create a Virtual Environment

Create a Python virtual environment to isolate project dependencies from other Python installations.

### Step 3: Activate the Virtual Environment

Activate the environment using the appropriate command for your operating system.

### Step 4: Install Dependencies

Install the packages required by the application.

These include FastAPI, Uvicorn, SQLAlchemy, Pydantic, cachetools, pytest, HTTPX, pytest-cov, and Locust.

### Step 5: Verify the Database Configuration

Check the database configuration and ensure that the application can access its SQLite database.

The development database is located at:

`data/products.db`

### Step 6: Start the Application

Run the FastAPI application through Uvicorn.

Development command:

`uvicorn main:app --reload`

The reload option automatically restarts the application when relevant source files change.

## 10. Accessing the API

After successfully starting the application, access the following interfaces.

| Interface | URL |
|---|---|
| API Base URL | http://127.0.0.1:8000 |
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |

Swagger UI provides an interactive interface for manually testing the implemented API endpoints.

Users can submit requests, inspect responses, and examine request validation behaviour.

## 11. Deployment Considerations

The current application is developed and tested in a local environment.

The following considerations are relevant before deploying it to a production environment.

### Database

SQLite is currently used for development.

A migration to PostgreSQL may be considered when the application requires more advanced database capabilities and concurrent database workloads.

### Caching

The current caching mechanism is local to the application process.

A distributed caching solution could be considered if the application is deployed across multiple processes or server instances.

### Server Configuration

Uvicorn is used to run the FastAPI application.

For production deployment, server configuration should account for process management, resource allocation, restart behaviour, and application availability.

### Security

Before production deployment, additional security measures should be evaluated, including:

- Authentication and authorization.
- Secure configuration and secret management.
- HTTPS.
- Input and access control.
- Database backup and recovery.
- Appropriate error handling.

### Monitoring

Application logging and performance profiling provide development-level observability.

Additional production monitoring would be required to track application health, resource usage, errors, and performance over time.

## 12. Current Implementation Limitations

The current implementation has the following limitations:

1. The application uses SQLite rather than a production database such as PostgreSQL.
2. Only the Product database model is implemented.
3. The cache is stored in local application memory.
4. Cache invalidation clears all entries instead of selectively invalidating related entries.
5. No distributed caching mechanism is implemented.
6. No containerization or Docker deployment configuration is included.
7. No production deployment environment has been configured.
8. Production authentication, authorization, and HTTPS configuration are not implemented.
9. Production monitoring and centralized log aggregation are not implemented.

These limitations describe the current scope of the project and identify possible areas for future development.

## 13. Conclusion

The High-Performance Application demonstrates a modular backend architecture using FastAPI, SQLAlchemy, SQLite, Pydantic, and in-memory caching.

The application separates API handling, database operations, request validation, caching, configuration, and logging into dedicated components.

Pagination and caching provide basic performance-oriented mechanisms, while automated testing, load testing, and profiling support application evaluation.

The current implementation provides a foundation for understanding backend architecture and performance optimization. Further development could extend the application with PostgreSQL, distributed caching, production security, and deployment infrastructure.