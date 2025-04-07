# instagram_api.py
import requests

class InstagramAPI:
    def __init__(self, access_token, api_version="v22.0"):
        self.access_token = access_token
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    def get_recent_post(self, instagram_account_id):
        """
        Retrieve the most recent post from an Instagram Business account.
        """
        url = f"{self.base_url}/{instagram_account_id}/media"
        params = {
            "fields": "id,caption,media_url,media_type,permalink,timestamp",
            "access_token": self.access_token,
            "limit": 1
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
            "access_token": self.access_token
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
