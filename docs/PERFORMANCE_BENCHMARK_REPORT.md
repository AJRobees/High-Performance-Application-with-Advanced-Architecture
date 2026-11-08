# Performance and Benchmark Report

## 1. Overview

This report documents the performance evaluation of the High-Performance Application with Advanced Architecture project.

The application uses FastAPI, SQLAlchemy, SQLite, and an in-memory caching mechanism to improve API responsiveness and reduce unnecessary database queries.

Performance evaluation focuses on API response times, request handling, database query execution, caching behaviour, and application profiling.

## 2. Testing Environment

| Component | Technology |
|---|---|
| Programming Language | Python 3.12 |
| Backend Framework | FastAPI |
| ASGI Server | Uvicorn |
| Database | SQLite |
| ORM | SQLAlchemy |
| Caching | cachetools TTLCache |
| Concurrency Control | threading.Lock |
| API Testing | pytest, HTTPX |
| Load Testing | Locust 2.47.0 |
| Profiling | cProfile |

The load tests were performed against the locally running application at `http://127.0.0.1:8000`.

## 3. API Load Testing

Locust was used to evaluate the application's response behaviour under simulated user requests.

The primary endpoint tested was:

- `GET /api/products` – Retrieves a paginated list of products.

### Recorded Benchmark Results

A successful load-testing run produced the following results:

| Metric | Result |
|---|---:|
| Simulated Users | 30 |
| User Spawn Rate | 1 user/second |
| Total Requests | 509 |
| Failed Requests | 0 |
| Average Response Time | 8.09 ms |
| Median Response Time | 8 ms |
| 95th Percentile (P95) | 11 ms |
| 99th Percentile (P99) | 20 ms |
| Minimum Response Time | 3 ms |
| Maximum Response Time | 111 ms |
| Average Response Size | 1,176 bytes |
| Current Requests per Second | 3.3 |

### Observations

- All 509 recorded requests completed without reported failures.
- The median response time was 8 ms.
- Most requests completed within 11 ms, according to the P95 measurement.
- The maximum recorded response time was 111 ms.
- The results indicate responsive behaviour during this particular local test run.

These measurements represent the recorded test environment and workload. They should not be interpreted as guaranteed production performance or as evidence of performance under substantially higher traffic.

## 4. Database Performance Analysis

SQLite and SQLAlchemy were used for database operations.

Several database query behaviours were examined using SQLite's `EXPLAIN QUERY PLAN`.

### Query Analysis

| Operation | Observed Behaviour |
|---|---|
| Product lookup by ID | Uses INTEGER PRIMARY KEY lookup |
| Paginated retrieval | Retrieves records using ORDER BY, LIMIT and OFFSET |
| Total product count | Uses a table scan |
| Database sessions | Uses per-request database sessions |

### Observations

- Product ID lookups benefit from SQLite's INTEGER PRIMARY KEY lookup.
- Pagination limits the number of records retrieved in a single request.
- The total product count operation performs a table scan.
- Database operations use SQLAlchemy sessions to manage database interactions.

The query analysis confirmed the execution strategies used by SQLite. No comparative database benchmark was conducted to establish a quantified improvement.

## 5. Caching Performance Optimization

An in-memory caching mechanism was implemented using `cachetools.TTLCache`.

### Cache Configuration

| Property | Configuration |
|---|---|
| Cache Type | TTLCache |
| Maximum Capacity | 1,000 entries |
| Time to Live | 30 seconds |
| Thread Safety | threading.Lock |
| Cache Storage | Application memory |

### Cached Operations

The application supports caching for:

- Paginated product listings.
- Individual product retrieval by ID.

Cache keys are generated using the requested pagination parameters or product ID.

### Cache Management

The caching module provides the following operations:

- `get_cache()` – Retrieves an existing cached value.
- `set_cache()` – Stores a value in the cache.
- `delete_cache()` – Removes a specific cache entry.
- `clear_cache()` – Clears the cache.

The cache is cleared after product creation, modification, and deletion to prevent outdated product information from being served.

### Cache Testing

The caching module was tested independently.

The following behaviours were verified:

- Storing and retrieving cached values.
- Retrieving values using the appropriate cache keys.
- Removing individual cache entries.
- Clearing all cached entries.

All implemented cache tests passed.

**Limitation:** The cache implementation has been functionally tested, but a separate before-and-after load benchmark has not been completed. Therefore, a specific percentage of response-time improvement cannot be claimed.

## 6. Application Profiling

Python's `cProfile` was used to examine the execution behaviour of the application during automated testing.

### Recorded Profiling Results

| Metric | Result |
|---|---:|
| Tests Executed | 6 |
| Tests Passed | 6 |
| Pytest Execution Time | 0.95 seconds |
| Total Profiling Time | 1.373 seconds |
| Function Calls | Approximately 1.37 million |
| `get_products()` Cumulative Time | Approximately 0.036 seconds |
| `get_products()` Calls | 5 |

### Observations

- All six tests passed during the profiling run.
- The `get_products()` function recorded approximately 0.036 seconds of cumulative execution time across five calls.
- Profiling included test execution, framework operations, and startup overhead.

These measurements represent the complete profiled test process rather than isolated API response times.

## 7. Testing and Reliability

Automated tests were implemented using pytest and HTTPX.

The tests cover product management operations, request validation, and caching behaviour.

The product API testing includes:

- Product creation.
- Product retrieval.
- Product updates.
- Product deletion.
- Pagination behaviour.
- Invalid request handling.
- Validation of product fields.

The caching tests cover storing, retrieving, deleting, and clearing cached values.

The recorded profiling run confirmed that six product-related tests passed. Cache tests were also executed successfully.

## 8. Performance Optimization Summary

The following performance-related mechanisms have been implemented:

| Optimization | Implementation |
|---|---|
| Paginated data retrieval | LIMIT and OFFSET |
| Product lookup | Primary key lookup |
| In-memory caching | TTLCache |
| Cache expiration | 30-second TTL |
| Cache capacity management | Maximum 1,000 entries |
| Thread safety | threading.Lock |
| Cache invalidation | Clears cache after write operations |
| Database connection management | Per-request SQLAlchemy sessions |
| Performance analysis | cProfile and Locust |

These mechanisms provide the application with basic performance optimization and analysis capabilities.

## 9. Limitations

The following limitations apply to the current implementation and testing:

1. SQLite is used as the development database; PostgreSQL integration has not been implemented.
2. The cache is stored in application memory and is not shared across multiple application processes.
3. The cache uses a fixed expiration time of 30 seconds.
4. Cache invalidation clears all entries after write operations rather than selectively invalidating related entries.
5. The Locust benchmark represents a local test environment and does not establish production scalability.
6. No separate benchmark has quantified the performance improvement introduced by caching.
7. Profiling measurements include test framework and application startup overhead.

## 10. Conclusion

The High-Performance Application implements several performance-oriented techniques, including paginated database retrieval, primary-key lookups, in-memory caching, thread-safe cache access, and automated testing.

The recorded Locust benchmark completed 509 requests with zero reported failures, achieving an average response time of 8.09 ms in the tested local environment.

Database query analysis and application profiling provided additional insight into the application's execution behaviour.

The caching module passed its functional tests, although its actual performance improvement has not yet been quantified through comparative benchmarking.

Overall, the project demonstrates the implementation and evaluation of fundamental backend performance optimization techniques using Python and FastAPI.