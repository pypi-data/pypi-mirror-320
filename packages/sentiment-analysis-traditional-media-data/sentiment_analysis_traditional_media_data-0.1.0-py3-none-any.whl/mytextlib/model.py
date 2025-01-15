# mytextlib/model.py
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

class MyTextModel:
    def __init__(self, model_dir="./model_files"):
        """
        Initialize the model and tokenizer from the specified directory.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        self.pipeline = pipeline("text-classification", model=self.model, tokenizer=self.tokenizer, max_length=512, truncation=True)

    def analyze_sentiment(self, text):
        """
        Analyze sentiment for the input text.
        """
        return self.pipeline(text)