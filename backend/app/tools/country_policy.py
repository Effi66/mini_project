from app.domain.policy_repository import PolicyRepository


def get_country_policy(policy_repository: PolicyRepository, country: str):
    return policy_repository.get_policy_summary(country)

