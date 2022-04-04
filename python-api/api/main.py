# run with: `uvicorn api:app` or `uvicorn api:app [--reload]`
# hosts docs at localhost:8000/docs

import fastapi
import airtable
from routers.form import router as form_router
from routers.web import router as web_router


app = fastapi.FastAPI()

app.include_router(form_router)
app.include_router(web_router)
