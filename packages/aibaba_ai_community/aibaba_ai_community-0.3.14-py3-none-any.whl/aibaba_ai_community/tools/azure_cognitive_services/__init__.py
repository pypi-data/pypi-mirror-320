"""Azure Cognitive Services Tools."""

from aiagentsforce_community.tools.azure_cognitive_services.form_recognizer import (
    AzureCogsFormRecognizerTool,
)
from aiagentsforce_community.tools.azure_cognitive_services.image_analysis import (
    AzureCogsImageAnalysisTool,
)
from aiagentsforce_community.tools.azure_cognitive_services.speech2text import (
    AzureCogsSpeech2TextTool,
)
from aiagentsforce_community.tools.azure_cognitive_services.text2speech import (
    AzureCogsText2SpeechTool,
)
from aiagentsforce_community.tools.azure_cognitive_services.text_analytics_health import (
    AzureCogsTextAnalyticsHealthTool,
)

__all__ = [
    "AzureCogsImageAnalysisTool",
    "AzureCogsFormRecognizerTool",
    "AzureCogsSpeech2TextTool",
    "AzureCogsText2SpeechTool",
    "AzureCogsTextAnalyticsHealthTool",
]
