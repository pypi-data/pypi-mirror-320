from typing import List

from deepeval.guardrails.api import (
    ApiGuard,
    ApiGuardrails,
    GuardsResponseData,
)
from deepeval.guardrails.base_guard import BaseGuard
from deepeval.confident.api import Api, HttpMethods, Endpoints
from deepeval.telemetry import capture_guardrails
from deepeval.utils import is_confident
from deepeval.guardrails.api import BASE_URL


class Guardrails:
    def __init__(self, guards: List[BaseGuard]):
        self.guards: List[BaseGuard] = guards

    def guard(self, input: str, response: str):
        print(self.guards)
        if len(self.guards) == 0:
            raise TypeError(
                "Guardrails cannot guard LLM responses when no guards are provided."
            )

        with capture_guardrails(guards=self.guards):
            # Prepare parameters for API request
            api_guards = []
            for guard in self.guards:
                api_guard = ApiGuard(
                    guard=guard.get_guard_name(),
                    guard_type=guard.get_guard_type(),
                    input=input,
                    response=response,
                    vulnerability_types=getattr(guard, "vulnerabilities", None),
                    purpose=getattr(guard, "purpose", None),
                    allowed_topics=getattr(guard, "allowed_topics", None),
                )
                api_guards.append(api_guard)

            api_guardrails = ApiGuardrails(guards=api_guards)
            body = api_guardrails.model_dump(by_alias=True, exclude_none=True)

            # API request
            if is_confident():
                api = Api(base_url=BASE_URL)
                response = api.send_request(
                    method=HttpMethods.POST,
                    endpoint=Endpoints.GUARDRAILS_ENDPOINT,
                    body=body,
                )
                return GuardsResponseData(**response).result
            else:
                raise Exception(
                    "Access denied: You need Enterprise access on Confident AI to use deepeval's guardrails."
                )
