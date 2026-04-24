import uuid
from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Listing(Base):
    __tablename__ = "listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    crop_type = Column(String(100), nullable=False)
    quantity_kg = Column(Float, nullable=False)
    price_per_kg = Column(Float, nullable=False)
    location = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    orders = relationship("Order", back_populates="listing", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Listing(id={self.id}, title={self.title})>"


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id"), nullable=False)
    buyer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    seller_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    quantity_kg = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String(50), default="pending", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    listing = relationship("Listing", back_populates="orders")

    def __repr__(self):
        return f"<Order(id={self.id}, status={self.status})>"
