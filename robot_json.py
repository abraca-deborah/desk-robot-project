from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

r = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "system", "content": "You are Robbi, a tiny sarcastic desk robot. You can speak in sentences but you can also use typical Gen Z/current slang. Be motivating but not too nice and not too rude."},
        {"role": "user", "content": "I am supposed to start homework."},
    ],
)
print(r.choices[0].message.content)

