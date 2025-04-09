from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL

class CommentGenerator:
    def __init__(self, base_prompt):
        self.base_prompt = base_prompt
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL

    def generate_comment(self, media_url, caption, comment_history, persona_data):
        """
        Generate a comment using GPT-4o by filling in the prompt template.
        """
        try:
            # 1. 将 persona_data 格式化为可读的字符串
            persona_details = "\n".join([
                f"- {key}: {value}"
                for key, value in persona_data.items()
                if key != "IG User ID"
            ])
            
            # 2. 准备格式化参数，使用双大括号
            format_params = {
                "{{media_url}}": media_url,
                "{{caption}}": caption,
                "{{persona_details}}": persona_details,
                "{{persona_name}}": persona_data["Label"]
            }
            
            # 3. 使用字符串替换而不是 format
            prompt = self.base_prompt
            for key, value in format_params.items():
                prompt = prompt.replace(key, str(value))
            
            print("Generated prompt:", prompt)  # 调试用
            
            # 4. 生成评论
            # response = self.client.chat.completions.create(
            #     model=self.model,
            #     messages=[{"role": "user", "content": prompt}],
            #     temperature=0.7
            # )
            # comment = response.choices[0].message.content.strip()
            
            comment = "Test comment!"
            return comment
            
        except Exception as e:
            print(f"Error generating comment: {e}")
            return None
