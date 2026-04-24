from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from app.database import get_db
from app.models import Listing, Order
from app.schemas import (
    ListingCreate,
    ListingResponse,
    OrderCreate,
    OrderResponse,
    MessageResponse,
)
from app.auth import get_current_user

router = APIRouter(prefix="/api/v1/market", tags=["marketplace"])


# --- Listings ---

@router.post("/listings", response_model=ListingResponse, status_code=status.HTTP_201_CREATED)
async def create_listing(
    listing_data: ListingCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new produce listing (protected)."""
    new_listing = Listing(
        seller_id=current_user["user_id"],
        title=listing_data.title,
        description=listing_data.description,
        crop_type=listing_data.crop_type,
        quantity_kg=listing_data.quantity_kg,
        price_per_kg=listing_data.price_per_kg,
        location=listing_data.location,
    )
    db.add(new_listing)
    await db.flush()
    await db.refresh(new_listing)
    return ListingResponse.model_validate(new_listing)


@router.get("/listings", response_model=List[ListingResponse])
async def get_listings(
    crop_type: Optional[str] = None,
    location: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get all active listings (public)."""
    query = select(Listing).where(Listing.is_active == True).order_by(desc(Listing.created_at))

    if crop_type:
        query = query.where(Listing.crop_type.ilike(f"%{crop_type}%"))
    if location:
        query = query.where(Listing.location.ilike(f"%{location}%"))

    result = await db.execute(query)
    listings = result.scalars().all()
    return [ListingResponse.model_validate(l) for l in listings]


@router.get("/listings/{listing_id}", response_model=ListingResponse)
async def get_listing(
    listing_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single listing by ID (public)."""
    result = await db.execute(select(Listing).where(Listing.id == listing_id))
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return ListingResponse.model_validate(listing)


@router.delete("/listings/{listing_id}", response_model=MessageResponse)
async def delete_listing(
    listing_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a listing (protected — owner only)."""
    result = await db.execute(select(Listing).where(Listing.id == listing_id))
    listing = result.scalar_one_or_none()

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    if str(listing.seller_id) != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this listing")

    listing.is_active = False
    await db.flush()
    return MessageResponse(message="Listing deleted successfully")


# --- Orders ---

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Place an order on a listing (protected)."""
    result = await db.execute(
        select(Listing).where(Listing.id == order_data.listing_id, Listing.is_active == True)
    )
    listing = result.scalar_one_or_none()

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found or inactive")

    if str(listing.seller_id) == current_user["user_id"]:
        raise HTTPException(status_code=400, detail="Cannot order your own listing")

    if order_data.quantity_kg > listing.quantity_kg:
        raise HTTPException(status_code=400, detail="Requested quantity exceeds available stock")

    total_price = order_data.quantity_kg * listing.price_per_kg

    new_order = Order(
        listing_id=order_data.listing_id,
        buyer_id=current_user["user_id"],
        seller_id=listing.seller_id,
        quantity_kg=order_data.quantity_kg,
        total_price=round(total_price, 2),
    )
    db.add(new_order)

    # Reduce available quantity
    listing.quantity_kg -= order_data.quantity_kg
    if listing.quantity_kg <= 0:
        listing.is_active = False

    await db.flush()
    await db.refresh(new_order)
    return OrderResponse.model_validate(new_order)


@router.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get orders for the current user (as buyer or seller)."""
    result = await db.execute(
        select(Order)
        .where(
            (Order.buyer_id == current_user["user_id"])
            | (Order.seller_id == current_user["user_id"])
        )
        .order_by(desc(Order.created_at))
    )
    orders = result.scalars().all()
    return [OrderResponse.model_validate(o) for o in orders]
