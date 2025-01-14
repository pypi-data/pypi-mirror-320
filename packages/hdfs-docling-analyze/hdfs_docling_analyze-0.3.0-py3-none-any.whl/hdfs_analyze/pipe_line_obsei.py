import logging
import json
from .obsei_module.obsei.analyzer.classification_analyzer import ZeroShotClassificationAnalyzer, ClassificationAnalyzerConfig
from .obsei_module.obsei.sink.http_sink import HttpSinkConfig, HttpSink
from .obsei_module.obsei.analyzer.sentiment_analyzer import *
from  .connect_mongo import *
from obsei.payload import TextPayload
from bson.objectid import ObjectId
from collections import defaultdict
from .obsei_module.obsei.analyzer.ner_analyzer import *

labels = [
    "Thời sự", "Thế giới", "Xe", "Giáo dục", "Bất động sản", "Khoa học", "Giải trí",
    "Thể thao", "Pháp luật", "Sức khỏe", "Đời sống", "Du lịch", "Công nghệ", 
    "Kinh tế", "Văn hóa", "Thời trang", "Giáo dục", "Kỹ thuật"
]

#chuyển đổi ngôn ngữ
translations = {
    "Thời sự": {
        "EN": "Current Affairs", 
        "JP": "時事", 
        "FR": "Actualités", 
        "KR": "시사", 
        "RU": "Текущие события", 
        "ZH": "时事", 
        "HI": "समसामयिक",
        "PT": "Atualidades", 
        "ES": "Actualidades"
    },
    "Thế giới": {
        "EN": "World", 
        "JP": "世界", 
        "FR": "Monde", 
        "KR": "세계", 
        "RU": "Мир", 
        "ZH": "世界", 
        "HI": "दुनिया",
        "PT": "Mundo", 
        "ES": "Mundo"
    },
    "Xe": {
        "EN": "Automobiles", 
        "JP": "車", 
        "FR": "Automobiles", 
        "KR": "자동차", 
        "RU": "Автомобили", 
        "ZH": "汽车", 
        "HI": "ऑटोमोबाइल",
        "PT": "Automóveis", 
        "ES": "Automóviles"
    },
    "Giáo dục": {
        "EN": "Education", 
        "JP": "教育", 
        "FR": "Éducation", 
        "KR": "교육", 
        "RU": "Образование", 
        "ZH": "教育", 
        "HI": "शिक्षा",
        "PT": "Educação", 
        "ES": "Educación"
    },
    "Bất động sản": {
        "EN": "Real Estate", 
        "JP": "不動産", 
        "FR": "Immobilier", 
        "KR": "부동산", 
        "RU": "Недвижимость", 
        "ZH": "房地产", 
        "HI": "रियल एस्टेट",
        "PT": "Imóveis", 
        "ES": "Bienes raíces"
    },
    "Khoa học": {
        "EN": "Science", 
        "JP": "科学", 
        "FR": "Science", 
        "KR": "과학", 
        "RU": "Наука", 
        "ZH": "科学", 
        "HI": "विज्ञान",
        "PT": "Ciência", 
        "ES": "Ciencia"
    },
    "Kỹ thuật": {
        "EN": "Engineering", 
        "JP": "エンジニアリング", 
        "FR": "Ingénierie", 
        "KR": "엔지니어링", 
        "RU": "Инженерия", 
        "ZH": "工程", 
        "HI": "अभियांत्रिकी",
        "PT": "Engenharia", 
        "ES": "Ingeniería"
    },
    "Công nghệ": {
        "EN": "Technology", 
        "JP": "技術", 
        "FR": "Technologie", 
        "KR": "기술", 
        "RU": "Технологии", 
        "ZH": "技术", 
        "HI": "प्रौद्योगिकी",
        "PT": "Tecnologia", 
        "ES": "Tecnología"
    },
    "Giải trí": {
        "EN": "Entertainment", 
        "JP": "エンターテインメント", 
        "FR": "Divertissement", 
        "KR": "엔터테인먼트", 
        "RU": "Развлечения", 
        "ZH": "娱乐", 
        "HI": "मनोरंजन",
        "PT": "Entretenimento", 
        "ES": "Entretenimiento"
    },
    "Thể thao": {
        "EN": "Sports", 
        "JP": "スポーツ", 
        "FR": "Sports", 
        "KR": "스포츠", 
        "RU": "Спорт", 
        "ZH": "体育", 
        "HI": "खेल",
        "PT": "Esportes", 
        "ES": "Deportes"
    },
    "Pháp luật": {
        "EN": "Law", 
        "JP": "法律", 
        "FR": "Droit", 
        "KR": "법", 
        "RU": "Закон", 
        "ZH": "法律", 
        "HI": "कानून",
        "PT": "Lei", 
        "ES": "Ley"
    },
    "Sức khỏe": {
        "EN": "Health", 
        "JP": "健康", 
        "FR": "Santé", 
        "KR": "건강", 
        "RU": "Здоровье", 
        "ZH": "健康", 
        "HI": "स्वास्थ्य",
        "PT": "Saúde", 
        "ES": "Salud"
    },
    "Đời sống": {
        "EN": "Lifestyle", 
        "JP": "ライフスタイル", 
        "FR": "Mode de vie", 
        "KR": "라이프스타일", 
        "RU": "Образ жизни", 
        "ZH": "生活方式", 
        "HI": "जीवनशैली",
        "PT": "Estilo de vida", 
        "ES": "Estilo de vida"
    },
    "Du lịch": {
        "EN": "Travel", 
        "JP": "旅行", 
        "FR": "Voyage", 
        "KR": "여행", 
        "RU": "Путешествие", 
        "ZH": "旅游", 
        "HI": "यात्रा",
        "PT": "Viagem", 
        "ES": "Viaje"
    },
    "Công nghệ": {
        "EN": "Technology", 
        "JP": "技術", 
        "FR": "Technologie", 
        "KR": "기술", 
        "RU": "Технологии", 
        "ZH": "技术", 
        "HI": "प्रौद्योगिकी",
        "PT": "Tecnologia", 
        "ES": "Tecnología"
    },
    "Kinh tế": {
        "EN": "Economy", 
        "JP": "経済", 
        "FR": "Économie", 
        "KR": "경제", 
        "RU": "Экономика", 
        "ZH": "经济", 
        "HI": "अर्थव्यवस्था",
        "PT": "Economia", 
        "ES": "Economía"
    },
    "Văn hóa": {
        "EN": "Culture", 
        "JP": "文化", 
        "FR": "Culture", 
        "KR": "문화", 
        "RU": "Культура", 
        "ZH": "文化", 
        "HI": "संस्कृति",
        "PT": "Cultura", 
        "ES": "Cultura"
    },
    "Thời trang": {
        "EN": "Fashion", 
        "JP": "ファッション", 
        "FR": "Mode", 
        "KR": "패션", 
        "RU": "Мода", 
        "ZH": "时尚", 
        "HI": "फ़ैशन",
        "PT": "Moda", 
        "ES": "Moda"
    }
}

def get_label(language:str):
    if(language == "VN"):
        return labels
    elif(language == "JP"):
        labels_jp = [translations[label]["JP"] for label in labels if label in translations]
        return labels_jp
    elif(language =="EN"):
        labels_en = [translations[label]["EN"] for label in labels if label in translations]
        return labels_en
    elif(language =="FR"):
        labels_fr = [translations[label]["FR"] for label in labels if label in translations]
        return labels_fr
    elif(language=="KR"):
        labels_kr = [translations[label]["KR"] for label in labels if label in translations]
        return labels_kr
    elif(language=="RU"):
        labels_fr = [translations[label]["RU"] for label in labels if label in translations]
        return labels_fr
    elif(language=="ZH"):
        labels_fr = [translations[label]["ZH"] for label in labels if label in translations]
        return labels_fr
    elif(language=="HI"):
        labels_fr = [translations[label]["HI"] for label in labels if label in translations]
        return labels_fr
    elif(language=="PT"):
        labels_fr = [translations[label]["PT"] for label in labels if label in translations]
        return labels_fr
    elif(language=="ES"):
        labels_fr = [translations[label]["ES"] for label in labels if label in translations]
        return labels_fr
    else:
        return labels


def get_config_language(language:str) -> list:
    if(language == "VN"):
        return [
            "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7",
            "joeddav/xlm-roberta-large-xnli",
            "NlpHUST/ner-vietnamese-electra-base"
        ]
    elif(language == "JP"):
        return [
            "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7",
            "joeddav/xlm-roberta-large-xnli",
            "tsmatz/xlm-roberta-ner-japanese"
        ]
    elif(language =="EN"):
        return [
            "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7",
            "joeddav/xlm-roberta-large-xnli",
            "dslim/bert-base-NER"
        ]
    else:
        return [
            "facebook/bart-large-mnli",
            "joeddav/xlm-roberta-large-xnli",
            "facebook/bart-large-mnli"
        ]
        

async def get_object_by_link(db_name, collection_name, link):
    collection = connect_to_mongo(db_name, collection_name)
    if collection is None:
        print("Failed to connect to MongoDB.")
        return None
    result = collection.find_one({"link": link})
    return result

async def get_existing_record_by_name(db_name, collection_name, name, link):
    collection = connect_to_mongo(db_name, collection_name)
    if collection is None:
        print("Failed to connect to MongoDB.")
        return None
    result = collection.find_one({"name": name, "link": link}) 
    return result


def group_entities(results):
    grouped_results = []
    for result in results:
        ner_data = result.segmented_data.get("ner_data", [])
        grouped_entities = defaultdict(list)
        for entity in ner_data:
            grouped_entities[entity["entity_group"]].append(entity["word"])
        grouped_results.append({
            "grouped_ner_data": {
                entity_group: "; ".join(words)
                for entity_group, words in grouped_entities.items()
            }
        })
    return grouped_results


async def process_url_hadoop(mongo_url:str,url: str, data: str,  db_name: str, collection_name: str,language:str):
    """Test"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    models = get_config_language(language)
    labels = get_label(language)
    

    texts = [data]  # data phải là kiểu str
    crawled_data = [TextPayload(processed_text=text) for text in texts]
    if not crawled_data:
        logger.error("No data found from crawler")
        return {"error": "No data found from crawler"}
    
    # Config Classification
    analyzer_config = ClassificationAnalyzerConfig(
    labels = labels,
    multi_class_classification=False,
    add_positive_negative_labels=False
)
    analyzer = ZeroShotClassificationAnalyzer(
        model_name_or_path=models[0],
        device="auto"
    )
    analysis_results = analyzer.analyze_input(
        source_response_list=crawled_data,
        analyzer_config=analyzer_config
    )
    
    #Config Sentiment
    transformers_analyzer_config = TransformersSentimentAnalyzerConfig(
    labels=["positive", "negative","neutral"],
    multi_class_classification=False,
    add_positive_negative_labels=True) 
    transformers_analyzer = TransformersSentimentAnalyzer(model_name_or_path=models[1], device="auto")
    transformers_results = transformers_analyzer.analyze_input(crawled_data, analyzer_config=transformers_analyzer_config)
    
    #Config NER
    transformers_analyzer_ner = TransformersNERAnalyzer(
    model_name_or_path=models[2],
    grouped_entities=True)
    transformers_results_ner = transformers_analyzer_ner.analyze_input(crawled_data)
    grouped_results = group_entities(transformers_results_ner)
    grouped_results = grouped_results[0].get('grouped_ner_data', {})
    
    #Config Sink
    http_sink_config = HttpSinkConfig(
        url="https://httpbin.org/post", 
        headers={"Content-type": "application/json"},
        base_payload={"common_field": "test cua VNY"},
    )
    
    http_sink = HttpSink()
    
    #Get Response
    responses = http_sink.send_data(analysis_results, http_sink_config)
    responses1 = http_sink.send_data(transformers_results, http_sink_config)
    
    #Response Classification
    response_data = []
    for i, response in enumerate(responses):
        response_content = response.read().decode("utf-8")
        response_json = json.loads(response_content)
        response_data.append({
            "response_index": i + 1,
            "content": response_json,
            "status_code": response.status,
            "headers": dict(response.getheaders())
        })
    #Response Sentiment
    response_data1 = []
    for i, response1 in enumerate(responses1):
        response_content1 = response1.read().decode("utf-8")
        response_json1 = json.loads(response_content1)
        response_data1.append({
            "response_index": i + 1,
            "content": response_json1,
            "status_code": response1.status,
            "headers": dict(response1.getheaders())
        })
    
    #Response NER
    content_data1 = [item["content"] for item in response_data1]
    processed_text_sentiment = content_data1[0].get("json", {}).get('segmented_data', 'No processed text available.').get('classifier_data')
    
    #GetContent
    content_data = [item["content"] for item in response_data]
    processed_text = content_data[0].get("json", {}).get('segmented_data', 'No processed text available.').get('classifier_data')
    
    #get Content
    processed_text1 = content_data[0].get("json", {})
    content_data = processed_text1.get('meta').get('text')  
    
    collection1 = connect_to_mongo(mongo_url,db_name,collection_name)
    
    record = collection1.find_one({
    "link": url})   
    
    if record:
      collection1.update_one(
      {"_id": ObjectId(record["_id"])},
      {"$set": {
              "obsei_sentiment": processed_text_sentiment,
              "obsei_classification":processed_text,
              "obsei_ner":grouped_results
              }}
    )
    else:
        pass
    return processed_text,processed_text_sentiment,grouped_results

