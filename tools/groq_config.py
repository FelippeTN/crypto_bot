import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def groq_chat(user_promt: str) -> str:
    print('iniciando bot...')
    try:
        client = Groq(
            api_key=os.getenv("GROQ_API_KEY"),
        )
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"""{user_promt}""",
                }
            ],
            model="llama3-70b-8192",
        )
        
        return chat_completion.choices[0].message.content
    
    except Exception as e:
        print(e)
    
