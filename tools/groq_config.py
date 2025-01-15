import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def groc_chat(stock_name, price, user_promt):
    print('iniciando')
    try:
        client = Groq(
            api_key=os.getenv("GROQ_API_KEY"),
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {   "role": "system",
                    "content": f"Você é um bot profissional em analise de preços de criptomoedas e somente responde sobre criptomoedas se for perguntado. Com base no histórico de dados: Preço minimo do Ethereum esse ano: $2200. Preço Maximo do Ethereum esse ano: $4070. Preço atual: Nome: {stock_name}: Preço: {price}."
                },
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
    
