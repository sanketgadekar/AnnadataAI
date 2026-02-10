from typing import Optional
from pydantic import BaseModel, Field

class FertilizerInput(BaseModel):
    Temparature: Optional[float] = Field(None, alias="Temparature")
    Temperature: Optional[float] = Field(None, alias="Temperature")
    Humidity: Optional[float] = None
    Moisture: Optional[float] = None
    Nitrogen: Optional[float] = None
    Potassium: Optional[float] = None
    Phosphorous: Optional[float] = None
    Soil_Type: Optional[str] = Field(None, alias="Soil Type")
    Crop_Type: Optional[str] = Field(None, alias="Crop Type")

    class Config:
        allow_population_by_field_name = True
