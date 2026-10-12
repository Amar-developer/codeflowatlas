from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.users import router as user_router
from app.routers.protected import router as protect_router
from app.database import  Base, engine
from app import models



Base.metadata.create_all(bind=engine)




app = FastAPI(
    title= "Authentication Api"
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(protect_router)

@app.get("/")
def root():
    return{
        "message": "Authentication is running...."
    }


@app.get("/db-test")
def database_test():
    try:
        with engine.connect() as connection:
            return {
                "database": "connected"
            }
    except Exception as e:
        return {
            "database": "connection failed",
            "error": str(e)
        }