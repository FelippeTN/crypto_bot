import time, requests

def fetch_cryptos():
    crypto_dic = []
    while True:
        try:
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                'vs_currency': 'usd',
                'ids': 'ethereum',  
            }
            response = requests.get(url, params=params)
            data = response.json()


            print("Atualizando preços das criptos:")
            for crypto in data:
                crypto_dic.append({'name': crypto['name'], 'price': crypto['current_price']})
            
            for crypto in crypto_dic:
               return crypto['name'], crypto['price']

        except Exception as e:
            print(f"Erro ao buscar dados: {e}")
        
        time.sleep(5000)  
