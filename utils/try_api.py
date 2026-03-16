from openai import OpenAI
import os

API_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "https://openrouter.ai/api/v1")
API_KEY = os.getenv("ANTHROPIC_API_KEY", "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")
DEFAULT_MODEL = os.getenv("ANTHROPIC_DEFAULT_SONNET_MODEL", "moonshotai/kimi-k2.5")

api_key = "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"

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