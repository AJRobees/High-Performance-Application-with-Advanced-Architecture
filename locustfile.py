"""
Load testing configuration for the product management API.

This module defines Locust users, request tasks, and waiting intervals
to simulate concurrent API traffic and measure application performance.
"""
from locust import task,HttpUser,between
from fastapi import status

class LoadUser(HttpUser):
    """Simulate users retrieving products from the API."""
    wait_time = between(5,15)
    host = "http://127.0.0.1:8000"

    @task
    def load_get_products(self):
        """Request the product listing endpoint and record the response outcome."""
        with self.client.get("/api/products",catch_response=True) as response:
            if response.status_code == status.HTTP_200_OK:
                response.success()

            else:
                response.failure(f"Status code :{response.status_code},Body:{response.text}")
