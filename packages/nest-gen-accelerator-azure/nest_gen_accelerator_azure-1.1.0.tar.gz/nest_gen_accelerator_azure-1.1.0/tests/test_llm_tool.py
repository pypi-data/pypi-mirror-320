import json

import pytest
import requests
from promptflow.connections import CustomConnection

from nest_gen_accelerator_azure.tools.llm_tool import llm_tool


@pytest.fixture
def my_custom_connection() -> CustomConnection:
    return CustomConnection(
        {
            "client_id": "my-client-id",
            "client_secret": "my-client-secret",
        },
        {
            "endpoint": "my-endpoint",
        },
    )


@pytest.fixture
def my_llm_mock_response():
    return {
        "usage": {"total_tokens": 42},
        "choices": [{"message": {"content": "This is a mock response"}}],
    }


@pytest.fixture
def my_llm_error_response():
    return {
        "errorMessage": {
            "error": {
                "message": "no healthy upstream",
                "innererror": {"code": "HTTPError"},
            }
        }
    }


def test_llm_tool(mocker, my_custom_connection, my_llm_mock_response):
    mock_requests_post = mocker.patch(
        "nest_gen_accelerator_azure.tools.llm_tool.requests.post"
    )
    mock_requests_post.return_value.json.return_value = my_llm_mock_response
    mock_requests_post.return_value.status_code = 200

    result = llm_tool(my_custom_connection, rendered_prompt="user:\nThis is a test")
    assert result["usage"]["total_tokens"] > 0
    assert result["choices"][0]["message"]["content"] == "This is a mock response"


def test_http_500_response(mocker, my_custom_connection):
    mock_requests_post = mocker.patch(
        "nest_gen_accelerator_azure.tools.llm_tool.requests.post"
    )
    mock_response = mocker.Mock()
    mock_response.status_code = 500
    mock_response.text = '{"error": "Internal Server Error"}'
    mock_response.json.return_value = {"error": "Internal Server Error"}
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "500 Server Error: Internal Server Error"
    )
    mock_requests_post.return_value = mock_response

    result = llm_tool(my_custom_connection, rendered_prompt="user:\nThis is a test")
    assert "error" in result
    assert result["error"]["type"] == "HTTP error"
    assert "details" in result["error"]
    assert isinstance(result["error"]["response"], dict)
    assert result["error"]["status_code"] == 500


def test_azure_content_safety_error(mocker, my_custom_connection):
    mock_requests_post = mocker.patch(
        "nest_gen_accelerator_azure.tools.llm_tool.requests.post"
    )
    mock_response = mocker.Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {
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
    }
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "400 Client Error: Bad Request"
    )
    mock_requests_post.return_value = mock_response

    result = llm_tool(my_custom_connection, rendered_prompt="user:\nThis is a test")
    assert "error" in result
    assert result["error"]["type"] == "HTTP error"
    assert result["error"]["status_code"] == 400


def test_request_exception(mocker, my_custom_connection):
    mock_requests_post = mocker.patch(
        "nest_gen_accelerator_azure.tools.llm_tool.requests.post"
    )
    mock_response = mocker.Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.RequestException(
        "Request error"
    )
    mock_requests_post.return_value = mock_response

    result = llm_tool(my_custom_connection, rendered_prompt="user:\nThis is a test")
    assert "error" in result
    assert result["error"]["type"] == "Request error"
    assert "details" in result["error"]


def test_json_decode_error(mocker, my_custom_connection):
    mock_requests_post = mocker.patch(
        "nest_gen_accelerator_azure.tools.llm_tool.requests.post"
    )
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = "Invalid JSON response"
    mock_response.json.side_effect = json.JSONDecodeError(
        "Expecting value", "Invalid JSON response", 0
    )
    mock_requests_post.return_value = mock_response

    result = llm_tool(my_custom_connection, rendered_prompt="user:\nThis is a test")
    assert "error" in result and result["error"]["type"] == "Invalid JSON object"
    assert "details" in result["error"]
