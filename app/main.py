#!/usr/bin/env python3
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

from routers import auth, system, lircd2uinput

# for production: think about locking down the docs:
# app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app = FastAPI()

# mount the static ressources
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """This method redirects to the openapi page of this app"""
    return RedirectResponse(url="/docs")


# include the routes defined in other modules
app.include_router(auth.router)
app.include_router(system.router)
app.include_router(lircd2uinput.router)
