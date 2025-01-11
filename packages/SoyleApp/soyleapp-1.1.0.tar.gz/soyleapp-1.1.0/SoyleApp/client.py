import requests
from typing import Dict
from .exceptions import (
    SoyleAppError,
    AuthenticationError,
    APIError,
    ValidationError,
    InsufficientBalanceError,
)
from .constants import BASE_URL, SUPPORTED_LANGUAGES


class SoyleApp:
    def __init__(self, token: str):
        if not token or not isinstance(token, str):
            raise ValidationError("Token must be a non-empty string")
        self.token = token.strip()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

    def _post(self, endpoint: str, data: Dict) -> Dict:
        url = f"{BASE_URL}{endpoint}"
        response = requests.post(url, json=data, headers=self.headers, timeout=30)

        if response.status_code == 401:
            raise AuthenticationError("Invalid or expired token")
        elif response.status_code == 403:
            raise AuthenticationError("Access forbidden")
        elif response.status_code == 402:
            raise InsufficientBalanceError("Insufficient balance")
        elif response.status_code >= 400:
            raise APIError(f"API Error {response.status_code}: {response.text}")

        return response.json()

    def text_translate(self, source_language: str, target_language: str, text: str) -> str:
        """
        Translate text from one language to another.
        :param source_language: Source language of the text
        :param target_language: Target language for the translation
        :param text: Text to be translated
        :return: Translated text
        """
        if source_language not in SUPPORTED_LANGUAGES:
            raise ValidationError(
                f"Invalid source language: {source_language}. "
                f"Supported languages: {', '.join(SUPPORTED_LANGUAGES)}"
            )
        if target_language not in SUPPORTED_LANGUAGES:
            raise ValidationError(
                f"Invalid target language: {target_language}. "
                f"Supported languages: {', '.join(SUPPORTED_LANGUAGES)}"
            )
        if not text or not isinstance(text, str):
            raise ValidationError("Text must be a non-empty string")

        payload = {
            "source_language": source_language,
            "target_language": target_language,
            "text": text,
            "output_format": "text",
        }

        response = self._post("translate/text/", payload)
        return response.get("text", "")

    def audio_translate(
        self, source_language: str, target_language: str, text: str, voice: str = "male"
    ) -> str:
        """
        Translate text and generate audio output.
        :param source_language: Source language of the text
        :param target_language: Target language for the translation
        :param text: Text to be translated
        :param voice: Voice type for the audio output ('male' or 'female')
        :return: Audio data in base16 format
        """
        if source_language not in SUPPORTED_LANGUAGES:
            raise ValidationError(
                f"Invalid source language: {source_language}. "
                f"Supported languages: {', '.join(SUPPORTED_LANGUAGES)}"
            )
        if target_language not in SUPPORTED_LANGUAGES:
            raise ValidationError(
                f"Invalid target language: {target_language}. "
                f"Supported languages: {', '.join(SUPPORTED_LANGUAGES)}"
            )
        if not text or not isinstance(text, str):
            raise ValidationError("Text must be a non-empty string")
        if voice not in {"male", "female"}:
            raise ValidationError("Voice must be either 'male' or 'female'")

        payload = {
            "source_language": source_language,
            "target_language": target_language,
            "text": text,
            "output_format": "audio",
            "output_voice": voice,
        }

        response = self._post("translate/text/", payload)
        return response.get("audio", "")  # Returns audio in base16 format
