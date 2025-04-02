from pydantic import BaseModel, HttpUrl


class Make(BaseModel):
    name: str


class Model(BaseModel):
    name: str
    year: str | None
    trim: str | None
    body_style: str | None
    transmission: str | None
    fuel_type: str | None
    drivetrain: str | None
    engine: str | None
    make: Make


class VehicleDetail(BaseModel):
    dealership_id: str
    vin: str | None
    mileage: int | None
    stock_number: str | None
    description: str | None = ""
    exterior_color: str | None
    interior_color: str | None
    model: Model


class Vehicle(BaseModel):
    inventory_source_id: str
    listing_url: HttpUrl
    status: str
    price: float | None
    vehicle_data: VehicleDetail