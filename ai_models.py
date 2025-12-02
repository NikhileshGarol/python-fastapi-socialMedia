# ai_models.py
from transformers import pipeline

# sentiment_analyzer = pipeline("sentiment-analysis")
# summarizer = pipeline("summarization")
# Initialize pipelines (runs on CPU by default)
# summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
sentiment_analyzer = pipeline(
    "sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
