import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import database
from api.router import router



def startup():
    database.create_tables()


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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)