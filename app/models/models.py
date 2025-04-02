from dataclasses import dataclass


@dataclass
class Dealership:
    dealership_id: str
    inventory_source_id: str
    dealership_name: str
    url: str
    category: str


@dataclass
class Vehicle:
    inventory_source_id: str
    listing_url: str
    status: str
    price: float
    vehicle_data: dict