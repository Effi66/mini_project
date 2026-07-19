from pathlib import Path

from fastapi import FastAPI

from app.api.routes_agent import router as agent_router
from app.api.routes_countries import router as countries_router
from app.core.config import build_settings
from app.domain.policy_repository import PolicyRepository


def create_app(data_dir: Path | None = None) -> FastAPI:
    settings = build_settings(data_dir=data_dir)
    app = FastAPI(title="Global Employment Agent")
    app.state.settings = settings
    app.state.policy_repository = PolicyRepository(settings.data_dir)
    app.include_router(agent_router)
    app.include_router(countries_router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
