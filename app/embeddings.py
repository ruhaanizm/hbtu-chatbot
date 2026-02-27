from sentence_transformers import SentenceTransformer
from app.config import EMBED_MODEL

_model = None


def get_embedding_model():
    global _model

    if _model is None:
        print("Loading embedding model...")
        _model = SentenceTransformer(EMBED_MODEL)

    return _model


def embed_query(query: str):
    model = get_embedding_model()

    embedding = model.encode(
        [query],
        normalize_embeddings=True
    )

    return embedding