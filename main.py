import asyncio
from pathlib import Path

# Unofficial Instagram API:
from instagrapi import Client
from instagrapi.exceptions import ClientError

# Official Instagram Graph API-related modules and others
from instagram_api import InstagramAPI
from token_manager import TokenManager
from persona_manager import PersonaManager
from media_uploader import MediaUploader
from comment_generator import CommentGenerator
from comment_logger import CommentLogger
import config
# from config import (
#     GCS_BUCKET_NAME,
#     BASE_PROMPT,
#     PARTICIPANT_FB_PAGE_NAME,
#     PARTICIPANT_IG_USERNAME,
#     PARTICIPANT_IG_PASSWORD,
#     # FRIEND_IG_USERNAME,
#     # FRIEND_IG_PASSWORD,
#     # COACH_IG_USERNAME,
#     # COACH_IG_PASSWORD,
#     # CONNOISSEUR_IG_USERNAME,
#     # CONNOISSEUR_IG_PASSWORD,
#     # FAN_IG_USERNAME,
#     # FAN_IG_PASSWORD,
#     # VISITOR_IG_USERNAME,
#     # VISITOR_IG_PASSWORD,
#     AUNT_IG_USERNAME,
#     AUNT_IG_PASSWORD
# )

TEMP_MEDIA_DIR = Path("/tmp/instagrapi_downloads")
TEMP_MEDIA_DIR.mkdir(parents=True, exist_ok=True)

async def download_and_upload_media(insta_api, uploader, media_urls):
    """
    Download media from each URL and then upload them to cloud storage.
    Wrapping synchronous operations in asyncio.to_thread to avoid blocking.
    Returns a list of URLs for uploaded media.
    """
    uploaded_media_urls = []
    for media_url in media_urls:
        try:
            # Wrap the synchronous download in a separate thread
            media_bytes = await asyncio.to_thread(insta_api.download_media, media_url)
        except Exception as e:
            print(f"Error downloading media from {media_url}: {e}")
            continue

        try:
            # Likewise, wrap the uploader call if it's synchronous
            uploaded_url = await asyncio.to_thread(
                uploader.upload_media_bytes,
                media_bytes,
                source_url=media_url  # enables MIME type detection
            )

            uploaded_media_urls.append(uploaded_url)
        except Exception as e:
            print(f"Error uploading media: {e}")
            continue
    return uploaded_media_urls

async def process_post(selected_persona=None, use_instagrapi=False):
    """
    Process the most recent post by:
      - retrieving media information,
      - downloading media,
      - uploading media to Google Cloud Storage,
      - generating comments (via LLM),
      - and posting comments under different personas (using either the official 
        Graph API or unofficial Instagrapi library).
    """
    # Load configuration and initialize helper classes
    persona_manager = PersonaManager()
    token_manager = TokenManager()
    business_token = token_manager.get_instagram_business_token()
    print(f"Business Token: {business_token}")

    uploader = MediaUploader(bucket_name=getattr(config, "GCS_BUCKET_NAME"))
    comment_gen = CommentGenerator(base_prompt=getattr(config, "BASE_PROMPT"))
    logger = CommentLogger()

    # Variables to be set by each branch
    media_urls = []      # List of URLs to download media from

    # Step 1: Retrieve the most recent post using the participant's Facebook Page name
    insta_api = InstagramAPI(business_token)
    try:
        post = insta_api.get_recent_post(getattr(config, "PARTICIPANT_FB_PAGE_NAME"))
        if not post:
            print("No recent post found using Graph API.")
            return
    except Exception as e:
        print(f"Error fetching recent post from Graph API: {e}")
        return

    post_id = post.get("id")
    print(post_id)
    caption = post.get("caption", "")
    
    # Step 2: Retrieve media URLs based on media type (carousel vs. single post)
    media_urls = insta_api.get_media_urls(post)  # 调用新函数获取媒体 URL
    print(media_urls)

    # Step 3 & 4: Download and upload post media (images and/or videos)
    uploaded_media_urls = await download_and_upload_media(insta_api, uploader, media_urls)
    if not uploaded_media_urls:
        print("No media was successfully uploaded.")
        return
    
    # Step 5 & 6: For each persona, generate and post a comment with the specified delay
    async def handle_persona(persona_name, persona_data, post_id, caption, uploaded_media_urls):
        try:
            existing_comments = insta_api.get_comments(post_id)
            comment_history = [f"{comment['username']}: {comment['text']}" for comment in existing_comments]
        except Exception as e:
            print(f"Error fetching comments via Graph API for post {post_id}: {e}")
            comment_history = []

        # Generate comment 
        print(uploaded_media_urls)
        comment_text = comment_gen.generate_comment(
            media_url=uploaded_media_urls,  # Pass the list of uploaded GCS URLs
            caption=caption,
            comment_history=comment_history,
            persona_data=persona_data
        )
        print(f"Generated comment for {persona_name}: {comment_text}")

        # Schedule the posting after a delay defined in the persona data
        delay_minutes = persona_data.get("delay_minutes", 0)
        print(f"Scheduling comment for {persona_name} with a delay of {delay_minutes} minutes.")
        await asyncio.sleep(delay_minutes * 60)

        try:
            if use_instagrapi:
                # Retrieve Instagram credentials for the persona
                ig_username = getattr(config, f"{persona_name.upper()}_IG_USERNAME", None)
                ig_password = getattr(config, f"{persona_name.upper()}_IG_PASSWORD", None)

                # Check if credentials are provided
                if not ig_username or not ig_password:
                    raise Exception(f"Missing credentials for persona: {persona_name}")

                # Create a Client instance and log in to the Instagram account of the persona
                cl = Client()
                cl.login(ig_username, ig_password)  # Log in to the persona's Instagram account

                try:
                    # Retrieve the latest post for the given user using Instagrapi
                    user_id = cl.user_id_from_username(getattr(config, "PARTICIPANT_IG_USERNAME"))
                    media = cl.user_medias(user_id, 1)  # Retrieve latest post
                    if not media:
                        print(f"No media found for user {getattr(config, 'PARTICIPANT_IG_USERNAME')}.")
                        return
                    post = media[0]
                    post_id = post.pk
                    caption = post.caption_text or ""
                except Exception as e:
                    print(f"Error retrieving post with Instagrapi: {e}")
                    return

                # Post the comment on the media
                response = cl.media_comment(post_id, comment_text)
            else:
                persona_token = token_manager.token_store.get_persona_token(persona_name)
                if not persona_token:
                    raise Exception(f"No access token found for persona: {persona_name}")
                response = insta_api.post_comment(post_id, comment_text, persona_token)
            print(f"Posted comment for {persona_name}: {response}")
            logger.log_comment(post_id, persona_name, comment_text)
        except Exception as e:
            print(f"Error posting comment for {persona_name}: {e}")

    # Create asynchronous tasks for personas.
    tasks = []
    if selected_persona is None:
        # Process all personas from personas.json
        for persona_name, persona_data in persona_manager.personas.items():
            tasks.append(handle_persona(persona_name, persona_data, post_id, caption, uploaded_media_urls))
    else:
        # Process only the selected persona(s)
        for persona_name in selected_persona:
            persona_data = persona_manager.get_persona(persona_name)
            if persona_data:
                tasks.append(handle_persona(persona_name, persona_data, post_id, caption, uploaded_media_urls))
            else:
                print(f"Persona {persona_name} not found.")

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    # 选择要生成评论的角色，可以传入角色名称或 None 以生成所有角色的评论
    # Available personas: ["aunt", "close_friend", "healthy_eating_coach", "food_connoisseur", "fan", "curious_casual_visitor"]
    # Make sure all names match the keys in personas.json
    selected_persona = ["aunt"]  # 或者指定某个角色名称，例如 "Aunt"
    use_instagrapi = True  # Set True to use Instagrapi, False to use official Graph API
    asyncio.run(process_post(selected_persona, use_instagrapi))