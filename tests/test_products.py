"""
Test suite for the product management API.

This module tests API endpoints for product creation, retrieval,
updating, deletion, and validation using an isolated in-memory
SQLite database.
"""
from sqlalchemy import create_engine,StaticPool
from sqlalchemy.orm import sessionmaker

from fastapi.testclient import TestClient
from fastapi import status

from main import app,cache
from database import get_db,Base

import pytest

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL,
                       connect_args={"check_same_thread":False},
                       poolclass=StaticPool)

TestingSessionLocal = sessionmaker(autoflush= False, autocommit= False, bind=engine)

def override_get_db():
    """Provide a database session connected to the test database."""
    with TestingSessionLocal() as db:
        yield db

@pytest.fixture
def client():
    """
    Configure the test environment and provide a FastAPI test client.

    Clears the cache, creates test database tables, overrides the
    database dependency, and cleans up the database and cache after
    each test.
    """
    cache.clear_cache()
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    cache.clear_cache()

def test_read_root(client):
    """Verify that the root endpoint returns the expected server message."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message":"Server starts"}


def test_get_products(client):
    """Verify product listing and successful product creation."""
    response = client.get("/api/products")
    assert response.status_code == status.HTTP_200_OK

    response = client.post("/api/products",json = {"product":"Mouse","price":20,"stock":5})
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["product"] == "Mouse"
    assert data["price"] == 20
    assert data["stock"] == 5
    assert "product_id" in data
    assert "stocked_date" in data

    response = client.get("/api/products")
    assert response.status_code == status.HTTP_200_OK

def test_add_product(client):
    """Verify product creation and rejection of invalid product data."""
    response = client.post("/api/products",json = {"product":"Television","price":0,"stock":-1})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT,response.text 
    response = client.get("/api/products")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["products"]  == []

    response = client.post("/api/products",json = {"product":"","price":80,"stock":15})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT,response.text 
    response = client.get("/api/products")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["products"]  == []

    response = client.post("/api/products",json = {"product":"Mouse","price":20,"stock":5})
    assert response.status_code == status.HTTP_201_CREATED,response.text 

    data = response.json()
    assert data["product"] == "Mouse"
    assert data["price"] == 20
    assert data["stock"] == 5
    assert "product_id" in data
    assert "stocked_date" in data

def test_read_product(client):
    """Verify product retrieval by ID and handling of missing products."""
    product_id = 9999
    response = client.get(f"/api/products/{product_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = client.post("/api/products",json = {"product":"Mouse","price":20,"stock":5})
    assert response.status_code == status.HTTP_201_CREATED,response.text 

    product = response.json()
    response = client.get(f"/api/products/{product["product_id"]}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["product_id"] == product["product_id"]
    assert data["product"] == "Mouse"
    assert data["price"] == 20
    assert data["stock"] == 5
    assert "stocked_date" in data

def test_update_product(client):
    """Verify product updates, partial updates, and invalid update rejection."""
    response = client.post("/api/products",json = {"product":""})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT,response.text 
    response = client.get("/api/products")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["products"]  == []

    response = client.post("/api/products",json = {"product":"Mouse","price":20,"stock":5})
    assert response.status_code == status.HTTP_201_CREATED,response.text 
    product = response.json()

    response = client.patch(f"/api/products/{product["product_id"]}",json = {"product":""})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT,response.text 

    response = client.patch(f"/api/products/{product["product_id"]}",json = {"price":0,"stock":-1})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT,response.text 
    
    response = client.patch(f"/api/products/{product["product_id"]}",json={"product":"Monitor","stock":10})
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["product_id"] == product["product_id"]
    assert data["product"] == "Monitor"
    assert data["price"] == 20
    assert data["stock"] == 10
    assert "stocked_date" in data

def test_delete_product(client):
    """Verify product deletion and handling of deleted or missing products."""
    response = client.post("/api/products",json = {"product":"Mouse","price":20,"stock":5})
    assert response.status_code == status.HTTP_201_CREATED,response.text 
    product1 = response.json()

    response = client.post("/api/products",json={"product":"Monitor","price":150,"stock":10})
    assert response.status_code == status.HTTP_201_CREATED,response.text
    product2 = response.json()

    response = client.delete(f"/api/products/{product1["product_id"]}")
    assert response.status_code == status.HTTP_204_NO_CONTENT,response.text
    response = client.delete(f"/api/products/{product1["product_id"]}")
    assert response.status_code == status.HTTP_404_NOT_FOUND,response.text

    response = client.get(f"/api/products/{product1["product_id"]}")
    assert response.status_code == status.HTTP_404_NOT_FOUND,response.text

    response = client.get(f"/api/products/{product2["product_id"]}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["product_id"] == product2["product_id"]
