import sqlite3
import json
from typing import List, Dict, Optional
import os
import logging
import secrets
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class PersonaNotFoundError(Exception):
    pass

class InvalidAPIKeyError(Exception):
    pass

class PersonaDB:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.getenv('DATABASE_PATH', '/app/data/mavera.db')
        logger.debug(f"Initializing database with path: {self.db_path}")
        self._init_db()
    
    def _init_db(self):
        logger.debug("Creating database tables if they don't exist")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Personas table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS personas (
                name TEXT PRIMARY KEY,
                system_prompt JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # API keys table with `is_admin` column added
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                key TEXT PRIMARY KEY,
                user_name TEXT NOT NULL,
                email TEXT NOT NULL,
                active BOOLEAN DEFAULT true,
                request_count INTEGER DEFAULT 0,
                daily_limit INTEGER DEFAULT 1000,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used_at TIMESTAMP,
                is_admin BOOLEAN DEFAULT false
            )
        """)
        
        # Usage tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key TEXT NOT NULL,
                persona TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (api_key) REFERENCES api_keys (key),
                FOREIGN KEY (persona) REFERENCES personas (name)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_persona(self, name: str, prompt_data: list):
        logger.debug(f"Adding persona: {name}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        prompt_json = json.dumps(prompt_data)
        
        cursor.execute(
            "INSERT OR REPLACE INTO personas (name, system_prompt) VALUES (?, ?)",
            (name, prompt_json)
        )
        
        conn.commit()
        conn.close()
        logger.debug(f"Successfully added persona: {name}")
    
    def get_persona(self, name: str) -> Optional[Dict]:
        """Get a persona's system prompt data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT system_prompt FROM personas WHERE name = ?", (name,))
        result = cursor.fetchone()
        conn.close()
        return json.loads(result[0]) if result else None

    def update_persona(self, name: str, prompt_data: list):
        """Update an existing persona or add if it doesn't exist."""
        existing_persona = self.get_persona(name)
        if existing_persona:
            logger.debug(f"Updating persona: {name}")
            self.add_persona(name, prompt_data)
        else:
            logger.debug(f"Persona not found, adding as new: {name}")
            self.add_persona(name, prompt_data)

    def get_system_prompt(self, persona: str) -> str:
        logger.debug(f"Getting system prompt for persona: {persona}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT system_prompt FROM personas WHERE name = ?",
            (persona,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            logger.error(f"Persona not found: {persona}")
            raise PersonaNotFoundError(f"Persona '{persona}' not found")
        
        prompts = json.loads(result[0])
        logger.debug(f"Found prompt for persona: {persona}")
        return prompts[0]['text'] if prompts else ""

    def create_api_key(self, user_name: str, email: str, daily_limit: int = 1000, is_admin: bool = False) -> str:
        """Create a new API key"""
        api_key = f"mk-{secrets.token_urlsafe(32)}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO api_keys (key, user_name, email, daily_limit, is_admin) VALUES (?, ?, ?, ?, ?)",
            (api_key, user_name, email, daily_limit, is_admin)
        )
        
        conn.commit()
        conn.close()
        
        logger.debug(f"Created new API key for user: {user_name} (Admin: {is_admin})")
        return api_key

    def validate_api_key(self, api_key: str) -> bool:
        """Validate an API key and check usage limits"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT active, request_count, daily_limit 
            FROM api_keys 
            WHERE key = ?
            """,
            (api_key,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            raise InvalidAPIKeyError("Invalid API key")
            
        active, request_count, daily_limit = result
        
        if not active:
            raise InvalidAPIKeyError("API key is inactive")
            
        if request_count >= daily_limit:
            raise InvalidAPIKeyError("Daily limit exceeded")
            
        return True

    def is_admin(self, api_key: str) -> bool:
        """Check if an API key belongs to an admin user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT is_admin FROM api_keys WHERE key = ?",
            (api_key,)
        )
        result = cursor.fetchone()
        conn.close()
        if not result:
            raise InvalidAPIKeyError("Invalid API key")
        return result[0]  # True if admin, False otherwise

    def increment_usage(self, api_key: str, persona: str):
        """Track API usage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update request count and last used timestamp
        cursor.execute(
            """
            UPDATE api_keys 
            SET request_count = request_count + 1,
                last_used_at = CURRENT_TIMESTAMP
            WHERE key = ?
            """,
            (api_key,)
        )
        
        # Log the usage
        cursor.execute(
            "INSERT INTO usage_logs (api_key, persona) VALUES (?, ?)",
            (api_key, persona)
        )
        
        conn.commit()
        conn.close()

    def get_usage_stats(self, api_key: str) -> Dict:
        """Get usage statistics for an API key"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT request_count, daily_limit, created_at, last_used_at
            FROM api_keys
            WHERE key = ?
            """,
            (api_key,)
        )
        
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            raise InvalidAPIKeyError("Invalid API key")
            
        request_count, daily_limit, created_at, last_used_at = result
        
        # Get persona usage breakdown
        cursor.execute(
            """
            SELECT persona, COUNT(*) as count
            FROM usage_logs
            WHERE api_key = ?
            GROUP BY persona
            """,
            (api_key,)
        )
        
        persona_usage = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            "request_count": request_count,
            "daily_limit": daily_limit,
            "created_at": created_at,
            "last_used_at": last_used_at,
            "persona_usage": persona_usage
        }

    def reset_daily_counts(self):
        """Reset all daily request counts to zero"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE api_keys SET request_count = 0")
        
        conn.commit()
        conn.close()
        
        logger.debug("Reset all daily request counts")
