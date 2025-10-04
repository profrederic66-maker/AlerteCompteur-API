# main.py
import io
import csv
import logging
from datetime import timedelta, datetime
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import models
import schemas
import security
import email_service
import config
import dependencies
from database import engine, get_db

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Création des tables
models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="AlerteCompteur API")

# =============================================================================
# --- Fonctions CRUD ---
# =============================================================================

# --- Utilisateurs ---
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Biens (Properties) ---
def get_property_by_id(db: Session, property_id: int):
    return db.query(models.Property).filter(models.Property.id == property_id).first()

def get_properties_by_owner(db: Session, owner_id: int):
    return db.query(models.Property).filter(models.Property.owner_id == owner_id).all()

def create_user_property(db: Session, property: schemas.PropertyCreate, owner_id: int):
    db_property = models.Property(**property.dict(), owner_id=owner_id)
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property

def update_user_property(db: Session, property_id: int, property_update: schemas.PropertyBase, owner_id: int):
    db_property = db.query(models.Property).filter(
        models.Property.id == property_id,
        models.Property.owner_id == owner_id
    ).first()
    if db_property:
        for var, value in vars(property_update).items():
            if value is not None:
                setattr(db_property, var, value)
        db.add(db_property)
        db.commit()
        db.refresh(db_property)
        return db_property
    return None

def delete_user_property(db: Session, property_id: int, owner_id: int):
    db_property = db.query(models.Property).filter(
        models.Property.id == property_id,
        models.Property.owner_id == owner_id
    ).first()
    if db_property:
        db.delete(db_property)
        db.commit()
        return db_property
    return None

# --- Alertes ---
def get_alerts_by_property(db: Session, property_id: int):
    return db.query(models.Alert).filter(
        models.Alert.property_id == property_id
    ).order_by(models.Alert.created_at.desc()).all()

def create_property_alert(db: Session, alert: schemas.AlertCreate):
    db_alert = models.Alert(**alert.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

# --- Consentements ---
def get_consents_by_property(db: Session, property_id: int):
    return db.query(models.Consent).filter(models.Consent.property_id == property_id).all()

def create_property_consent(db: Session, consent: schemas.ConsentCreate):
    db_consent = models.Consent(**consent.dict())
    db.add(db_consent)
    db.commit()
    db.refresh(db_consent)
    return db_consent

# --- Consommation ---
def get_consumption_by_property(db: Session, property_id: int, days: int = 30):
    date_limit = datetime.now() - timedelta(days=days)
    return db.query(models.ConsumptionData).filter(
        models.ConsumptionData.property_id == property_id,
        models.ConsumptionData.date >= date_limit
    ).order_by(models.ConsumptionData.date.desc()).all()

def create_consumption_data(db: Session, property_id: int, consumption: schemas.ConsumptionCreate):
    db_consumption = models.ConsumptionData(property_id=property_id, **consumption.dict())
    db.add(db_consumption)
    db.commit()
    db.refresh(db_consumption)
    return db_consumption

# =============================================================================
# --- Routes de l'API ---
# =============================================================================

@app.get("/api/", tags=["Général"])
def read_root():
    return {"message": "Bienvenue sur l'API AlerteCompteur"}

@app.post("/api/users/", response_model=schemas.User, tags=["Utilisateurs"])
def create_user_route(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = get_user_by_email(db, email=user.email)
        if db_user:
            raise HTTPException(status_code=400, detail="Email déjà enregistré")
        return create_user(db=db, user=user)
    except Exception as e:
        logger.error(f"Erreur création utilisateur: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/token", response_model=schemas.Token, tags=["Utilisateurs"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/users/me", response_model=schemas.User, tags=["Utilisateurs"])
def read_users_me(current_user: models.User = Depends(dependencies.get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "phone": current_user.phone,
        "company_name": current_user.company_name,
        "siret": current_user.siret,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }

@app.post("/api/properties/", response_model=schemas.Property, tags=["Biens"])
def create_property_route(
    property: schemas.PropertyCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    return create_user_property(db=db, property=property, owner_id=current_user.id)

@app.get("/api/properties/", response_model=List[schemas.Property], tags=["Biens"])
def read_properties_route(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    return get_properties_by_owner(db=db, owner_id=current_user.id)

@app.get("/api/properties/{property_id}", response_model=schemas.Property, tags=["Biens"])
def read_property_route(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    db_property = get_property_by_id(db, property_id=property_id)
    if not db_property or db_property.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Bien non trouvé")
    return db_property

@app.put("/api/properties/{property_id}", response_model=schemas.Property, tags=["Biens"])
def update_property_route(
    property_id: int,
    property_update: schemas.PropertyBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    db_property = update_user_property(db, property_id=property_id, property_update=property_update, owner_id=current_user.id)
    if db_property is None:
        raise HTTPException(status_code=404, detail="Bien non trouvé")
    return db_property

@app.delete("/api/properties/{property_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Biens"])
def delete_property_route(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    db_property = delete_user_property(db, property_id=property_id, owner_id=current_user.id)
    if db_property is None:
        raise HTTPException(status_code=404, detail="Bien non trouvé")
    return

@app.post("/api/properties/{property_id}/consumption", response_model=schemas.ConsumptionData, tags=["Consommation"])
def add_consumption_route(
    property_id: int,
    consumption: schemas.ConsumptionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    db_property = get_property_by_id(db, property_id=property_id)
    if not db_property or db_property.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Bien non trouvé")
    return create_consumption_data(db=db, property_id=property_id, consumption=consumption)

@app.get("/api/properties/{property_id}/consumption", response_model=List[schemas.ConsumptionData], tags=["Consommation"])
def get_consumption_route(
    property_id: int,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    db_property = get_property_by_id(db, property_id=property_id)
    if not db_property or db_property.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Bien non trouvé")
    return get_consumption_by_property(db=db, property_id=property_id, days=days)

@app.get("/api/properties/{property_id}/alerts", response_model=List[schemas.Alert], tags=["Alertes"])
def get_alerts_route(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    db_property = get_property_by_id(db, property_id=property_id)
    if not db_property or db_property.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Bien non trouvé")
    return get_alerts_by_property(db=db, property_id=property_id)

@app.post("/api/alerts/", response_model=schemas.Alert, tags=["Alertes"])
def create_alert_route(
    alert: schemas.AlertCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    db_property = get_property_by_id(db, property_id=alert.property_id)
    if not db_property or db_property.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Bien non trouvé")
    return create_property_alert(db=db, alert=alert)

@app.get("/api/properties/{property_id}/consents/", response_model=List[schemas.Consent], tags=["Consentements"])
def get_consents_route(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    db_property = get_property_by_id(db, property_id=property_id)
    if not db_property or db_property.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Bien non trouvé")
    return get_consents_by_property(db=db, property_id=property_id)

@app.post("/api/consents/", response_model=schemas.Consent, tags=["Consentements"])
def create_consent_route(
    consent: schemas.ConsentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    db_property = get_property_by_id(db, property_id=consent.property_id)
    if not db_property or db_property.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Bien non trouvé")
    return create_property_consent(db=db, consent=consent)

# =============================================================================
# --- Fichiers Statiques ---
# =============================================================================

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")