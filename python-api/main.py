# run with: `uvicorn api:app` or `uvicorn api:app [--reload]`
# hosts docs at localhost:8000/docs

import fastapi
import airtable
from routers.form import router as form_router
from routers.web import router as web_router
from fastapi.middleware.cors import CORSMiddleware


app = fastapi.FastAPI()

app.include_router(form_router, tags=["org & listings crud"])
app.include_router(web_router, tags=["for frontend"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.encoders import jsonable_encoder

# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request, exc: RequestValidationError):
#     validation_errors = exc.errors()
#     print(validation_errors)
#     return PlainTextResponse(
#         status_code=422,
#         content='\n'.join(error['msg'] for error in validation_errors),
#     )
# 
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    validation_errors = exc.errors()
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
        #content=jsonable_encoder({"detail": '\n'.join(error['msg'] for error in validation_errors), "body": "body"}),
    )
