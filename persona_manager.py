# persona_manager.py
import json
from token_manager import TokenManager

class PersonaManager:
    def __init__(self, persona_file="personas.json"):
        self.persona_file = persona_file
        self.personas = self.load_personas()
        self.token_manager = TokenManager()  # NEW: to retrieve tokens for personas

    def load_personas(self):
        with open(self.persona_file, "r") as f:
            return json.load(f)

    def save_personas(self):
        with open(self.persona_file, "w") as f:
            json.dump(self.personas, f, indent=4)

    def get_persona(self, name):
        return self.personas.get(name)

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
            # If the persona has provided an auth_code but lacks an access_token,
            # retrieve the tokens.
            if "auth_code" in persona_data and not persona_data.get("access_token"):
                print(f"Retrieving tokens for persona: {persona_name}")
                try:
                    short_token, long_token = self.token_manager.get_user_tokens(persona_data["auth_code"])
                    # Save the long-lived token for future API calls
                    persona_data["access_token"] = long_token
                    updated = True
                except Exception as e:
                    print(f"Error retrieving token for {persona_name}: {e}")
        # Save the updated personas back to file if any tokens were updated
        if updated:
            self.save_personas()
