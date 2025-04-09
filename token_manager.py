import requests
from config import (
    INSTAGRAM_APP_ID,
    INSTAGRAM_APP_SECRET,
    INSTAGRAM_REDIRECT_URI,
    GRAPH_API_VERSION
)
from token_store import TokenStore

class TokenManager:
    def __init__(self):
        # Initialize token store
        self.token_store = TokenStore()
        
        # Credentials for performing OAuth exchanges for user tokens
        self.app_id = INSTAGRAM_APP_ID
        self.app_secret = INSTAGRAM_APP_SECRET
        self.redirect_uri = INSTAGRAM_REDIRECT_URI
        
        # Validate required configuration
        if not self.app_id:
            raise Exception("Missing required configuration: INSTAGRAM_APP_ID")
        if not self.app_secret:
            raise Exception("Missing required configuration: INSTAGRAM_APP_SECRET")

    def get_instagram_business_token(self):
        """
        Get the Instagram Business Access Token, refreshing if necessary.
        """
        try:
            # Get token from store
            business_token = self.token_store.get_business_token()
            
            if not business_token:
                print("No existing token found, getting new token...")
                return self.refresh_token()
            
            # Try to validate token
            try:
                url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/me"
                params = {
                    "access_token": business_token,
                    "fields": "id,name"
                }
                response = requests.get(url, params=params)
                
                if response.status_code == 200:
                    return business_token
                
            except Exception as e:
                print(f"Token validation failed: {e}")
            
            # If we get here, token is invalid or expired
            print("Token is invalid or expired, refreshing...")
            return self.refresh_token()
            
        except Exception as e:
            print(f"Error getting business token: {e}")
            raise

    def get_short_lived_token(self, auth_code=None):
        """
        Exchanges an auth code for a short-lived access token.
        If auth_code is None, uses client_credentials grant type.
        """
        url = "https://api.instagram.com/oauth/access_token"
        data = {
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "grant_type": "authorization_code" if auth_code else "client_credentials",
            "redirect_uri": self.redirect_uri if auth_code else None,
            "code": auth_code
        }
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        
        response = requests.post(url, data=data)
        if response.status_code != 200:
            raise Exception(f"Error obtaining short-lived token: {response.text}")
        token_data = response.json()
        return token_data.get("access_token")

    def exchange_short_lived_token(self, short_lived_token):
        """
        Exchanges a short-lived token for a long-lived token.
        """
        url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "fb_exchange_token": short_lived_token
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Error exchanging token: {response.text}")
        token_data = response.json()
        return token_data.get("access_token")

    def get_user_tokens(self, auth_code):
        """
        Retrieves both short-lived and long-lived tokens for a user/persona.
        Expects an auth code (obtained via the OAuth flow) as input.
        Returns a tuple: (short_lived_token, long_lived_token)
        """
        short_lived_token = self.get_short_lived_token(auth_code)
        long_lived_token = self.exchange_short_lived_token(short_lived_token)
        return short_lived_token, long_lived_token

    def refresh_token(self):
        """
        Refresh the Instagram Business Access Token using the current long-lived token.
        This method assumes that a valid current token exists in the token store.
        
        If no current token is found, the method raises an exception to indicate that 
        re-authentication via OAuth is needed.
        """
        try:
            # Get current business token from token store
            current_token = self.token_store.get_business_token()
            if not current_token:
                raise Exception("No current business access token available. Please authenticate first.")

            print("Attempting to refresh Instagram Business access token using current token...")
            
            # Use the Graph API endpoint to refresh the token.
            # We call exchange_short_lived_token() with the current token because the endpoint is the same for both exchanging and refreshing.
            new_token = self.exchange_short_lived_token(current_token)
            if not new_token:
                raise Exception("No long-lived token received in response")
            
            print("Successfully refreshed the token.")
            # Save the new token back to the token store (and update timestamp, if desired)
            self.token_store.save_business_token(new_token)
            print("New token saved to tokens.json.")

            return new_token

        except Exception as e:
            print(f"Error in refresh_token: {e}")
            raise Exception("Failed to refresh Instagram access token. Please check your app credentials and token validity.")

    def generate_or_regenerate_access_tokens_for_users(self, fb_page_id, ig_user_id):
        """
        Generate or regenerate access tokens for the specified Facebook page and Instagram user.
        """
        try:
            # Step 1: Get short-lived token for the Facebook page
            short_lived_token = self.get_short_lived_token(auth_code=None)  # 使用 client_credentials 获取短期令牌
            
            if not short_lived_token:
                raise Exception("Failed to obtain short-lived token.")

            print("Successfully obtained short-lived token.")

            # Step 2: Exchange short-lived token for long-lived token
            long_lived_token = self.exchange_short_lived_token(short_lived_token)
            
            if not long_lived_token:
                raise Exception("Failed to obtain long-lived token.")

            print("Successfully exchanged for long-lived token.")

            # Step 3: Save tokens to token store with expiration date
            expires_at = "2025-12-31T23:59:59Z"  # 示例过期日期，实际应根据 API 返回的过期时间设置
            self.token_store.save_persona_token("Aunt", long_lived_token, expires_at)  # 保存 Aunt 的令牌
            self.token_store.save_persona_token("Participant", long_lived_token, expires_at)  # 保存 Participant 的令牌

            print("Access tokens saved successfully.")

        except Exception as e:
            print(f"Error generating or regenerating access tokens: {e}")
