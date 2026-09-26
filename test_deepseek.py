from openai import OpenAI

client = OpenAI(
    api_key="local",
    base_url="http://127.0.0.1:9655/v1"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": "Привет! Ответь коротко: работает ли подключение?"}
    ]
)

print(response.choices[0].message.content)