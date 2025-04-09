import asyncio
import json
from config import (
    GCS_BUCKET_NAME,
    BASE_PROMPT,
    PARTICIPANT_FB_PAGE_NAME
)

from instagram_api import InstagramAPI
from token_manager import TokenManager
from persona_manager import PersonaManager
from media_uploader import MediaUploader
from comment_generator import CommentGenerator
from comment_logger import CommentLogger

async def process_post(selected_persona=None):
    # Load configuration
    persona_manager = PersonaManager()
    
    # Initialize modules
    token_manager = TokenManager()
    business_token = token_manager.get_instagram_business_token()
    print(business_token)

    insta_api = InstagramAPI(business_token)
    uploader = MediaUploader(bucket_name=GCS_BUCKET_NAME)
    comment_gen = CommentGenerator(base_prompt=BASE_PROMPT)
    logger = CommentLogger()

    # Step 1: Retrieve the most recent post using the participant's Facebook Page name
    try:
        post = insta_api.get_recent_post(PARTICIPANT_FB_PAGE_NAME)
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
            persona_data=persona_data
        )
        print(f"Generated comment for {persona_name}: {comment_text}")

        delay_minutes = persona_data.get("delay_minutes", 0)
        print(f"Scheduling comment for {persona_name} with a delay of {delay_minutes} minutes.")
        await asyncio.sleep(delay_minutes * 60)

        try:
            persona_token = token_manager.token_store.get_persona_token(persona_name)
            if not persona_token:
                raise Exception(f"No access token found for persona: {persona_name}")

            response = insta_api.post_comment(post_id, comment_text, persona_token)
            print(f"Posted comment for {persona_name}: {response}")
            logger.log_comment(post_id, persona_name, comment_text)
        except Exception as e:
            print(f"Error posting comment for {persona_name}: {e}")

    # Create and run tasks for specified persona or all personas
    tasks = []
    if selected_persona is None:
        # 为所有角色生成评论
        for persona_name, persona_data in persona_manager.personas.items():
            tasks.append(handle_persona(persona_name, persona_data))
    else:
        # 为指定角色生成评论
        tasks.append(handle_persona(selected_persona, persona_manager.get_persona(selected_persona)))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    # 选择要生成评论的角色，可以传入角色名称或 None 以生成所有角色的评论
    selected_persona = "aunt"  # 或者指定某个角色名称，例如 "Aunt"
    asyncio.run(process_post(selected_persona))