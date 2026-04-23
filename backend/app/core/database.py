"""
RentWiz – Supabase Database Client
Provides a singleton Supabase client for use across the app.
"""
from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

_supabase_client: Client | None = None


def get_supabase() -> Client:
    """Return (or lazily initialise) the global Supabase client."""
    global _supabase_client
    if _supabase_client is None:
        try:
            _supabase_client = create_client(
                settings.supabase_url,
                settings.supabase_service_key,
            )
            logger.info("✅ Supabase client initialised")
        except Exception as e:
            logger.error(f"❌ Failed to init Supabase: {e}")
            raise
    return _supabase_client
