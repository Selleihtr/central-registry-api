import fastapi
import sqlalchemy

from src.api.schemas.signed_api_data import SignedApiData
from src.api import service
from src.database import get_db
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session




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


@router.post("/outgoing")
def get_outgoing_messages(
    envelope: SignedApiData,
    db: Session = fastapi.Depends(get_db)
):
    """
    Получение входящих сообщений

    Возвращает список транзакций с сообщениями, адресованными Системе А, за указанный период.

    """
    return JSONResponse(
        content=service.outgoing_service(
            envelope=envelope, 
            db=db,
        ),
        status_code=200
    )
  



@router.post("/incoming")
def get_ingoing_messages():
    
   pass


