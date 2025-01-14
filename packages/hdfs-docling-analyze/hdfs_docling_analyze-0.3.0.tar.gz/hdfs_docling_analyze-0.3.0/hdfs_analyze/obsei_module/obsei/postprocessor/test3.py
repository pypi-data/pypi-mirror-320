from obsei.analyzer.classification_analyzer import ClassificationAnalyzerConfig, ZeroShotClassificationAnalyzer
from obsei.analyzer.sentiment_analyzer import *

# Tạo đối tượng cấu hình phân tích
transformers_analyzer_config = TransformersSentimentAnalyzerConfig(
    labels=["positive", "negative"],
    multi_class_classification=False,
    add_positive_negative_labels=True
)
text_samples = [
    "Tao ghét sản phẩm này",
    "I hate this, it's terrible.",
    "sản phẩm này rất tốt",
]

# Chuyển văn bản thành đối tượng TextPayload
source_responses = [TextPayload(processed_text=text) for text in text_samples]
# Tạo đối tượng phân tích cảm xúc với TransformersSentimentAnalyzer
transformers_analyzer = TransformersSentimentAnalyzer(model_name_or_path="facebook/bart-large-mnli", device="auto")

# Phân tích cảm xúc với TransformersSentimentAnalyzer và truyền analyzer_config
transformers_results = transformers_analyzer.analyze_input(source_responses, analyzer_config=transformers_analyzer_config)
print(transformers_results)


