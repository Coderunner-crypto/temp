import openai
import os
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')



def get_response(messages, message):
    if message:
        messages.append({
            "role": "user", "content": message
        })

        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )

        response = chat.choices[0].message.content

        messages.append({
            "role": "assistant", "content": response
        })

        return messages, response