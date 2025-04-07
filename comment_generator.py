import openai
import os

class CommentGenerator:
    def __init__(self, base_prompt):
        self.base_prompt = base_prompt
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def generate_comment(self, media_url, caption, comment_history, persona):
        """
        Generate a comment using GPT-4o by filling in the prompt template.
        """
        prompt = self.base_prompt.format(
            media_url=media_url,
            caption=caption,
            comment_history="\n".join(comment_history),
            style=persona.get("style", "default")
        )
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        comment = response.choices[0].message.content.strip()
        return comment
