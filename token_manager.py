# token_manager.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

class TokenManager:
    def __init__(self):
        # Load tokens from environment variables (defined in config.env/.env)
        self.instagram_business_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        # Credentials for performing OAuth exchanges for user tokens
        self.app_id = os.getenv("INSTAGRAM_APP_ID")
        self.app_secret = os.getenv("INSTAGRAM_APP_SECRET")
        self.redirect_uri = os.getenv("INSTAGRAM_REDIRECT_URI")
        
        # 验证必要的环境变量
        if not all([self.app_id, self.app_secret, self.instagram_business_token]):
            raise Exception("Missing required environment variables: INSTAGRAM_APP_ID, INSTAGRAM_APP_SECRET, or INSTAGRAM_ACCESS_TOKEN")

    def get_instagram_business_token(self):
        # 验证令牌是否有效
        if not self.instagram_business_token:
            raise Exception("Instagram access token is not set in environment variables")
        
        # 尝试使用令牌获取用户信息来验证令牌
        try:
            url = f"https://graph.facebook.com/v22.0/me"
            params = {
                "access_token": self.instagram_business_token,
                "fields": "id,name"
            }
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"Token validation failed: {response.text}")
                # 如果令牌无效，尝试刷新
                self.refresh_token()
        except Exception as e:
            print(f"Error validating token: {e}")
            self.refresh_token()
        
        return self.instagram_business_token

    def get_short_lived_token(self, auth_code):
        """
        Exchanges an auth code for a short-lived access token.
        For Instagram Basic Display API, use:
          POST https://api.instagram.com/oauth/access_token
        """
        url = "https://api.instagram.com/oauth/access_token"
        data = {
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
            "code": auth_code
        }
        response = requests.post(url, data=data)
        if response.status_code != 200:
            raise Exception(f"Error obtaining short-lived token: {response.text}")
        token_data = response.json()
        return token_data.get("access_token")

    def exchange_short_lived_token(self, short_lived_token):
        """
        Exchanges a short-lived token for a long-lived token.
        Endpoint: GET https://graph.facebook.com/v12.0/oauth/access_token
        """
        url = "https://graph.facebook.com/v12.0/oauth/access_token"
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
        刷新访问令牌
        """
        try:
            print("Attempting to refresh Instagram access token...")
            print(f"Using APP_ID: {self.app_id}")
            
            # 使用正确的 API 版本和端点
            url = "https://graph.facebook.com/v22.0/oauth/access_token"
            params = {
                "grant_type": "fb_exchange_token",
                "client_id": self.app_id,
                "client_secret": self.app_secret,
                "fb_exchange_token": self.instagram_business_token
            }
            
            print(f"Making request to: {url}")
            response = requests.get(url, params=params)
            print(f"Response status: {response.status_code}")
            print(f"Response text: {response.text}")
            
            if response.status_code == 200:
                token_data = response.json()
                new_token = token_data.get("access_token")
                if new_token:
                    self.instagram_business_token = new_token
                    print("Successfully refreshed Instagram access token")
                    # 更新环境变量
                    os.environ["INSTAGRAM_ACCESS_TOKEN"] = new_token
                else:
                    raise Exception("Failed to get new access token from response")
            else:
                error_data = response.json()
                error_message = error_data.get("error", {}).get("message", "Unknown error")
                raise Exception(f"Error refreshing token: {error_message}")
        except Exception as e:
            print(f"Error in refresh_token: {e}")
            raise Exception("Failed to refresh Instagram access token. Please check your app credentials and try again.")
