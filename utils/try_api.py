from openai import OpenAI
import os

API_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "https://openrouter.ai/api/v1")
API_KEY = os.getenv("ANTHROPIC_API_KEY", "PUT_YOUR_KEY_HERE")
DEFAULT_MODEL = os.getenv("ANTHROPIC_DEFAULT_SONNET_MODEL", "moonshotai/kimi-k2.5")

api_key = "PUT_YOUR_KEY_HERE"

client = OpenAI(
  api_key = API_KEY,
  base_url= API_BASE_URL,
)

response = client.chat.completions.create(
    model=DEFAULT_MODEL,   # 在这里指定模型
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你好，可以帮我解释一下量子叠加吗？"}
    ],
    max_tokens=5000
)

print(response.choices[0].message.content)