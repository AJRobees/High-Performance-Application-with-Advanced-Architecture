"""
Pydantic schemas for product data validation and API responses.

This module defines the request, update, response, and pagination schemas
used by the product management endpoints.
"""
from datetime import datetime
from pydantic import Field,ConfigDict,BaseModel

class ProductBase(BaseModel):
    """Define the common fields and validation rules for product data."""
    product : str = Field(min_length=1,max_length=100)
    price : int = Field(gt=0)
    stock : int  = Field(ge=0)

class ProductCreate(ProductBase):
    """Validate the data required to create a new product."""
    pass

class ProductUpdate(BaseModel):
    """Validate the optional fields used to update an existing product."""
    product : str | None = Field(default=None, min_length=1,max_length=100)
    price : int | None = Field(default=None, gt=0)
    stock : int | None  = Field(default=None, ge=0)
    stocked_date : datetime | None = Field(default= None)

class ProductResponse(ProductBase):
    """Define the product data returned by the API."""
    model_config =ConfigDict(from_attributes=True)

    product_id : int
    stocked_date : datetime

class PaginatedProductResponse(BaseModel):
    """Represent a paginated collection of products and its metadata."""
    products : list[ProductResponse]
    skip : int
    limit : int
    total : int
    has_more : bool