"""
SQLAlchemy database models for the application.

This module defines the database tables and their mapped attributes.
"""
from datetime import datetime,UTC

from sqlalchemy import String,DateTime
from sqlalchemy.orm import Mapped,mapped_column

from database import Base

class Product(Base):
    """Represent a product record stored in the products table."""
    __tablename__ = "products"
    product_id : Mapped[int] = mapped_column(primary_key=True,nullable=False)
    product : Mapped[str] = mapped_column(String(length=100),nullable=False,)
    price : Mapped[int] = mapped_column(nullable=False)
    stock : Mapped[int] = mapped_column(nullable=False)

    stocked_date : Mapped[datetime] = mapped_column(DateTime(),
                                                       default= lambda : datetime.now(UTC))
