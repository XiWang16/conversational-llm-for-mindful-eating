# persona_manager.py
import json
from token_manager import TokenManager
from token_store import TokenStore
from config import PERSONA_FILE

class PersonaManager:
    def __init__(self, persona_file=PERSONA_FILE):
        self.persona_file = persona_file
        self.token_manager = TokenManager()
        self.token_store = TokenStore()
        self.personas = self.load_personas()

    def load_personas(self):
        with open(self.persona_file, "r") as f:
            personas = json.load(f)
            # Load tokens from token store
            stored_tokens = self.token_store.get_all_persona_tokens()
            for name, data in personas.items():
                if name in stored_tokens:
                    data["access_token"] = stored_tokens[name]["access_token"]
            return personas

    def save_personas(self):
        # Save basic persona data
        with open(self.persona_file, "w") as f:
            # Remove access tokens before saving to persona file
            personas_without_tokens = {
                name: {k: v for k, v in data.items() if k != "access_token"}
                for name, data in self.personas.items()
            }
            json.dump(personas_without_tokens, f, indent=4)
        
        # Save tokens separately in token store
        for name, data in self.personas.items():
            if "access_token" in data:
                self.token_store.save_persona_token(name, data["access_token"])

    def get_persona(self, name):
        persona = self.personas.get(name)
        if persona:
            # 尝试从 token store 获取令牌
            token = self.token_store.get_persona_token(name)
            if token:
                persona["access_token"] = token
            else:
                # 如果令牌不可用，尝试重新生成
                if "auth_code" in persona:
                    print(f"Access token for {name} is not available or expired. Attempting to regenerate.")
                    try:
                        short_token, long_token = self.token_manager.get_user_tokens(persona["auth_code"])
                        persona["access_token"] = long_token
                        self.token_store.save_persona_token(name, long_token)
                    except Exception as e:
                        print(f"Error regenerating token for {name}: {e}")
        return persona

    def get_all_personas(self):
        return self.personas.keys()

    async def schedule_comment(self, delay_minutes, coro):
        """
        Schedule a coroutine to run after delay_minutes.
        """
        import asyncio
        await asyncio.sleep(delay_minutes * 60)
        await coro

    def retrieve_tokens_for_persona(self):
        """
        For each persona that has an 'auth_code' but does not yet have an 'access_token',
        retrieve the tokens using token_manager and update the persona's config.
        """
        updated = False
        for persona_name, persona_data in self.personas.items():
            # Check token store first
            stored_token = self.token_store.get_persona_token(persona_name)
            if stored_token:
                persona_data["access_token"] = stored_token
                continue

            # If no stored token but has auth_code, get new tokens
            if "auth_code" in persona_data and not persona_data.get("access_token"):
                print(f"Retrieving tokens for persona: {persona_name}")
                try:
                    short_token, long_token = self.token_manager.get_user_tokens(persona_data["auth_code"])
                    # Save the long-lived token
                    persona_data["access_token"] = long_token
                    self.token_store.save_persona_token(persona_name, long_token)
                    updated = True
                except Exception as e:
                    print(f"Error retrieving token for {persona_name}: {e}")
        
        # Save the updated personas if any tokens were updated
        if updated:
            self.save_personas()

    def get_fb_page_name(self, persona_name):
        persona = self.personas.get(persona_name)
        return persona.get("FB Page Name") if persona else None

    def get_fb_page_id(self, persona_name):
        persona = self.personas.get(persona_name)
        return persona.get("FB Page ID") if persona else None

    def get_ig_user_id(self, persona_name):
        persona = self.personas.get(persona_name)
        return persona.get("IG_USER_ID") if persona else None
