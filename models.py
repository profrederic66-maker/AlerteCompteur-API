from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    company_name = Column(String(255), nullable=True)
    siret = Column(String(14), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    properties = relationship("Property", back_populates="owner", cascade="all, delete-orphan")

class Property(Base):
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    label = Column(String(100), nullable=False)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=True)
    postal_code = Column(String(10), nullable=True)
    pdl = Column(String(14), unique=True, nullable=False)
    status = Column(String(20), default="EMPTY")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    threshold_alert = Column(Float, default=2.0)
    enedis_token = Column(Text, nullable=True)
    enedis_refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = relationship("User", back_populates="properties")
    consumption_data = relationship("ConsumptionData", back_populates="property", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="property", cascade="all, delete-orphan")
    consents = relationship("Consent", back_populates="property", cascade="all, delete-orphan")

class ConsumptionData(Base):
    __tablename__ = "consumption_data"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    date = Column(Date, nullable=False)
    kwh = Column(Float, nullable=False)
    max_power = Column(Float, nullable=True)
    source = Column(String(20), default="MANUAL")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    property = relationship("Property", back_populates="consumption_data")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    level = Column(String(20), nullable=False)
    event_type = Column(String(50), nullable=False)
    consumption_detected = Column(Float, nullable=True)
    confidence_score = Column(Integer, nullable=True)
    message = Column(Text, nullable=True)
    status = Column(String(20), default="ACTIVE")
    treated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    treated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    property = relationship("Property", back_populates="alerts")

class Consent(Base):
    __tablename__ = "consents"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    holder_email = Column(String(255), nullable=False)
    holder_name = Column(String(100), nullable=True)
    status = Column(String(20), default="INVITED")
    permissions = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    property = relationship("Property", back_populates="consents")