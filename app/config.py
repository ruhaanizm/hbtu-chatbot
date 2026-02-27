import os
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME")
EMBED_MODEL = os.getenv("EMBED_MODEL")
TOP_K = int(os.getenv("TOP_K", 5))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.3))

INDEX_DIR = "data/index"