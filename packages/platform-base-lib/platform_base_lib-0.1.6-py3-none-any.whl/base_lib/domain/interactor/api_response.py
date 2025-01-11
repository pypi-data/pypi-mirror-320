from typing import Any, Dict, Optional, List, Union
import uuid


class APIResponse:
    """
    Standardized API Response class to unify the structure of API responses.
    """

    def __init__(
        self,
        result: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
        status: int = 200,
        message: Optional[str] = None,
        error: Optional[Union[str, List[str]]] = None,
        traceId: Optional[str] = None,
    ):
        """
        Initialize the API response object with structured data.

        :param result: The actual data being returned in the response.
        :param status: HTTP status code indicating response type (200, 400, 500, etc.).
        :param message: A human-readable message providing additional context about the response.
        :param error: A string or list of error messages for failed responses.
        :param traceId: A unique identifier for tracing the request (auto-generated if not provided).
        """
        self.result = result or {}
        self.status = status
        self.message = message or self._default_message(status)
        self.error = error if status >= 400 else None
        self.traceId = traceId or str(
            uuid.uuid4()
        )  # Generate unique traceId if not provided

    @staticmethod
    def _default_message(status: int) -> str:
        """
        Provide a default message based on the status code.

        :param status: HTTP status code.
        :return: Default associated message.
        """
        if 200 <= status < 300:
            return "Success"
        elif 400 <= status < 500:
            return "Client Error"
        elif 500 <= status:
            return "Server Error"
        return "Unknown Status"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert APIResponse object to a dictionary for JSON serialization.

        :return: A dictionary representation of the API response.
        """
        response = {
            "status": self.status,
            "result": self.result,
            "message": self.message,
            "traceId": self.traceId,
        }

        # Include errors in response if status indicates an error
        if self.error:
            response["error"] = self.error

        return response

    def __repr__(self) -> str:
        """
        Represent the APIResponse object as a string for debugging.

        :return: String representation of the response.
        """
        return f"APIResponse(status={self.status}, message={self.message}, result={self.result}, traceId={self.traceId})"
