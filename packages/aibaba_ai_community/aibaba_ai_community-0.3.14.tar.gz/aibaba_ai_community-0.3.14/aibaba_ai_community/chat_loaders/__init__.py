"""**Chat Loaders** load chat messages from common communications platforms.

Load chat messages from various
communications platforms such as Facebook Messenger, Telegram, and
WhatsApp. The loaded chat messages can be used for fine-tuning models.

**Class hierarchy:**

.. code-block::

    BaseChatLoader --> <name>ChatLoader  # Examples: WhatsAppChatLoader, IMessageChatLoader

**Main helpers:**

.. code-block::

    ChatSession

"""  # noqa: E501

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aiagentsforce_community.chat_loaders.base import (
        BaseChatLoader,
    )
    from aiagentsforce_community.chat_loaders.facebook_messenger import (
        FolderFacebookMessengerChatLoader,
        SingleFileFacebookMessengerChatLoader,
    )
    from aiagentsforce_community.chat_loaders.gmail import (
        GMailLoader,
    )
    from aiagentsforce_community.chat_loaders.imessage import (
        IMessageChatLoader,
    )
    from aiagentsforce_community.chat_loaders.langsmith import (
        LangSmithDatasetChatLoader,
        LangSmithRunChatLoader,
    )
    from aiagentsforce_community.chat_loaders.slack import (
        SlackChatLoader,
    )
    from aiagentsforce_community.chat_loaders.telegram import (
        TelegramChatLoader,
    )
    from aiagentsforce_community.chat_loaders.whatsapp import (
        WhatsAppChatLoader,
    )

__all__ = [
    "BaseChatLoader",
    "FolderFacebookMessengerChatLoader",
    "GMailLoader",
    "IMessageChatLoader",
    "LangSmithDatasetChatLoader",
    "LangSmithRunChatLoader",
    "SingleFileFacebookMessengerChatLoader",
    "SlackChatLoader",
    "TelegramChatLoader",
    "WhatsAppChatLoader",
]

_module_lookup = {
    "BaseChatLoader": "alibaba_ai_core.chat_loaders",
    "FolderFacebookMessengerChatLoader": "aiagentsforce_community.chat_loaders.facebook_messenger",  # noqa: E501
    "GMailLoader": "aiagentsforce_community.chat_loaders.gmail",
    "IMessageChatLoader": "aiagentsforce_community.chat_loaders.imessage",
    "LangSmithDatasetChatLoader": "aiagentsforce_community.chat_loaders.langsmith",
    "LangSmithRunChatLoader": "aiagentsforce_community.chat_loaders.langsmith",
    "SingleFileFacebookMessengerChatLoader": "aiagentsforce_community.chat_loaders.facebook_messenger",  # noqa: E501
    "SlackChatLoader": "aiagentsforce_community.chat_loaders.slack",
    "TelegramChatLoader": "aiagentsforce_community.chat_loaders.telegram",
    "WhatsAppChatLoader": "aiagentsforce_community.chat_loaders.whatsapp",
}


def __getattr__(name: str) -> Any:
    if name in _module_lookup:
        module = importlib.import_module(_module_lookup[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__} has no attribute {name}")
