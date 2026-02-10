from pydantic import BaseModel

class SoilHealthInput(BaseModel):
    N: float
    P: float
    K: float
    ph: float
