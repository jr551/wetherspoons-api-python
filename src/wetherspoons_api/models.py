"""Pydantic models for Wetherspoons API"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Union, Any, Dict


class Location(BaseModel):
    latitude: float
    longitude: float
    distance_tolerance: Optional[float] = None


class Country(BaseModel):
    name: str
    code: str


class Address(BaseModel):
    line1: Optional[str] = None
    line2: Optional[str] = None
    line3: Optional[str] = None
    town: Optional[str] = None
    county: Optional[str] = None
    postcode: Optional[str] = None
    country: Optional[Country] = None
    location: Optional[Location] = None


class HighLevelVenue(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    franchise: str
    id: int
    is_closed: bool = Field(alias="isClosed")
    name: str
    venue_ref: int = Field(alias="venueRef")
    address: Optional[Address] = None


class DetailedVenue(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    can_place_order: Optional[bool] = Field(default=None, alias="canPlaceOrder")
    franchise: str
    id: int
    is_closed: Optional[bool] = Field(default=None, alias="isClosed")
    name: str
    sales_areas: List[dict] = Field(default_factory=list, alias="salesAreas")
    venue_can_order: Optional[bool] = Field(default=None, alias="venueCanOrder")
    venue_ref: Union[str, int] = Field(alias="venueRef")
    address: Optional[Address] = None


class HighLevelMenu(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    can_order: bool = Field(alias="canOrder")
    franchise: str
    id: int
    name: str
    sales_area_id: int = Field(alias="salesAreaId")
    venue_ref: int = Field(alias="venueRef")


class Price(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    currency: str
    discount: int
    initial_value: int = Field(alias="initialValue")
    value: int


class PortionOption(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    label: str
    value: dict


class Options(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    portion: dict


class DetailedMenuProduct(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: int
    is_out_of_stock: bool = Field(alias="isOutOfStock")
    item_type: str = Field(alias="itemType")
    name: str
    description: str
    options: Options


class Drink(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str
    units: float
    product_id: int = Field(alias="productId")
    price: float  # Price in pence (can be float from API)
    ppu: float  # price per unit


class DetailedMenu(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    data: Dict
