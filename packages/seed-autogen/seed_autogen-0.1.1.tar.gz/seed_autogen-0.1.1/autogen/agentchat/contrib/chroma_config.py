from chromadb.config import Settings

# Global ChromaDB settings
settings = Settings(
    anonymized_telemetry=False,
    allow_reset=True,
    is_persistent=True,
    persist_directory="chromadb_data"
)
