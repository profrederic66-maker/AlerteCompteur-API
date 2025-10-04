from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date

# User Schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    phone: Optional[str] = None
    company_name: Optional[str] = None
    siret: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Property Schemas
class PropertyBase(BaseModel):
    label: str
    address: str
    city: Optional[str] = None
    postal_code: Optional[str] = None
    pdl: str
    status: str = "EMPTY"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    threshold_alert: float = 2.0

class PropertyCreate(PropertyBase):
    pass

class Property(PropertyBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Consumption Schemas
class ConsumptionBase(BaseModel):
    date: date
    kwh: float
    max_power: Optional[float] = None
    source: str = "MANUAL"

class ConsumptionCreate(ConsumptionBase):
    pass

class ConsumptionData(ConsumptionBase):
    id: int
    property_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Alert Schemas
class AlertBase(BaseModel):
    property_id: int
    level: str
    event_type: str
    consumption_detected: Optional[float] = None
    confidence_score: Optional[int] = None
    message: Optional[str] = None
    status: str = "ACTIVE"

class AlertCreate(AlertBase):
    pass

class Alert(AlertBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Consent Schemas
class ConsentBase(BaseModel):
    property_id: int
    holder_email: str
    holder_name: Optional[str] = None
    status: str = "INVITED"

class ConsentCreate(ConsentBase):
    pass

class Consent(ConsentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True