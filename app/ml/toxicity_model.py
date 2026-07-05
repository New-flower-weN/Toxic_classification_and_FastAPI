import joblib
import nltk
import re
from typing import Dict, List, Union
from pathlib import Path
from nltk.corpus import stopwords

nltk.download('stopwords')
stop = set(stopwords.words('english'))

class ToxicityModel:
    def __init__(self, model_path: str, vectorizer_path: str = None):
        self.model_path = Path(model_path)
        self.vectorizer_path = Path(vectorizer_path) if vectorizer_path else None
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found at {self.model_path}")
        
        self.model = joblib.load(self.model_path)
    
    def predict_single(self, text: str) -> Dict[str, Union[float, bool]]:
        if not text or not text.strip():
            return {
                'is_toxic': False,
                'toxicity_score': 0.0,
                'confidence': 1.0
            }
        
        text = ' '.join([word for word in str(text).split() if word.lower() not in stop])
        text = re.sub(r'[^\w\s]', '', text).lower()
        text = re.sub(r'\s+', ' ', text).strip()

        # Получаем предсказание
        try:
            # Для бинарной классификации
            if hasattr(self.model, 'predict_proba'):
                probability = self.model.predict_proba([text])[0]
                # Предполагаем, что класс 1 — это токсичный
                toxicity_score = float(probability[1])
                is_toxic = toxicity_score > 0.8
                confidence = max(probability)
            else:
                # Если только predict
                prediction = self.model.predict([text])[0]
                is_toxic = bool(prediction)
                toxicity_score = 1.0 if is_toxic else 0.0
                confidence = 1.0
        except Exception as e:
            print(f"Prediction error: {e}")
            return {
                'is_toxic': False,
                'toxicity_score': 0.0,
                'confidence': 0.0
            }
        
        return {
            'is_toxic': is_toxic,
            'toxicity_score': toxicity_score,
            'confidence': confidence
        }
    
    def predict_batch(self, texts: List[str]) -> List[Dict]:
        """Проверяет список текстов на токсичность"""
        return [self.predict_single(text) for text in texts]
    
    def is_toxic(self, text: str, threshold: float = 0.5) -> bool:
        """Быстрая проверка на токсичность"""
        return self.predict_single(text)['is_toxic']