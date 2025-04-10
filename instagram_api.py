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
            raise Exception(f"Error getting pages: {response.text}")
        
        data = response.json()
        if "data" not in data:
            raise Exception("No pages found for the current user")
        
        return data["data"]

    def get_page_by_name(self, page_name):
        """
        Get a specific Facebook Page by its name.
        """
        pages = self.get_user_pages()
        for page in pages:
            if page["name"].lower() == page_name.lower():
                return page
        raise Exception(f"Page with name '{page_name}' not found")

    def get_connected_instagram_account(self, page_id, page_access_token):
        """
        Get the Instagram Business Account connected to the given Facebook Page.
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
        Retrieve the most recent post from an Instagram Business account connected to the given Facebook Page.
        Note: The API response might return posts in descending order.
        Adjust index as necessary.
        """
        # Get the page and its access token
        page = self.get_page_by_name(page_name)
        page_id = page["id"]
        page_access_token = page["access_token"]
        
        # Get the connected Instagram Business Account
        ig_account = self.get_connected_instagram_account(page_id, page_access_token)
        ig_account_id = ig_account["id"]
        
        # Get the most recent posts
        url = f"{self.base_url}/{ig_account_id}/media"
        params = {
            "fields": "id,caption,media_type,media_url,timestamp,permalink,children",  # include children if carousel
            "limit": 1,
            "access_token": self.ig_business_access_token
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Error retrieving posts: {response.text}")
        data = response.json()
        if "data" in data and len(data["data"]) > 0:
            # Adjust the index as needed. Here we pick the second most-recent post.
            return data["data"][0]
        else:
            raise Exception("No posts found for the specified account.")
    
    
    def get_media_details(self, media_id):
        """
        Retrieve full details of a media item using its media ID.
        This is particularly useful for carousel items, which only include the ID in the children list.
        """
        url = f"{self.base_url}/{media_id}"
        params = {
            "fields": "id,media_type,media_url,timestamp",
            "access_token": self.ig_business_access_token
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Error retrieving media details: {response.text}")
        return response.json()


    def get_media_urls(self, post):
        """
        Retrieve media URLs based on media type (carousel vs. single post).
        """
        media_urls = []
        try:
            media_type = post.get("media_type")
            if media_type == "CAROUSEL_ALBUM":
                children = post.get("children", {})
                # Instagram may return children as { "data": [...] }
                children_data = children.get("data", []) if isinstance(children, dict) else children
                print(children_data)
                for child in children_data:
                    child_id = child.get("id")
                    if child_id:
                        # Get the full child media details using the API.
                        child_details = self.get_media_details(child_id)
                        url = child_details.get("media_url")
                        if url:
                            media_urls.append(url)
            else:
                url = post.get("media_url")
                if url:
                    media_urls.append(url)
        except Exception as e:
            print(f"Error parsing media URLs from Graph API post: {e}")
        
        return media_urls

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
        # Verify the persona token is valid and has required permissions.
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

