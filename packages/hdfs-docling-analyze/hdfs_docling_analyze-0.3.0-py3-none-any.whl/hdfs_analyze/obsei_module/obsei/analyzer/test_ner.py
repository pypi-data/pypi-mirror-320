from obsei.payload import TextPayload
from ner_analyzer import *

# Example input data
input_data = [
    TextPayload(processed_text="Apple is a technology company headquartered in California."),
]

transformers_analyzer = TransformersNERAnalyzer(
    model_name_or_path="NlpHUST/ner-vietnamese-electra-base",
    grouped_entities=True
)

transformers_results = transformers_analyzer.analyze_input(input_data)
print("TransformersNERAnalyzer Results:")
for result in transformers_results:
    print(result.segmented_data)
