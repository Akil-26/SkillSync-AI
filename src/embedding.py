"""
Embedding utilities using a local, CPU-friendly sentence-transformers model.

Design notes:
- precompute.py (offline stage) may download the model from the hub the
  FIRST time this project is set up, then it gets cached to
  config.EMBEDDING_MODEL_LOCAL_PATH.
- rank.py (the actual timed/no-network ranking run) must load ONLY from
  that local path, never touch the hub.
"""

from __future__ import annotations

# pyrefly: ignore [missing-import]
import numpy as np

from . import config
from .utils import get_logger

logger = get_logger(__name__)

_model = None  # lazy singleton


def _load_model(allow_download: bool = False):
    """Load (and cache) the sentence-transformers model.

    Args:
        allow_download: if True and no local cache exists, download from the
            hub (only ever True during precompute/setup, never during rank.py).
    """
    global _model
    if _model is not None:
        return _model

    # pyrefly: ignore [missing-import]
    from sentence_transformers import SentenceTransformer

    local_path = config.EMBEDDING_MODEL_LOCAL_PATH
    if local_path.exists():
        logger.info(f"Loading embedding model from local cache: {local_path}")
        _model = SentenceTransformer(str(local_path), device="cpu")
    elif allow_download:
        logger.warning(
            f"No local model cache found at {local_path}. Downloading "
            f"{config.EMBEDDING_MODEL_NAME} from the hub (setup-time only)."
        )
        _model = SentenceTransformer(config.EMBEDDING_MODEL_NAME, device="cpu")
        local_path.parent.mkdir(parents=True, exist_ok=True)
        _model.save(str(local_path))
        logger.info(f"Model cached locally at {local_path}")
    else:
        raise FileNotFoundError(
            f"Embedding model not found at {local_path} and downloading is "
            f"disabled (no-network constraint). Run precompute.py's setup "
            f"step once with network access to populate this cache."
        )

    return _model


def encode_texts(
    texts: list[str],
    allow_download: bool = False,
    batch_size: int | None = None,
    show_progress: bool = True,
) -> np.ndarray:
    """Encode a list of texts into an (N, EMBEDDING_DIM) float32 array."""
    if not texts:
        return np.zeros((0, config.EMBEDDING_DIM), dtype=np.float32)

    model = _load_model(allow_download=allow_download)
    batch_size = batch_size or config.EMBEDDING_BATCH_SIZE

    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=show_progress,
        convert_to_numpy=True,
        normalize_embeddings=True,  # so dot product == cosine similarity
    )
    return embeddings.astype(np.float32)


def cosine_similarity_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Cosine similarity between rows of a and rows of b.

    Assumes embeddings are already L2-normalized (encode_texts does this).
    If b is a single vector of shape (D,), returns shape (N,).
    """
    if b.ndim == 1:
        return a @ b
    return a @ b.T


def save_embeddings(embeddings: np.ndarray, ids: list[str], emb_path, ids_path) -> None:
    from .utils import write_json

    emb_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(emb_path, embeddings)
    write_json(ids_path, ids)


def load_embeddings(emb_path, ids_path) -> tuple[np.ndarray, list[str]]:
    from .utils import read_json

    embeddings = np.load(emb_path)
    ids = read_json(ids_path)
    return embeddings, ids