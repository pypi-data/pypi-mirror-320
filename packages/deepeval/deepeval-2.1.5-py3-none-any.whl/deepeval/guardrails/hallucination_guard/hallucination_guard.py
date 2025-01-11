from deepeval.guardrails.base_guard import BaseOutputGuard
from deepeval.guardrails.api import ApiGuard, GuardResponseData
from deepeval.confident.api import Api, HttpMethods, Endpoints
from deepeval.guardrails.api import BASE_URL
from deepeval.utils import is_confident


class HallucinationGuard(BaseOutputGuard):

    def guard(self, response: str) -> int:
        guard_params = ApiGuard(
            guard=self.get_guard_name(),
            guard_type=self.get_guard_type(),
            response=response,
        )
        body = guard_params.model_dump(by_alias=True, exclude_none=True)

        # API request
        if is_confident():
            api = Api(base_url=BASE_URL)
            response = api.send_request(
                method=HttpMethods.POST,
                endpoint=Endpoints.GUARD_ENDPOINT,
                body=body,
            )
            return GuardResponseData(**response).result
        else:
            raise Exception("To use DeepEval guardrails, run `deepeval login`")

    async def a_guard(self, response: str) -> int:
        guard_params = ApiGuard(
            guard=self.get_guard_name(),
            guard_type=self.get_guard_type(),
            response=response,
        )
        body = guard_params.model_dump(by_alias=True, exclude_none=True)

        # API request
        if is_confident():
            api = Api(base_url=BASE_URL)
            response = await api.a_send_request(
                method=HttpMethods.POST,
                endpoint=Endpoints.GUARD_ENDPOINT,
                body=body,
            )
            return GuardResponseData(**response).result
        else:
            raise Exception("To use DeepEval guardrails, run `deepeval login`")

    def get_guard_name(self) -> str:
        return "Hallucination Guard"
