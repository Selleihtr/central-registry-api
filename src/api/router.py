import fastapi
import sqlalchemy
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db



router = fastapi.APIRouter(prefix="/api", tags=["messages"])

@router.get("/health")
def get_health(db: Session = fastapi.Depends(get_db)):
    try:
        # Проверяем подключение к БД
        db.execute(sqlalchemy.text("SELECT 1")).scalar()
        return JSONResponse(
            content={
                "status": "OK",
            },
            status_code=200
        )
    except Exception:
        return JSONResponse(
            content={
                "status": "INTERNAL SERVER ERROR",
            },
            status_code=500
        )
