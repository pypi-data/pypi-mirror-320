import logging
import os
import secrets

import colorlog
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import \
    OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (BatchSpanProcessor,
                                            ConsoleSpanExporter)
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from fastapi_booster.LifeSpanManager import lifespan

# set up logging
logger = logging.getLogger("FasterAPI-Booster")
stream_handler = logging.StreamHandler()

# Define log colors
cformat = "%(log_color)s%(levelname)-10s%(reset)s%(log_color)s%(message)s"
colors = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "red,bg_white",
}

stream_formatter = colorlog.ColoredFormatter(cformat, log_colors=colors)
stream_handler.setFormatter(stream_formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)


class Settings(BaseSettings):
    SERVICE_NAME: str = Field(default="FastAPI", description="The name of the service for OpenTelemetry")
    OTEL_ENDPOINT: str = Field(default="http://localhost:4317", description="The endpoint for the OpenTelemetry collector")
    AUTH_SQL_URL: str = Field(default="sqlite:///auth.db", description="The URL for the authentication database")
    ALLOW_SELF_SIGNUP: bool = Field(default=False, description="Whether to allow self-registration of users")
    JWT_SECRET_KEY: str = Field(default=secrets.token_urlsafe(32), description="The secret key for JWT")
    JWT_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="The expiration time for JWT in minutes")
    JWT_ALGORITHM: str = Field(default="HS256", description="The algorithm for JWT")
    OAUTH_SERVER_CONFIG_URL: str = Field(default="https://auth.example.com/.well-known/openid-configuration", description="The URL for the OAuth server configuration")
    OAUTH_CLIENT_ID: str = Field(default="client_id", description="The client ID for OAuth")
    OAUTH_CLIENT_SECRET: str = Field(default="client_secret", description="The client secret for OAuth")
    OAUTH_CLIENT_KWARGS: str = Field(default="openid email profile", description="The client kwargs for OAuth")
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

settings = Settings()
class App(FastAPI):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = cls(*args, **kwargs)
        return cls._instance

    def __init__(self, *args, **kwargs):

        self.name = settings.SERVICE_NAME
        self.otel_endpoint = settings.OTEL_ENDPOINT

        # Initialize the FastAPI app
        super().__init__(lifespan=lifespan, *args, **kwargs)

        # Set up tracing
        trace_provider = TracerProvider(
            resource=Resource.create(attributes={"service.name": self.name})
        )
        logger.info(f"Tracing provider created for {self.name}")

        # Set up the OTLP exporter
        if self.otel_endpoint:
            exporter = OTLPSpanExporter(endpoint=self.otel_endpoint, insecure=False)
            logger.info(f"OTLP exporter created for {self.otel_endpoint}")
        else:
            exporter = ConsoleSpanExporter()
            logger.info("Console exporter created")

        # Add the exporter to the trace provider
        trace_provider.add_span_processor(BatchSpanProcessor(exporter))
        logger.info("Span processor added")

        # Set the tracer provider for the app
        trace.set_tracer_provider(trace_provider)

        # Instrument the FastAPI app
        FastAPIInstrumentor.instrument_app(self)
        logger.info("FastAPI app instrumented")
