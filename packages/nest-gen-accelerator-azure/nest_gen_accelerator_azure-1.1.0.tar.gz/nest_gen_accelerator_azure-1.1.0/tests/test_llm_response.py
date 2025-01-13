import pytest

from nest_gen_accelerator_azure.components.output_parsers import JsonOutputParser
from nest_gen_accelerator_azure.components.outputs import ExitStrategy
from nest_gen_accelerator_azure.components.outputs.llm_response import LLMResponse
from nest_gen_accelerator_azure.exceptions import InvalidLLMResponseException


@pytest.fixture
def valid_llm_response():
    return {
        "choices": [
            {
                "message": {
                    "content": '{"content": "Do you know where my orders FR6A0889826 and FR6A0898073 are?", "callToAction": {"type": "NONE"}, "exitStrategy": ""}'
                }
            }
        ],
        "model": "test-model",
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
        },
        "params": {"seed": 42, "temperature": 0.7},
    }


@pytest.fixture
def handover_response():
    return {
        "choices": [
            {
                "message": {
                    "content": '{"content": "Can I talk to an agent?", "callToAction": {"type": "TO_LIVE_AGENT", "value": true}, "exitStrategy": ""}'
                }
            }
        ],
        "model": "test-model",
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
        },
        "params": {"seed": 42, "temperature": 0.7},
    }


@pytest.fixture
def invalid_llm_response():
    return {
        "choices": [],
        "model": "test-model",
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
        },
        "params": {"seed": 42, "temperature": 0.7},
    }


@pytest.fixture
def policy_violation_response():
    return {
        "error": {
            "type": "HTTP error",
            "details": "400 Client Error: Bad Request",
            "response": {
                "errorCode": 400,
                "errorType": "HTTP:BAD_REQUEST",
                "errorMessage": {
                    "error": {
                        "message": "The response was filtered due to the triggering of content management policy.",
                        "type": None,
                        "param": "prompt",
                        "code": "content_filter",
                        "status": 400,
                        "innererror": {
                            "code": "ResponsibleAIPolicyViolation",
                            "content_filter_result": {
                                "hate": {"filtered": False, "severity": "safe"},
                                "jailbreak": {"filtered": False, "detected": False},
                                "self_harm": {"filtered": False, "severity": "safe"},
                                "sexual": {"filtered": False, "severity": "safe"},
                                "violence": {"filtered": True, "severity": "medium"},
                            },
                        },
                    }
                },
            },
            "status_code": 400,
        },
        "params": {},
    }


@pytest.fixture
def error_response():
    return {
        "error": {
            "type": "HTTP error",
            "details": "500 Server Error: Internal Server Error",
            "response": {"error": "Internal Server Error"},
            "status_code": 500,
        }
    }


class TestValidResponses:
    def test_from_json_valid_response(self, valid_llm_response):
        tracking_id = "test-tracking-id"
        context = "test-context"
        response = LLMResponse.from_json(valid_llm_response, tracking_id, context)

        assert (
            response.content
            == "Do you know where my orders FR6A0889826 and FR6A0898073 are?"
        )
        assert response.call_to_action.type == "NONE"
        assert response.exit_strategy == ExitStrategy.EMPTY
        assert response.model_details["name"] == "test-model"
        assert response.model_details["total_tokens"] == 30
        assert response.model_details["params"] == {"seed": 42, "temperature": 0.7}
        assert (
            response.model_details["content_filter_results"]["prompt_results"]
            is not None
        )
        assert (
            response.model_details["content_filter_results"]["completion_results"]
            is not None
        )
        assert response.context == context

    def test_from_json_handover_response(self, handover_response):
        tracking_id = "test-tracking-id"
        context = "test-context"
        response = LLMResponse.from_json(handover_response, tracking_id, context)

        assert response.call_to_action.type in {
            "TO_LIVE_AGENT",
            "NONE",
        }  # TODO Remove NONE when SEVOLU-617 (random TO_LIVE_AGENT) is removed
        assert response.exit_strategy == ExitStrategy.EMPTY
        assert response.model_details["name"] == "test-model"
        assert response.model_details["total_tokens"] == 30
        assert response.context == context

    def test_to_json_serialization(self, valid_llm_response):
        tracking_id = "test-tracking-id"
        context = "test-context"
        response = LLMResponse.from_json(valid_llm_response, tracking_id, context)
        serialized = response.to_dict()

        assert isinstance(serialized, dict)
        assert (
            serialized["content"]
            == "Do you know where my orders FR6A0889826 and FR6A0898073 are?"
        )
        assert serialized["callToAction"] == {"type": "NONE"}
        assert serialized["exitStrategy"] == ""
        assert serialized["modelStats"] == {
            "name": "test-model",
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
            "params": {"seed": 42, "temperature": 0.7},
            "content_filter_results": {
                "prompt_results": {},
                "completion_results": {},
            },
        }
        assert serialized["context"] == context


class TestErrorHandling:
    def test_from_json_invalid_response(self, invalid_llm_response):
        tracking_id = "test-tracking-id"
        context = "test-context"
        response = LLMResponse.from_json(invalid_llm_response, tracking_id, context)

        assert response.call_to_action.type == "NONE"
        assert response.exit_strategy == ExitStrategy.ON_ERROR
        assert response.model_details["name"] == "test-model"
        assert response.model_details["total_tokens"] == 30
        assert response.context == context

    def test_from_json_parsing_error(self, mocker, valid_llm_response):
        tracking_id = "test-tracking-id"
        context = "test-context"
        mocker.patch.object(
            JsonOutputParser, "parse", side_effect=ValueError("Parsing error")
        )

        response = LLMResponse.from_json(valid_llm_response, tracking_id, context)

        assert response.call_to_action.type == "NONE"
        assert response.exit_strategy == ExitStrategy.ON_ERROR
        assert response.model_details["name"] == "test-model"
        assert response.model_details["total_tokens"] == 30
        assert (
            not response.model_details["content_filter_results"]["prompt_results"]
            and not response.model_details["content_filter_results"][
                "completion_results"
            ]
        )
        assert response.context == context

    def test_content_policy_violation(self, policy_violation_response):
        tracking_id = "test-tracking-id"
        context = "test-context"
        response = LLMResponse.from_json(
            policy_violation_response, tracking_id, context
        )

        assert response.call_to_action.type == "NONE"
        assert response.exit_strategy == ExitStrategy.OUT_OF_DOMAIN
        assert (
            response.model_details["content_filter_results"]["prompt_results"]
            is not None
        )
        assert response.model_details["content_filter_results"]["prompt_results"] == {
            "hate": {"filtered": False, "severity": "safe"},
            "jailbreak": {"filtered": False, "detected": False},
            "self_harm": {"filtered": False, "severity": "safe"},
            "sexual": {"filtered": False, "severity": "safe"},
            "violence": {"filtered": True, "severity": "medium"},
        }
        assert (
            response.model_details["content_filter_results"]["completion_results"] == {}
        )
        assert response.context == context

    def test_error_response(self, error_response):
        tracking_id = "test-tracking-id"
        context = "test-context"
        response = LLMResponse.from_json(error_response, tracking_id, context)

        assert response.exit_strategy == ExitStrategy.ON_ERROR
        assert response.model_details["total_tokens"] is None
        assert (
            not response.model_details["content_filter_results"]["prompt_results"]
            and not response.model_details["content_filter_results"][
                "completion_results"
            ]
        )
        assert response.context == context
