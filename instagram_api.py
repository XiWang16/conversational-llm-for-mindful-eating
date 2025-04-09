# instagram_api.py
import requests
from config import GRAPH_API_VERSION

class InstagramAPI:
    def __init__(self, access_token):
        self.ig_business_access_token = access_token
        self.api_version = GRAPH_API_VERSION
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    def get_user_pages(self):
        """
        Get all Facebook Pages that the current user has access to.
        """
        url = f"{self.base_url}/me/accounts"
        params = {
            "access_token": self.ig_business_access_token,
            "fields": "id,name,access_token"
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Error getting pages that the current user has access to: {response.text}")
        
        data = response.json()
        if "data" not in data:
            raise Exception("No pages found for the current user")
        
        return data["data"]

    def get_page_by_name(self, page_name):
        """
        Get a specific Facebook Page by name.
        """
        pages = self.get_user_pages()
        for page in pages:
            if page["name"].lower() == page_name.lower():
                return page
        raise Exception(f"Page with name '{page_name}' not found")

    def get_connected_instagram_account(self, page_id, page_access_token):
        """
        Get the Instagram Business Account connected to a Facebook Page.
        """
        url = f"{self.base_url}/{page_id}"
        params = {
            "fields": "connected_instagram_account",
            "access_token": page_access_token
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Error getting connected Instagram account: {response.text}")
        
        page_data = response.json()
        if "connected_instagram_account" not in page_data:
            raise Exception("No connected Instagram Business Account found for this Page")
        
        return page_data["connected_instagram_account"]

    def get_recent_post(self, page_name):
        """
        Retrieve the most recent post from an Instagram Business account connected to a Facebook Page.
        """
        # Step 1 & 2: Get the page by name and its access token
        page = self.get_page_by_name(page_name)
        page_id = page["id"]
        page_access_token = page["access_token"]
        
        # Step 3: Get the connected Instagram Business Account
        ig_account = self.get_connected_instagram_account(page_id, page_access_token)
        ig_account_id = ig_account["id"]
        
        # Step 4: Get the most recent post
        url = f"{self.base_url}/{ig_account_id}/media"
        params = {
            "fields": "id,caption,media_type,media_url,timestamp,permalink",
            "limit": 1,
            "access_token": self.ig_business_access_token
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Error retrieving posts: {response.text}")
        data = response.json()
        if "data" in data and len(data["data"]) > 0:
            return data["data"][0]
        else:
            raise Exception("No posts found for the specified account.")

    def get_comments(self, post_id):
        """
        Retrieve existing comments for a given post.
        """
        url = f"{self.base_url}/{post_id}/comments"
        params = {
            "fields": "id,text,username,timestamp",
            "access_token": self.ig_business_access_token
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Error retrieving comments: {response.text}")
        data = response.json()
        return data.get("data", [])

    def post_comment(self, post_id, comment_text, persona_token):
        """
        Post a comment to a given post using a persona's access token.
        """
        # First verify the persona token is valid and has required permissions
        url = f"{self.base_url}/me"
        params = {
            "fields": "id,name",
            "access_token": persona_token
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Invalid persona token or insufficient permissions: {response.text}")
        
        # Now post the comment
        url = f"{self.base_url}/{post_id}/comments"
        params = {
            "message": comment_text,
            "access_token": persona_token
        }
        response = requests.post(url, data=params)
        if response.status_code != 200:
            raise Exception(f"Error posting comment: {response.text}")
        return response.json()

    def download_media(self, media_url):
        """
        Download media content from a URL.
        """
        response = requests.get(media_url)
        if response.status_code != 200:
            raise Exception(f"Error downloading media: {response.text}")
        return response.content
