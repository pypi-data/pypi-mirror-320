# mytextlib/__init__.py
from .model import MyTextModel

def analyze_text(text, model_dir="mytextlib/model_files"):
    """
    Analyze text using the fine-tuned model.
    """
    model = MyTextModel(model_dir)
    return model.analyze_sentiment(text)