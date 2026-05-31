import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://api.clod.io/v1",
    api_key=os.environ["CLOD_API_KEY"],
)

response = client.chat.completions.create(
    model="GPT OSS 120B",
    messages=[
        {"role": "user", "content": "Hello! Please say hi back in one short sentence."}
    ],
)

print(response.choices[0].message.content)
