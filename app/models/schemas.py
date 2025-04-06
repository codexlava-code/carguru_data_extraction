from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl

class InventorySource(BaseModel):
    id: Optional[str]
    url: Optional[HttpUrl]
    category: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class Dealership(BaseModel):
    id: Optional[str]
    address_id: Optional[str]
    inventory_source_id: Optional[str]
    name: Optional[str]
    phone_number: Optional[str]
    email: Optional[str]
    general_manager: Optional[str]
    website: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    inventory_source: Optional[InventorySource]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class DealershipData(BaseModel):
    dealership_id: Optional[str]
    dealership_name: Optional[str]
    url: Optional[HttpUrl]
    inventory_source_id: Optional[str]
    category: Optional[str]

class DealershipDetails(BaseModel):
    title: Optional[str]
    link: Optional[HttpUrl]
    address: Optional[str]
    phone: Optional[str]
    hours_operation: Optional[str]
    logo: Optional[HttpUrl]


class Make(BaseModel):
    name: Optional[str]


class Model(BaseModel):
    name: Optional[str]
    year: Optional[str]
    trim: Optional[str]
    body_style: Optional[str]
    transmission: Optional[str]
    fuel_type: Optional[str]
    drivetrain: Optional[str]
    engine: Optional[str]
    make: Optional[Make]


class VehicleDetails(BaseModel):
    dealership_id: Optional[str]
    vin: Optional[str]
    mileage: Optional[int]
    stock_number: Optional[str]
    description: Optional[str] = ""
    exterior_color: Optional[str]
    interior_color: Optional[str]
    model: Optional[Model]


class VehicleData(BaseModel):
    inventory_source_id: Optional[str]
    listing_url: Optional[HttpUrl]
    status: str
    price: Optional[float]
    vehicle_data: Optional[VehicleDetails]