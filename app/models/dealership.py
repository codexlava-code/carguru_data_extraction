from pydantic import BaseModel, HttpUrl


class Dealership(BaseModel):
    dealership_id: str
    dealership_name: str
    url: HttpUrl
    inventory_source_id: str