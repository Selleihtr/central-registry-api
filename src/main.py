import uvicorn

from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.api import constants
from src.api.router import router
from src import database
from src import placeholder

def startup():
    database.create_tables()
    
    # Создаем тестовую транзакцию
    db = database.SessionLocal()
    try:
        signed_data = placeholder.create_first_transaction()
        placeholder.create_transaction_in_db(
            db=db,
            signed_api_data=signed_data,
            transaction_type=9,
            meta_data=None
        )
        db.commit()
    except Exception as e:
        print(f"Ошибка: {e}")
        db.rollback()
    finally:
        db.close()


def shutdown():
    database.engine.dispose()


app = FastAPI(
    on_startup=[startup],
    on_shutdown=[shutdown],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.exception_handler(404)
def not_found_handler(request: Request, exc):
    if request.url.path.startswith(("/docs", "/openapi")):
        return JSONResponse(
            content={"error": "Not found"},
            status_code=404
        )
    
    return JSONResponse(
        content={"error": constants.HTTP_DESCRIPTIONS[404]},
        status_code=404
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)