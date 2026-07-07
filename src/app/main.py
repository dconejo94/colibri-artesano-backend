import os

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.core.rate_limit import limiter
from app.core.exceptions import (
    AuthenticationException,
    ConflictException,
    ForbiddenException,
    InvalidImageUrlError,
    NotFoundException,
    ServiceUnavailableException,
    ValidationException,
)

from app.api.v1 import api_router

# Wire Azure Monitor / Application Insights when a connection string is present.
# Gating on the env var keeps local dev and tests free of telemetry exporters.
if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
    from azure.monitor.opentelemetry import configure_azure_monitor

    configure_azure_monitor()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Auto-capture request traces and latency once telemetry is configured.
if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    FastAPIInstrumentor.instrument_app(app)

# Wire slowapi: expose the limiter and return 429 when a limit is exceeded.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request: Request, exc: NotFoundException):
    return JSONResponse(status_code=404, content={"detail": exc.detail})


@app.exception_handler(ConflictException)
async def conflict_exception_handler(request: Request, exc: ConflictException):
    return JSONResponse(status_code=409, content={"detail": exc.detail})


@app.exception_handler(ForbiddenException)
async def forbidden_exception_handler(request: Request, exc: ForbiddenException):
    return JSONResponse(status_code=403, content={"detail": exc.detail})


@app.exception_handler(AuthenticationException)
async def authentication_exception_handler(
    request: Request, exc: AuthenticationException
):
    return JSONResponse(
        status_code=401,
        content={"detail": exc.detail},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    detail = [
        {"loc": ["body", field], "msg": msg} for field, msg in exc.field_errors.items()
    ]
    return JSONResponse(status_code=422, content={"detail": detail})


# Pydantic error "type" -> Spanish message, for FastAPI's automatic request
# body/query validation (as opposed to ValidationException, which services
# raise directly for business-rule validation).
_PYDANTIC_ERROR_MESSAGES = {
    "missing": "Este campo es obligatorio.",
    "string_type": "Debe ser una cadena de texto.",
    "int_type": "Debe ser un número entero.",
    "int_parsing": "Debe ser un número entero.",
    "float_type": "Debe ser un número.",
    "float_parsing": "Debe ser un número.",
    "bool_type": "Debe ser un valor booleano.",
    "bool_parsing": "Debe ser un valor booleano.",
    "uuid_parsing": "Debe ser un identificador válido.",
    "value_error": "Valor inválido.",
    "json_invalid": "El cuerpo de la solicitud no es un JSON válido.",
}


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    detail = [
        {
            "loc": list(error["loc"]),
            "msg": _PYDANTIC_ERROR_MESSAGES.get(error["type"], "Valor inválido."),
        }
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": detail})


@app.exception_handler(InvalidImageUrlError)
async def invalid_image_url_exception_handler(
    request: Request, exc: InvalidImageUrlError
):
    return JSONResponse(status_code=400, content={"detail": exc.detail})


@app.exception_handler(ServiceUnavailableException)
async def service_unavailable_exception_handler(
    request: Request, exc: ServiceUnavailableException
):
    return JSONResponse(status_code=503, content={"detail": exc.detail})


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "status": "ok",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
