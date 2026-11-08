"""
FastAPI application providing product management endpoints.

This module handles product creation, retrieval, updating, and deletion.
It also supports paginated product retrieval, in-memory caching, and
application logging.
"""

from fastapi import FastAPI,HTTPException,status,Depends,Query
from schemas import ProductCreate,ProductResponse,ProductUpdate,PaginatedProductResponse

from typing import Annotated

from sqlalchemy import select,func
from sqlalchemy.orm import Session

import models
from database import Base,engine,get_db

from configs import get_logger
from cache import MemoryCache

Base.metadata.create_all(bind=engine)

logger = get_logger("main_api")
cache = MemoryCache()
app = FastAPI()

@app.get("/")
def home():
    """Return the API's root message and log server availability."""
    logger.info("Server is started...")
    return {"message":"Server starts"}


@app.get("/api/products",response_model=PaginatedProductResponse)
def get_products(db:Annotated[Session,Depends(get_db)],
                 skip:Annotated[int,Query(ge=0)] = 0,
                 limit:Annotated[int,Query(ge=1,le=50)] = 10):
    """
    Retrieve products using pagination.

    Checks the in-memory cache before querying the database. If the requested
    page is not cached, retrieves the products, constructs the paginated
    response, and stores it in the cache.
    """
    cache_result = cache.get_cache(key=f"products_{skip}_{limit}")

    if cache_result is not None:
        logger.debug("Retreving a cache.")
        return cache_result
    
    result_count = db.execute(select(func.count()).select_from(models.Product))
    total = result_count.scalar() or 0
    
    result = db.execute(select(models.Product).order_by(models.Product.product_id)
                        .offset(skip).limit(limit))
    products = result.scalars().all()

    has_more = skip + len(products) < total

    paginated_products = PaginatedProductResponse(products= [ProductResponse.model_validate(product) for product in products],
                                    skip=skip, limit=limit, total=total,has_more=has_more)
    logger.info("Setting a cache and return retreived data.")
    cache.set_cache(key=f"products_{skip}_{limit}",value=paginated_products.model_dump(exclude_unset=True))
   
    return paginated_products

@app.post("/api/products",response_model=ProductResponse,status_code=status.HTTP_201_CREATED)
def add_product(product:ProductCreate,db:Annotated[Session,Depends(get_db)]):
    """
    Create and store a new product.

    Commits the new product to the database, refreshes its database-generated
    values, and clears the cache to prevent outdated product data.
    """
    new_product = models.Product(
        product=product.product,
        price=product.price,
        stock=product.stock,
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    cache.clear_cache()
    logger.info("New product is added.")
    return new_product

@app.get("/api/products/{product_id}",response_model=ProductResponse)
def read_product(product_id:int, db:Annotated[Session,Depends(get_db)]):
    """
    Retrieve a product by its ID.

    Checks the cache first and queries the database on a cache miss.
    Raises HTTP 404 when the requested product does not exist.
    """
    cache_result = cache.get_cache(key=f"product_{product_id}")
    if cache_result is not None:
        cache_data = (ProductResponse.model_validate(cache_result)).model_dump()
        logger.debug("Retreving a cache.")
        return cache_data
    
    result = db.execute(select(models.Product).where(models.Product.product_id == product_id ))
    product = result.scalars().first()

    if product:
        product_data = (ProductResponse.model_validate(product)).model_dump()
        logger.info("Setting a cache and return retreived product.")
        cache.set_cache(key=f"product_{product_id}",value=product_data)
        return product_data

    logger.error(f"Product not found! {status.HTTP_404_NOT_FOUND}")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Product not found!")

@app.patch("/api/products/{product_id}",response_model=ProductResponse)
def update_product(product_id:int, product_data:ProductUpdate, db:Annotated[Session,Depends(get_db)]):
    """
    Update an existing product using the supplied fields.

    Applies the provided changes, commits the updated record, and clears
    the cache to keep subsequent retrievals consistent with the database.
    """
    result = db.execute(select(models.Product).where(models.Product.product_id == product_id ))
    product = result.scalars().first()

    if not product:
        logger.error(f"Product not found! {status.HTTP_404_NOT_FOUND}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Product not found!")

    update_data = product_data.model_dump(exclude_unset=True)
    for field,value in update_data.items():
            setattr(product,field,value)

    db.commit()
    db.refresh(product)
    cache.clear_cache()
    logger.info(f"{product.product} has been updated.")

    return product

@app.delete("/api/products/{product_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id:int, db:Annotated[Session,Depends(get_db)]):
    """
    Delete an existing product by its ID.

    Commits the deletion to the database and clears cached product data.
    Raises HTTP 404 when the requested product does not exist.
    """
    result = db.execute(select(models.Product).where(models.Product.product_id == product_id ))
    product = result.scalars().first()
    
    if not product:
        logger.error(f"Product not found! {status.HTTP_404_NOT_FOUND}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Product not found!")

    db.delete(product)
    db.commit()
    cache.clear_cache()
    logger.info(f"{product.product} has been removed.")
