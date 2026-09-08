from contextvars import ContextVar
from middlewares.lang.en.common import CommonMessage as _EnCommon
from middlewares.lang.id.common import CommonMessage as _IdCommon

DEFAULT_LANG = "en"
SUPPORTED_LANGUAGES = {"en", "id"}
current_lang: ContextVar[str] = ContextVar("current_lang", default=DEFAULT_LANG)

MESSAGES: dict[str, dict[str, str]] = {
    "en": {
        **_EnCommon().message,
    },
    "id": {
        **_IdCommon().message,
    },
}


def resolve_message(key: str, lang: str = DEFAULT_LANG) -> str:
    """Translate a message key using `lang`, falling back to English, then the raw key."""
    localized = MESSAGES.get(lang, MESSAGES[DEFAULT_LANG])
    return localized.get(key, MESSAGES[DEFAULT_LANG].get(key, key))
