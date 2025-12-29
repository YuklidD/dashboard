from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.session import Session as SessionModel

router = APIRouter()

@router.get("/")
def get_sessions(db: Session = Depends(get_db)):
    return db.query(SessionModel).all()
