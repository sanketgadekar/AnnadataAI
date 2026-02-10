from typing import Optional
from pydantic import BaseModel

class YieldInput(BaseModel):
    Area: Optional[str] = "India"
    Item: Optional[str] = "Wheat"
    Year: Optional[int] = 2013
    average_rain_fall_mm_per_year: Optional[float] = 1100
    pesticides_tonnes: Optional[float] = 5.4
    avg_temp: Optional[float] = 24.5
