import json
import mimetypes
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL

def format_persona_for_prompt(persona_data):
    """
    Convert persona JSON dict into natural language description for prompting.
    """
    def format_list(title, items):
        if not items:
            return ""
        return f"{title}:\n" + "\n".join([f"- {item}" for item in items])

    parts = [
        f"Label: {persona_data.get('Label', '')}",
        f"Tone & Voice: {persona_data.get('Tone & Voice', '')}",
        format_list("Goals", persona_data.get("Goals", [])),
        format_list("Personality & Values", persona_data.get("Personality & Values", [])),
        f"Language Style: {persona_data.get('Language Style', '')}",
        f"Length of Comments: {persona_data.get('Length of Comments', '')}",
        format_list("Example Comments", persona_data.get("Example Comments", [])),
        f"Emoji Use: {persona_data.get('Emoji Use', '')}"
    ]

    return "\n\n".join([p for p in parts if p])

class CommentGenerator:
    def __init__(self, base_prompt):
        self.base_prompt = base_prompt
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL

    def is_supported_image(self, url):
        mime, _ = mimetypes.guess_type(url)
        return mime in ["image/png", "image/jpeg", "image/webp", "image/gif"]

    def generate_comment(self, media_url, caption, comment_history, persona_data):
        """
        Generate a comment using GPT-4o with multimodal structured input.
        """
        try:
            # # Format persona details as a readable string
            # persona_details = "\n".join([
            #     f"- {key}: {value}"
            #     for key, value in persona_data.items()
            #     if key != "IG User ID"
            # ])

            persona_details = format_persona_for_prompt(persona_data)

            # Ensure media_url is a list
            if isinstance(media_url, str):
                media_url = [media_url]

            # Filter to include only supported image URLs
            media_blocks = [
                {"type": "image_url", "image_url": {"url": url}}
                for url in media_url
                if url and self.is_supported_image(url)
            ]

            # Construct the structured message content
            message_content = [
                {"type": "text", "text": f"Caption:\n{caption.strip() or '[No caption provided]'}"},
                {"type": "text", "text": f"Persona:\n{persona_details.strip()}"},
                # {"type": "text", "text": f"Comment History:\n{comment_history.strip() or '[No previous comments]'}"},
                *media_blocks
            ]

            # Prepare the full message sequence
            messages = [
                {"role": "system", "content": self.base_prompt},
                {"role": "user", "content": message_content}
            ]

            # Uncomment this to call the real API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            output = response.choices[0].message.content.strip().strip("\"")

            # Simulated output for now
            # output = "test"

            print("🧠 Final message sent to GPT:")
            print(json.dumps(messages, indent=2))
            return output

        except Exception as e:
            print(f"❌ Error generating comment: {e}")
            return None
