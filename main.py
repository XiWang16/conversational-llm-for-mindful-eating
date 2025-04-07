# main.py
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from instagram_api import InstagramAPI
from token_manager import TokenManager
from persona_manager import PersonaManager
from media_uploader import MediaUploader
from comment_generator import CommentGenerator
from comment_logger import CommentLogger

async def process_post():
    # Load configuration
    instagram_account_id = os.getenv("PARTICIPANT_IG_USER_ID")  # 使用 AUNT_IG_USER_ID 作为默认账户
    if not instagram_account_id:
        print("Error: PARTICIPANT_IG_USER_ID is not set in .env file")
        return
    
    # Retrieve Instagram Business token from the token manager
    token_manager = TokenManager()
    business_token = token_manager.get_instagram_business_token()

    # Initialize modules
    insta_api = InstagramAPI(business_token)
    persona_manager = PersonaManager()
    
    # NEW: Retrieve access tokens for any personas that need them
    persona_manager.retrieve_tokens_for_persona()

    uploader = MediaUploader(bucket_name=os.getenv("GCS_BUCKET_NAME"))
    comment_gen = CommentGenerator(base_prompt=os.getenv("BASE_PROMPT"))
    logger = CommentLogger()

    # Step 1: Retrieve the most recent post
    try:
        post = insta_api.get_recent_post(instagram_account_id)
    except Exception as e:
        print(f"Error fetching recent post: {e}")
        return

    post_id = post.get("id")
    caption = post.get("caption", "")
    media_url = post.get("media_url")

    # Step 2: Download the media from the post
    try:
        media_bytes = insta_api.download_media(media_url)
    except Exception as e:
        print(f"Error downloading media: {e}")
        return

    # Step 3: Upload media to Google Cloud Storage
    try:
        uploaded_media_url = uploader.upload_media_bytes(media_bytes)
    except Exception as e:
        print(f"Error uploading media: {e}")
        return

    # Step 4 & 5: For each persona, generate and post a comment with the specified delay
    async def handle_persona(persona_name, persona_data):
        try:
            existing_comments_raw = insta_api.get_comments(post_id)
            comment_history = [f"{comment['username']}: {comment['text']}" for comment in existing_comments_raw]
        except Exception as e:
            print(f"Error fetching comments for post {post_id}: {e}")
            comment_history = []

        comment_text = comment_gen.generate_comment(
            media_url=uploaded_media_url,
            caption=caption,
            comment_history=comment_history,
            persona=persona_data
        )
        print(f"Generated comment for {persona_name}: {comment_text}")

        delay_minutes = persona_data.get("delay_minutes", 0)
        print(f"Scheduling comment for {persona_name} with a delay of {delay_minutes} minutes.")
        await asyncio.sleep(delay_minutes * 60)

        try:
            # Use the persona's access token (now automatically retrieved, if needed)
            persona_token = persona_data.get("access_token")
            response = insta_api.post_comment(post_id, comment_text, persona_token)
            print(f"Posted comment for {persona_name}: {response}")
            # Log the comment for historical tracking
            logger.log_comment(post_id, persona_name, comment_text)
        except Exception as e:
            print(f"Error posting comment for {persona_name}: {e}")

    # Create and run tasks for all personas concurrently
    tasks = []
    for persona_name, persona_data in persona_manager.personas.items():
        tasks.append(handle_persona(persona_name, persona_data))
    
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(process_post())