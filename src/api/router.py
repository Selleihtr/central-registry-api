import fastapi
import sqlalchemy

from src.api.schemas.signed_api_data import SignedApiData
from src.api import constants, exceptions, service
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
    try:
        result = service.outgoing_service(envelope=envelope, db=db)
        return JSONResponse(content=result, status_code=200)
    except exceptions.APIException as e:
        return JSONResponse(
            content={"error": e.message},
            status_code=e.status_code
        )
    except Exception:
        return JSONResponse(
            content={"error": constants.HTTP_DESCRIPTIONS[500]},
            status_code=500
        )
  

@router.post("/incoming")
def get_incoming_messages(
    envelope: SignedApiData,
    db: Session = fastapi.Depends(get_db)
):
    """
    Отправляет новые сообщения от Системы А в Систему Б.

    Запрос: конверт SignedApiData, где в поле Data находится TransactionsData с
    массивом транзакций, которые сохраняются.

    Тело ответа: конверт SignedApiData, где в поле Data находится TransactionsData с
    массивом транзакций-квитков.
    """
    try:
        result = service.incoming_service(envelope=envelope, db=db)
        return JSONResponse(content=result, status_code=200)
    except exceptions.APIException as e:
        return JSONResponse(
            content={"error": e.message},
            status_code=e.status_code
        )
    except Exception:
        return JSONResponse(
            content={"error": constants.HTTP_DESCRIPTIONS[500]},
            status_code=500
        )
    

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def catch_all(path: str):
    return JSONResponse(
        content=constants.HTTP_DESCRIPTIONS[404],
        status_code=404
    )