# run with: `uvicorn api:app` or `uvicorn api:app [--reload]`
# hosts docs at localhost:8000/docs

import fastapi
import airtable
from routers.form import router as form_router
from routers.web import router as web_router
from fastapi.middleware.cors import CORSMiddleware


app = fastapi.FastAPI()

app.include_router(form_router, tags=["org & listings management"])
app.include_router(web_router, tags=["Frontend"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
