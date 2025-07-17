from enum import Enum
from datetime import datetime
from pydantic import BaseModel, EmailStr

class CategoryEnum(str, Enum):
    Energy = "Energy"
    Water = "Water"
    Waste = "Waste"

class MetricBase(BaseModel):
    name: str
    category: CategoryEnum
    value: float
    unit: str
    date: datetime

class MetricResponse(MetricBase):
    id: str

class SignupRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str