from pydantic import BaseModel, Field

class IrrigationInput(BaseModel):
    soil_moisture: float
    temperature: float
    humidity: float
    rain_forecast: str = Field(..., example="no")
    crop_type: str = Field(..., example="Maize")
