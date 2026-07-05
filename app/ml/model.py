from ..config import settings
from .toxicity_model import ToxicityModel

toxicity_model=ToxicityModel(settings.model_path)
