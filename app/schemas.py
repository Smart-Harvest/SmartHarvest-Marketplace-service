from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


# --- Listing Schemas ---

class ListingCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    crop_type: str = Field(..., min_length=1, max_length=100)
    quantity_kg: float = Field(..., gt=0)
    price_per_kg: float = Field(..., gt=0)
    location: Optional[str] = None


class ListingResponse(BaseModel):
    id: UUID
    seller_id: UUID
    title: str
    description: Optional[str] = None
    crop_type: str
    quantity_kg: float
    price_per_kg: float
    location: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# --- Order Schemas ---

class OrderCreate(BaseModel):
    listing_id: UUID
    quantity_kg: float = Field(..., gt=0)


class OrderResponse(BaseModel):
    id: UUID
    listing_id: UUID
    buyer_id: UUID
    seller_id: UUID
    quantity_kg: float
    total_price: float
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    message: str
