import uvicorn
from fastapi import FastAPI

from database.connection import conn, drop_database
from routers.users import user_router


app = FastAPI()
app.include_router(user_router, prefix="/user")


@app.on_event("startup")
def on_startup():
    conn()


@app.on_event("shutdown")
def shutdown():
    drop_database()


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
