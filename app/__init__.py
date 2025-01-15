from groq import Groq
import os

def groq_config(message):
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )
    print('iniciando')   
    chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"{message}"
                }
            ],
            model="llama3-70b-8192",
        )

    response = chat_completion.choices[0].message.content
    return response

groq_config('Bom dia mundo')