"""
Supabase client utility for database and authentication operations.
Provides centralized access to Supabase services.
"""

from supabase import create_client, Client
from app.core.config import get_supabase_url, get_supabase_anon_key, get_supabase_service_key

# Global Supabase client instances
_supabase_client: Client = None
_supabase_admin_client: Client = None

def get_supabase_client() -> Client:
    """
    Get the Supabase client instance for regular operations.
    Uses the anonymous key for client-side operations.
    """
    global _supabase_client
    
    if _supabase_client is None:
        url = get_supabase_url()
        key = get_supabase_anon_key()
        
        if not url or not key:
            raise ValueError("Supabase URL and anonymous key must be configured")
        
        _supabase_client = create_client(url, key)
    
    return _supabase_client

def get_supabase_admin_client() -> Client:
    """
    Get the Supabase admin client instance for server-side operations.
    Uses the service role key for administrative operations.
    """
    global _supabase_admin_client
    
    if _supabase_admin_client is None:
        url = get_supabase_url()
        key = get_supabase_service_key()
        
        if not url or not key:
            raise ValueError("Supabase URL and service role key must be configured")
        
        _supabase_admin_client = create_client(url, key)
    
    return _supabase_admin_client

def get_auth_client():
    """
    Get the Supabase auth client for authentication operations.
    """
    return get_supabase_client().auth

def get_database_client():
    """
    Get the Supabase database client for database operations.
    """
    return get_supabase_client().table

def get_storage_client():
    """
    Get the Supabase storage client for file operations.
    """
    return get_supabase_client().storage
