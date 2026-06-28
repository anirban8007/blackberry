import sqlite3, hashlib, os
from datetime import datetime
import config

DB_PATH = os.path.join(config.BASE, f"{config.DEVICE}_mem.db")
MERGED  = os.path.join(config.BASE, "merged_mem.db")

# ── SQLite ─────────────────────────────────────────────────────────────────

def _conn(path=None):
    path = path or DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    db = sqlite3.connect(path)
    db.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id        TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            source    TEXT NOT NULL,
            role      TEXT NOT NULL,
            content   TEXT NOT NULL
        )
    """)
    db.commit()
    return db


def save(role: str, content: str):
    """Save a conversation turn to this device's local DB."""
    uid = hashlib.md5(
        (content + datetime.now().isoformat()).encode()
    ).hexdigest()
    db = _conn()
    db.execute(
        "INSERT OR IGNORE INTO conversations VALUES (?,?,?,?,?)",
        (uid, datetime.now().isoformat(), config.DEVICE, role, content)
    )
    db.commit()
    db.close()

    # Also store in ChromaDB for semantic search
    try:
        _chroma_save(uid, content)
    except Exception as e:
        print(f"[MEM] ChromaDB save skipped: {e}")


def get_recent(limit: int = 5) -> list[str]:
    """Get most recent conversations from merged DB (or local if no merge yet)."""
    path = MERGED if os.path.exists(MERGED) else DB_PATH
    if not os.path.exists(path):
        return []
    db   = _conn(path)
    rows = db.execute(
        "SELECT role, content FROM conversations ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    ).fetchall()
    db.close()
    return [f"{r[0]}: {r[1]}" for r in reversed(rows)]


# ── ChromaDB ───────────────────────────────────────────────────────────────

_chroma_col = None

def _get_col():
    global _chroma_col
    if _chroma_col is None:
        import chromadb
        client      = chromadb.PersistentClient(
            path=os.path.join(config.BASE, "chroma")
        )
        _chroma_col = client.get_or_create_collection("blackberry_memory")
    return _chroma_col


def _chroma_save(uid: str, text: str):
    _get_col().add(documents=[text], ids=[uid])


def get_context(query: str) -> str:
    """Semantic search — find memories most relevant to current command."""
    try:
        results = _get_col().query(
            query_texts=[query],
            n_results=config.MEMORY_TOP_K
        )
        docs = results.get("documents", [[]])[0]
        if docs:
            return "\n".join(docs)
    except Exception as e:
        print(f"[MEM] Context fetch skipped: {e}")

    # Fallback to recent conversations if ChromaDB empty
    recent = get_recent(5)
    return "\n".join(recent) if recent else "No memory yet."
