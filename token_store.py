"""
Token Storage Management Module

Handles the persistent storage and retrieval of various types of tokens
(Instagram business tokens, persona tokens, etc.) in a JSON file.
"""

import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
import requests
from config import GRAPH_API_VERSION

TOKEN_FILE = Path("tokens.json")

class TokenStore:
    def __init__(self):
        self.token_file = TOKEN_FILE
        self._ensure_token_file()

    def _ensure_token_file(self):
        """Ensure the token file exists with proper structure."""
        if not self.token_file.exists():
            self.token_file.write_text(json.dumps({
                "business_token": None,
                "persona_tokens": {},
                "last_updated": None
            }, indent=4))

    def _load_tokens(self) -> Dict[str, Any]:
        """Load all tokens from the file."""
        with open(self.token_file) as f:
            return json.load(f)

    def _save_tokens(self, data: Dict[str, Any]):
        """Save tokens to the file."""
        # Time is formatted as "YYYY-MM-DD HH:MM:SS", e.g. "2024-03-08 14:30:25"
        data["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open(self.token_file, "w") as f:
            json.dump(data, f, indent=4)

    def get_business_token(self) -> Optional[str]:
        """Get the Instagram business token."""
        data = self._load_tokens()
        return data.get("business_token")

    def save_business_token(self, token: str):
        """Save the Instagram business token."""
        data = self._load_tokens()
        data["business_token"] = token
        self._save_tokens(data)

    def get_persona_token(self, persona_name: str) -> Optional[str]:
        """Get a specific persona's token."""
        data = self._load_tokens()
        persona_data = data.get("persona_tokens", {}).get(persona_name)
        
        if persona_data:
            access_token = persona_data.get("access_token")
            if access_token and not self.is_token_expired(access_token):
                return access_token
            
            # 如果访问令牌不可用或已过期，尝试重新生成
            if "auth_code" in persona_data:
                print(f"Access token for {persona_name} is not available or expired. Attempting to regenerate.")
                try:
                    # 使用 fb_page_id 和 ig_user_id 生成新的访问令牌
                    self.token_manager.generate_or_regenerate_access_tokens_for_users(persona_data["fb_page_id"], persona_data["ig_user_id"])
                    
                    # 重新加载令牌
                    return self.get_persona_token(persona_name)
                except Exception as e:
                    print(f"Error regenerating token for {persona_name}: {e}")
        
        return None

    def save_persona_token(self, persona_name: str, access_token: str, expires_at: Optional[str] = None):
        """Save a persona's token with optional expiration."""
        data = self._load_tokens()
        if "persona_tokens" not in data:
            data["persona_tokens"] = {}
        
        data["persona_tokens"][persona_name] = {
            "access_token": access_token,
            "expires_at": expires_at,
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }
        self._save_tokens(data)

    def get_all_persona_tokens(self) -> Dict[str, Dict[str, Any]]:
        """Get all persona tokens."""
        data = self._load_tokens()
        return data.get("persona_tokens", {})

    def delete_persona_token(self, persona_name: str):
        """Delete a specific persona's token."""
        data = self._load_tokens()
        if "persona_tokens" in data and persona_name in data["persona_tokens"]:
            del data["persona_tokens"][persona_name]
            self._save_tokens(data)

    def clear_all_tokens(self):
        """Clear all stored tokens."""
        self._save_tokens({
            "business_token": None,
            "persona_tokens": {},
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        })

    def is_token_expired(self, token):
        """
        Check if a token is expired or about to expire (within 24 hours).
        """
        try:
            url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/debug_token"
            params = {
                "input_token": token,
                "access_token": f"{self.app_id}|{self.app_secret}"
            }
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                return True
            
            data = response.json()
            expires_at = data.get("data", {}).get("expires_at", 0)
            
            # Consider token expired if it has less than 24 hours left
            return time.time() > (expires_at - 86400)
            
        except Exception:
            return True
