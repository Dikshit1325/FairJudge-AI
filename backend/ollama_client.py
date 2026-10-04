"""Small synchronous client for the local Ollama generate endpoint."""

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from pydantic import BaseModel


class OllamaUnavailableError(RuntimeError):
    """Ollama cannot be reached or returned a server error."""


class OllamaResponseError(RuntimeError):
    """Ollama returned an invalid envelope or malformed generated content."""


def generate_structured(prompt: str, response_model: type[BaseModel]) -> str:
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    model = os.getenv("OLLAMA_MODEL", "qwen3:8b")
    timeout = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "180"))
    body = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "format": response_model.model_json_schema(),
            "stream": False,
            "think": False,
            "options": {"temperature": 0, "num_ctx": 8192, "num_predict": 1800},
        }
    ).encode("utf-8")
    request = Request(
        f"{base_url}/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            envelope = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        if exc.code >= 500:
            raise OllamaUnavailableError(
                f"Ollama returned HTTP {exc.code}; verify it is running and model '{model}' is available. "
                f"Ollama detail: {detail or 'no detail provided'}"
            ) from exc
        raise OllamaResponseError(f"Ollama request failed (HTTP {exc.code}): {detail}") from exc
    except (URLError, TimeoutError, ConnectionError, OSError) as exc:
        raise OllamaUnavailableError(
            "Ollama is unavailable. Start the local Ollama service and ensure "
            f"the configured model '{model}' is installed."
        ) from exc
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise OllamaResponseError("Ollama returned a malformed response envelope.") from exc

    if not isinstance(envelope, dict):
        raise OllamaResponseError("Ollama returned an invalid response envelope.")
    generated = envelope.get("response")
    if not isinstance(generated, str) or not generated.strip():
        raise OllamaResponseError("Ollama response did not contain generated JSON text.")
    return generated
