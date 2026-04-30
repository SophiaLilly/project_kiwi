# vector_db.py
# Vector database for semantic memory storage and retrieval
# big TODO in this boi
# Local Imports

# Partial Imports
from chromadb.config import Settings
from datetime import datetime
from typing import List

# Full Imports
import chromadb
import threading
import uuid


_collection = None
_client = None
_cache_lock = threading.RLock()
_initialized = False

_config_cache = None

_embedding_model = None
_embedding_model_name = None



def _get_cached_config():
    from modules.llm_funcs import get_char_config_file
    global _config_cache
    if _config_cache is None:
        _config_cache = get_char_config_file()
    return _config_cache


def _get_vector_db_config() -> dict:
    config = _get_cached_config()
    return config.get('vector_db', {
        'enabled': True,
        'persist_directory': '/home/elodie/Projects/project_kiwi/vector_memory',
        'collection_name': 'semantic_memory',
        'embedding_model': 'all-MiniLM-L6-v2',
        'max_results': 5,
    })


def get_client():
    global _client
    with _cache_lock:
        if _client is None:
            db_config = _get_vector_db_config()
            persist_dir = db_config.get('persist_directory', './vector_memory')

            _client = chromadb.PersistentClient(
                path=persist_dir,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                )
            )
        return _client


def get_collection():
    global _collection
    with _cache_lock:
        if _collection is None:
            db_config = _get_vector_db_config()
            collection_name = db_config.get('collection_name', 'semantic_memory')
            client = get_client()

            try:
                _collection = client.get_collection(name=collection_name)
            except Exception:
                _collection = client.create_collection(
                    name=collection_name,
                    metadata={"description": "Semantic memory for LLM context enhancement"}
                )
        return _collection


def is_enabled() -> bool:
    try:
        db_config = _get_vector_db_config()
        return db_config.get('enabled', True)
    except Exception:
        return False


def _get_embedding_model():
    global _embedding_model, _embedding_model_name

    with _cache_lock:
        if _embedding_model is None:
            try:
                from sentence_transformers import SentenceTransformer

                db_config = _get_vector_db_config()
                model_name = db_config.get('embedding_model', 'all-MiniLM-L6-v2')

                print(f"Loading embedding model: {model_name}")
                _embedding_model = SentenceTransformer(model_name)
                _embedding_model_name = model_name
                print(f"Embedding model loaded successfully")

            except ImportError:
                raise ImportError(
                    "sentence-transformers is required for vector database functionality. "
                    "Install with: pip install sentence-transformers"
                )

        return _embedding_model, _embedding_model_name


def _create_embedding(text: str) -> List[float]:
    model, _ = _get_embedding_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def _format_message_for_vector(
        role: str,
        name: str,
        user_id: int,
        content: str,
        timestamp: str = None
) -> dict:

    if timestamp is None:
        timestamp = str(datetime.now())

    return {
        "role": role,
        "name": name,
        "user_id": user_id,
        "content": content,
        "timestamp": timestamp,
        "text": f"[{role}] {name}: {content}",  # Flattened text for embedding
    }


def store_vector_memory(memory, user_id) -> None:
    if not is_enabled() or not memory or memory == "NONE":
        return

    add_memory(
        role="memory",
        name="system",
        user_id=user_id,
        content=memory
    )


def add_memory(
        role: str,
        name: str,
        user_id: int,
        content: str,
        timestamp: str = None,
        metadata: dict = None
) -> str:

    if not is_enabled():
        return None

    try:
        message_data = _format_message_for_vector(
            role=role,
            name=name,
            user_id=user_id,
            content=content,
            timestamp=timestamp
        )

        if metadata:
            message_data.update(metadata)

        collection = get_collection()
        memory_id = str(uuid.uuid4())

        embedding_text = message_data["text"]
        embedding = _create_embedding(embedding_text)

        collection.add(
            ids=[memory_id],
            embeddings=[embedding],
            documents=[embedding_text],
            metadatas=[message_data]
        )

        return memory_id
    except Exception as e:
        print(f"Error adding memory to vector DB: {e}")
        return None


def add_memories_batch(messages: List[dict]) -> List[str]:

    if not is_enabled() or not messages:
        return []

    try:
        collection = get_collection()
        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for msg in messages:
            message_data = _format_message_for_vector(
                role=msg.get('role', 'user'),
                name=msg.get('name', 'Unknown'),
                user_id=msg.get('user_id', 0),
                content=msg.get('content', ''),
                timestamp=msg.get('timestamp')
            )

            if 'metadata' in msg:
                message_data.update(msg['metadata'])

            memory_id = str(uuid.uuid4())
            embedding_text = message_data["text"]

            ids.append(memory_id)
            embeddings.append(_create_embedding(embedding_text))
            documents.append(embedding_text)
            metadatas.append(message_data)

        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

        return ids
    except Exception as e:
        print(f"Error adding memories batch to vector DB: {e}")
        return []


def search_memories(
        query: str,
        n_results: int = None,
        where: dict = None,
        where_document: dict = None
) -> List[dict]:

    if not is_enabled():
        return []

    try:
        db_config = _get_vector_db_config()
        if n_results is None:
            n_results = db_config.get('max_results', 5)

        collection = get_collection()

        query_embedding = _create_embedding(query)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            where_document=where_document,
            include=["documents", "metadatas", "distances"]
        )

        memories = []
        if results and results.get('ids') and results['ids'][0]:
            for i, memory_id in enumerate(results['ids'][0]):
                memories.append({
                    "id": memory_id,
                    "content": results['documents'][0][i] if results.get('documents') else None,
                    "metadata": results['metadatas'][0][i] if results.get('metadatas') else None,
                    "distance": results['distances'][0][i] if results.get('distances') else None,
                    "relevance_score": 1 - results['distances'][0][i] if results.get('distances') else None,
                })

        return memories
    except Exception as e:
        print(f"Error searching vector DB: {e}")
        return []


def get_recent_memories(
        limit: int = 10,
        role: str = None,
        user_id: int = None
) -> List[dict]:

    if not is_enabled():
        return []

    try:
        collection = get_collection()

        where_filter = {}
        if role:
            where_filter["role"] = role
        if user_id is not None:
            where_filter["user_id"] = user_id

        results = collection.get(
            where=where_filter if where_filter else None,
            limit=limit,
            include=["documents", "metadatas"]
        )

        memories = []
        if results and results.get('ids'):
            for i, memory_id in enumerate(results['ids']):
                memories.append({
                    "id": memory_id,
                    "content": results['documents'][i] if results.get('documents') else None,
                    "metadata": results['metadatas'][i] if results.get('metadatas') else None,
                })

        return memories
    except Exception as e:
        print(f"Error getting recent memories from vector DB: {e}")
        return []


def get_context_for_query(query: str, max_memories: int = 5) -> List[str]:
    memories = search_memories(query, n_results=max_memories)
    context_strings = []

    for memory in memories:
        if memory.get('metadata'):
            meta = memory['metadata']
            role = meta.get('role', 'unknown')
            name = meta.get('name', 'Unknown')
            content = meta.get('content', '')
            context_strings.append(f"[{role}] {name}: {content}")

    return context_strings


def delete_memory(memory_id: str) -> bool:
    if not is_enabled():
        return False

    try:
        collection = get_collection()
        collection.delete(ids=[memory_id])
        return True
    except Exception as e:
        print(f"Error deleting memory from vector DB: {e}")
        return False


def delete_memories_by_filter(where: dict) -> int:
    if not is_enabled():
        return 0

    try:
        collection = get_collection()
        results = collection.get(where=where)

        if results and results.get('ids'):
            ids = results['ids']
            collection.delete(ids=ids)
            return len(ids)
        return 0
    except Exception as e:
        print(f"Error deleting memories by filter from vector DB: {e}")
        return 0


def clear_all_memories() -> bool:
    if not is_enabled():
        return False

    try:
        collection = get_collection()
        collection.delete(where={})  # Delete all
        return True
    except Exception as e:
        print(f"Error clearing all memories from vector DB: {e}")
        return False


def get_memory_count() -> int:
    if not is_enabled():
        return 0

    try:
        collection = get_collection()
        return collection.count()
    except Exception as e:
        print(f"Error getting memory count from vector DB: {e}")
        return 0


def sync_from_json_history(json_messages: List[dict]) -> int:
    if not is_enabled():
        return 0

    messages_to_sync = [
        msg for msg in json_messages
        if msg.get('role') in ('user', 'assistant')
    ]

    if not messages_to_sync:
        return 0

    ids = add_memories_batch(messages_to_sync)
    return len(ids)


def reset_vector_db() -> bool:
    global _collection, _client

    try:
        client = get_client()
        db_config = _get_vector_db_config()
        collection_name = db_config.get('collection_name', 'semantic_memory')

        try:
            client.delete_collection(name=collection_name)
        except Exception:
            pass

        with _cache_lock:
            _collection = None
            _client = None

        return True
    except Exception as e:
        print(f"Error resetting vector DB: {e}")
        return False


def clear_cache():
    global _config_cache, _collection, _client, _initialized

    with _cache_lock:
        _config_cache = None
        _collection = None
        _client = None
        _initialized = False


def get_augmented_messages(
        user_message: dict,
        semantic_context: bool = True,
        topic_context: str = None,
        max_semantic_results: int = 5
) -> List[dict]:

    from modules.memory.memory import get_system_message, get_working_memory

    messages = [get_system_message()]

    recent_memories = get_working_memory()
    messages.extend(recent_memories)

    if semantic_context and is_enabled():
        query = topic_context or user_message.get('content', '')

        if ':' in query:
            parts = query.split(':', 1)
            if len(parts) > 1:
                query = parts[1].strip()

        semantic_contexts = get_context_for_query(query, max_semantic_results)

        if semantic_contexts:
            context_text = "Relevant past context:\n" + "\n".join(semantic_contexts)
            messages.append({
                "role": "system",
                "content": context_text
            })

    content = user_message.get('content', '')
    current_name = content.split(":")[0] if ":" in content else "Unknown"

    messages.append({
        "role": "system",
        "content": f"Current speaker: {current_name}"
    })

    messages.append(user_message)

    return messages


if __name__ == "__main__":
    print("Running vector_db as main. Is this intended?")
    reset_vector_db()