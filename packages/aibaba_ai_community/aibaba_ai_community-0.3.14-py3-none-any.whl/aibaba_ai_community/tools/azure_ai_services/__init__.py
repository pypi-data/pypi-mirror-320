"""Azure AI Services Tools."""

from aiagentsforce_community.tools.azure_ai_services.document_intelligence import (
    AzureAiServicesDocumentIntelligenceTool,
)
from aiagentsforce_community.tools.azure_ai_services.image_analysis import (
    AzureAiServicesImageAnalysisTool,
)
from aiagentsforce_community.tools.azure_ai_services.speech_to_text import (
    AzureAiServicesSpeechToTextTool,
)
from aiagentsforce_community.tools.azure_ai_services.text_analytics_for_health import (
    AzureAiServicesTextAnalyticsForHealthTool,
)
from aiagentsforce_community.tools.azure_ai_services.text_to_speech import (
    AzureAiServicesTextToSpeechTool,
)

__all__ = [
    "AzureAiServicesDocumentIntelligenceTool",
    "AzureAiServicesImageAnalysisTool",
    "AzureAiServicesSpeechToTextTool",
    "AzureAiServicesTextToSpeechTool",
    "AzureAiServicesTextAnalyticsForHealthTool",
]
