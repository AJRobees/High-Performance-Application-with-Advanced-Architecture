# TESTING AND QUALITY ASSURANCE REPORT

## 1. Introduction

The High-Performance Application with Advanced Architecture project uses automated testing and validation techniques to evaluate the correctness, reliability, and behaviour of its backend components.

The application uses pytest and HTTPX for API testing, SQLite for isolated database testing, and dedicated test cases for validating the caching mechanism.

This report documents the testing environment, testing strategy, implemented test cases, validation procedures, and observed results.

## 2. Testing Environment

The following tools and technologies are used for testing:

| Component | Technology |
|---|---|
| Programming Language | Python 3.12 |
| API Framework | FastAPI |
| Testing Framework | pytest |
| HTTP Client | HTTPX |
| Database | SQLite |
| ORM | SQLAlchemy |
| Test Coverage | pytest-cov |
| Load Testing | Locust |
| Performance Profiling | cProfile |

## 3. Testing Strategy

The application uses different testing approaches to evaluate individual components and API behaviour.

### 3.1 API Testing

API testing verifies whether the product management endpoints behave as expected.

The tests cover:

- Product creation.
- Product retrieval.
- Product modification.
- Product deletion.
- Pagination.
- Request validation.
- Invalid input handling.

### 3.2 Database Testing

The product API tests use an in-memory SQLite database instead of the regular development database.

The testing configuration includes:

- A separate database engine.
- StaticPool for maintaining the in-memory database connection.
- A separate SQLAlchemy session factory.
- FastAPI dependency overrides.
- Database table creation and cleanup.

This approach isolates test operations from the application's regular development database.

### 3.3 Cache Testing

The caching module is tested independently to verify its basic operations.

The tests evaluate:

- Storing values in the cache.
- Retrieving stored values.
- Removing individual cache entries.
- Clearing all cached entries.

### 3.4 Performance and Load Testing

Locust is used to evaluate API response behaviour under simulated user requests.

Python's cProfile is used to examine function execution behaviour and identify areas that may require optimization.

These tools complement functional testing by evaluating application performance.

## 4. API Test Cases

The product management API is tested for successful operations and invalid requests.

### 4.1 Product Creation

The creation tests verify that valid product information can be submitted and stored.

The tests also verify that invalid input is rejected.

Example test scenarios:

| Test Scenario | Expected Result |
|---|---|
| Create a valid product | HTTP 201 |
| Submit an empty product name | HTTP 422 |
| Verify created product information | Correct product data |

### 4.2 Product Retrieval

The retrieval tests verify that product information can be accessed through the API.

The test scenarios include:

- Retrieving the product collection.
- Retrieving an individual product using its ID.
- Handling requests for unavailable product records.

### 4.3 Product Update

The update tests verify that existing product information can be modified without unintentionally changing unrelated fields.

The implemented test scenarios include:

| Test Scenario | Expected Result |
|---|---|
| Update with an empty product name | HTTP 422 |
| Update with price equal to zero | HTTP 422 |
| Update with negative stock | HTTP 422 |
| Update product name and stock with valid values | Successful update |
| Verify unchanged product ID | Original ID preserved |
| Verify unchanged price | Original price preserved |

A successful update test changes the product name to Monitor and stock quantity to 10 while retaining the original price of 20 and product ID.

### 4.4 Product Deletion

The deletion tests verify that product records can be removed using their identifiers.

The tests also check the API response when attempting to access a deleted or unavailable product.

## 5. Pagination Testing

Pagination is implemented in the product listing endpoint.

The tests verify the behaviour of the `skip` and `limit` query parameters.

The supported configuration is:

| Parameter | Default | Minimum | Maximum |
|---|---:|---:|---:|
| skip | 0 | 0 | No fixed upper limit |
| limit | 10 | 1 | 50 |

The paginated response contains:

- products
- skip
- limit
- total
- has_more

The following scenarios are used to evaluate pagination:

1. Retrieving the first page of products.
2. Retrieving subsequent pages.
3. Retrieving a page with a different limit.
4. Requesting an offset beyond the available records.
5. Validating pagination parameter boundaries.

These tests help ensure that pagination returns the expected product records and metadata.

## 6. Request Validation Testing

FastAPI and Pydantic handle request validation.

The application validates incoming product information before performing database operations.

Validation testing includes:

- Empty product names.
- Invalid product values.
- Zero or negative prices.
- Negative stock quantities.
- Invalid pagination parameters.
- Partial update requests.

Invalid requests are expected to return HTTP 422 responses where the configured validation rules are violated.

This helps prevent invalid data from being accepted through the API.

## 7. Cache Testing

The caching module uses `cachetools.TTLCache`.

The configured cache settings are:

| Property | Value |
|---|---|
| Cache Type | TTLCache |
| Maximum Capacity | 1,000 entries |
| Expiration Time | 30 seconds |
| Synchronization | threading.Lock |

### 7.1 Implemented Cache Test Scenarios

| Test Scenario | Expected Behaviour |
|---|---|
| Store a value | Value is added to the cache |
| Retrieve an existing key | Stored value is returned |
| Retrieve a deleted key | Returns None |
| Delete a cache entry | Specified entry is removed |
| Clear the cache | All entries are removed |

The cache tests successfully verified storing, retrieving, deleting, and clearing cached values.

### 7.2 Cache Testing Outcome

All implemented cache tests passed.

The tests confirm the basic functionality of the caching module.

The tests do not independently establish the performance improvement achieved by caching.

## 8. Load Testing

Locust was used to simulate multiple users making requests to the application.

The primary endpoint evaluated was:

`GET /api/products`

### 8.1 Recorded Load Test Results

| Metric | Result |
|---|---:|
| Simulated Users | 30 |
| User Spawn Rate | 1 user/second |
| Total Requests | 509 |
| Failed Requests | 0 |
| Average Response Time | 8.09 ms |
| Median Response Time | 8 ms |
| P95 Response Time | 11 ms |
| P99 Response Time | 20 ms |
| Minimum Response Time | 3 ms |
| Maximum Response Time | 111 ms |
| Average Response Size | 1,176 bytes |
| Current Requests per Second | 3.3 |

### 8.2 Observations

- All 509 recorded requests completed without reported failures.
- The average response time was 8.09 milliseconds.
- The median response time was 8 milliseconds.
- The P95 response time was 11 milliseconds.
- The maximum recorded response time was 111 milliseconds.

The results indicate responsive API behaviour during the recorded local load test.

These measurements apply to the tested environment and workload. They do not establish production scalability or guaranteed performance under higher traffic.

## 9. Application Profiling

Python's cProfile was used to examine the execution behaviour of the application during automated testing.

### 9.1 Recorded Profiling Results

| Metric | Result |
|---|---:|
| Tests Executed | 6 |
| Tests Passed | 6 |
| Pytest Execution Time | 0.95 seconds |
| Total Profiling Time | 1.373 seconds |
| Function Calls | Approximately 1.37 million |
| get_products() Cumulative Time | Approximately 0.036 seconds |
| get_products() Calls | 5 |

### 9.2 Observations

- All six tests passed during the profiling run.
- The `get_products()` function recorded approximately 0.036 seconds of cumulative execution time across five calls.
- The profiling results include application and testing framework execution overhead.

These measurements describe the profiled test process and should not be interpreted as isolated API response times.

## 10. Testing Results Summary

The following table summarizes the implemented testing areas and recorded outcomes.

| Testing Area | Result |
|---|---|
| Product API testing | Implemented |
| Product request validation | Implemented |
| Product update validation | Passed in recorded tests |
| Pagination | Implemented |
| Cache functionality | Passed |
| Database test isolation | Implemented |
| Locust load testing | 509 requests, 0 failures |
| Application profiling | Completed |

The recorded profiling run completed six tests successfully.

The cache tests were also executed successfully.

## 11. Limitations

The current testing implementation has the following limitations:

1. The testing database uses SQLite rather than PostgreSQL.
2. The recorded load test represents a local development environment.
3. Load testing has not established production-level scalability.
4. A comparative benchmark between cached and uncached requests has not been completed.
5. Cache expiration behaviour has not been included as a quantified performance benchmark.
6. Multi-process and distributed caching behaviour has not been tested.
7. Production deployment and infrastructure testing have not been performed.
8. The recorded profiling results cover a limited set of test executions.

These limitations identify areas that could be expanded in future testing activities.

## 12. Conclusion

The High-Performance Application includes automated API testing, database test isolation, request validation, cache testing, load testing, and application profiling.

The product API tests verify the behaviour of CRUD operations, pagination, and invalid request handling.

The caching tests confirm the basic functionality of the in-memory cache, while Locust provides measurements of API response behaviour under simulated user requests.

The recorded load test completed 509 requests with zero reported failures and an average response time of 8.09 milliseconds.

Overall, the testing activities provide a foundation for evaluating the correctness and performance characteristics of the application. Additional testing under different workloads and deployment environments would be required for a more comprehensive production-level assessment.