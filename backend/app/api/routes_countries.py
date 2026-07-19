from fastapi import APIRouter, HTTPException, Request

from app.domain.policy_repository import PolicyRepository


router = APIRouter(prefix="/api", tags=["countries"])


def get_repository(request: Request) -> PolicyRepository:
    return request.app.state.policy_repository


@router.get("/countries")
def list_countries(request: Request) -> dict:
    repository = get_repository(request)
    return {"countries": [country.model_dump() for country in repository.list_countries()]}


@router.get("/policies/{country}")
def get_policy(country: str, request: Request) -> dict:
    repository = get_repository(request)
    try:
        return repository.get_policy_summary(country).model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

