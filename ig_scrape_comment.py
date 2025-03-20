import os
import requests
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Instagram API credentials
INSTAGRAM_APP_ID = os.getenv("INSTAGRAM_APP_ID")
INSTAGRAM_APP_SECRET = os.getenv("INSTAGRAM_APP_SECRET")
INSTAGRAM_REDIRECT_URI = os.getenv("INSTAGRAM_REDIRECT_URI")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")

# OpenAI API credentials
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# TODO: add credentials for other models

# Instagram API endpoints
INSTAGRAM_API_BASE = "https://graph.instagram.com"
MEDIA_ENDPOINT = f"{INSTAGRAM_API_BASE}/me/media"
COMMENT_ENDPOINT = lambda media_id: f"{INSTAGRAM_API_BASE}/{media_id}/comments"

def fetch_recent_media():
    """
    Fetch the most recent media (post) from the authenticated Instagram account.
    """
    params = {
        "access_token": INSTAGRAM_ACCESS_TOKEN,
        "fields": "id,caption,media_type,media_url,timestamp"
    }
    response = requests.get(MEDIA_ENDPOINT, params=params)
    if response.status_code == 200:
        media_data = response.json().get("data", [])
        if media_data:
            return media_data[0]  # Return the most recent post
        else:
            raise Exception("No posts found.")
    else:
        raise Exception(f"Failed to fetch posts: {response.status_code} - {response.text}")

def download_media(media):
    """
    Download the media (image or video) from the post.
    """
    media_url = media.get("media_url")
    if not media_url:
        raise Exception("No media URL found in the post.")

    response = requests.get(media_url)
    if response.status_code == 200:
        file_name = f"media_{media['id']}.{'jpg' if media['media_type'] == 'IMAGE' else 'mp4'}"
        with open(file_name, "wb") as file:
            file.write(response.content)
        print(f"Downloaded media: {file_name}")
    else:
        raise Exception(f"Failed to download media: {response.status_code} - {response.text}")

def generate_comment(caption):
    """
    Use OpenAI's GPT to generate a comment based on the post's caption.
    """
    prompt = f"The following is a caption from an Instagram post. Generate a short, engaging comment:\n\n{caption}\n\nComment:"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=30,
        temperature=0.7
    )
    return response.choices[0].text.strip()

def post_comment(media_id, comment):
    """
    Post a comment under the specified media (post).
    """
    params = {
        "access_token": INSTAGRAM_ACCESS_TOKEN,
        "message": comment
    }
    response = requests.post(COMMENT_ENDPOINT(media_id), data=params)
    if response.status_code == 200:
        print(f"Comment posted successfully: {comment}")
    else:
        raise Exception(f"Failed to post comment: {response.status_code} - {response.text}")

def main():
    try:
        # Step 1: Fetch the most recent post
        print("Fetching recent media...")
        recent_media = fetch_recent_media()
        print(f"Fetched media: {recent_media['id']}")

        # Step 2: Download the media
        print("Downloading media...")
        download_media(recent_media)

        # Step 3: Generate a comment using GPT
        print("Generating comment...")
        caption = recent_media.get("caption", "No caption available.")
        comment = generate_comment(caption)
        print(f"Generated comment: {comment}")

        # Step 4: Post the comment
        print("Posting comment...")
        post_comment(recent_media["id"], comment)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()