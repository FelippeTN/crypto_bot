from ta.volatility import AverageTrueRange
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from textblob import TextBlob
from tabulate import tabulate
from time import sleep
import yfinance as yf
import requests,  os
import pandas as pd

from tools.groq_config import groq_chat

def fetch_crypto_data(ticker, period="6mo", interval="1d"):

    data = yf.download(ticker, period=period, interval=interval)
    if isinstance(data.columns, pd.MultiIndex):
        ticker_column = data.columns.get_level_values(1)[0]
        return data, ticker_column
    return data, None


def fetch_sentiment_score(query):
    """Busca o sentimento geral para um ativo usando uma API ou modelo local."""
    try:
        
        api_key = os.getenv('NEWSAPI_KEY')
        url = f"https://newsapi.org/v2/everything?q={query}&language=en&apiKey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json()["articles"]

        sentiments = []
        for article in articles:
            title = article["title"]
            analysis = TextBlob(title).sentiment
            sentiments.append(analysis.polarity)

        return sum(sentiments) / len(sentiments) if sentiments else 0
    except Exception as e:
        print(f"Erro ao buscar sentimento para {query}: {e}")
        return None

def analyze_trend(data, ticker_column):
    """Analisa a tendência do criptoativo usando indicadores técnicos."""
    try:
        close_data = data[('Close', ticker_column)] if ticker_column else data['Close']
        close_data = pd.to_numeric(close_data, errors='coerce').astype(float)

        if len(close_data) < 50:
            return False, False, False

        window_50 = min(50, len(close_data))
        window_200 = min(200, len(close_data))

        sma_50 = close_data.rolling(window=window_50).mean()
        sma_200 = close_data.rolling(window=window_200).mean()

        ema = EMAIndicator(close=close_data, window=min(20, len(close_data)))
        ema_20 = ema.ema_indicator()

        rsi = RSIIndicator(close=close_data, window=min(14, len(close_data)))
        rsi_values = rsi.rsi()

        short_term_buy = rsi_values.iloc[-1] < 45 and close_data.iloc[-1] > ema_20.iloc[-1]
        medium_term_buy = window_50 == 50 and sma_50.iloc[-1] > sma_200.iloc[-1]
        long_term_buy = window_200 == 200 and sma_200.iloc[-1] > sma_200.iloc[-50]

        return short_term_buy, medium_term_buy, long_term_buy
    except Exception as e:
        return False, False, False
    
def analyze_sentiment(asset):
    """Analisa o sentimento de mercado para um criptoativo."""
    sentiment_score = fetch_sentiment_score(asset)
    if sentiment_score is None:
        return "Sem dados", 0
    if sentiment_score > 0.1:
        return "Compra", 3
    elif sentiment_score < -0.1:
        return "Venda", -3
    else:
        return "Neutro", 1

def analyze_fundamentals(data, ticker_column):
    """Analisa métricas fundamentais do ativo, como volume e market cap."""
    try:
        close_data = data[('Close', ticker_column)] if ticker_column else data['Close']
        volume_data = data[('Volume', ticker_column)] if ticker_column else data['Volume']

        price_change = ((close_data.iloc[-1] - close_data.iloc[-7]) / close_data.iloc[-7]) * 100
        avg_volume = volume_data.rolling(window=7).mean().iloc[-1]

        if price_change > 5 and avg_volume > volume_data.mean():
            return "Fundamentos Fortes", 3
        elif price_change < -5:
            return "Fundamentos Fracos", -3
        else:
            return "Neutro", 1
    except Exception as e:
        return "Neutro", 0


def aggressive_fundamental_analysis(data, ticker_column):
    """Realiza uma análise fundamentalista mais agressiva."""
    try:
        close_data = data[('Close', ticker_column)] if ticker_column else data['Close']
        volume_data = data[('Volume', ticker_column)] if ticker_column else data['Volume']

        price_change = ((close_data.iloc[-1] - close_data.iloc[-14]) / close_data.iloc[-14]) * 100
        volume_spike = volume_data.iloc[-1] > 1.5 * volume_data.rolling(window=14).mean().iloc[-1]

        if price_change > 10 and volume_spike:
            return "Alta demanda e grande valorização", 4
        elif price_change < -10:
            return "Grande desvalorização", -4
        else:
            return "Sem sinais claros", 0
    except Exception as e:
        return "Sem sinais claros", 0


# Atualização do método para incluir chamada à API do Qwen
def analyze_volatility(data, ticker_column):
    """Analisa a volatilidade do ativo usando o indicador Average True Range (ATR)."""
    try:
        high_data = data[('High', ticker_column)] if ticker_column else data['High']
        low_data = data[('Low', ticker_column)] if ticker_column else data['Low']
        close_data = data[('Close', ticker_column)] if ticker_column else data['Close']

        atr = AverageTrueRange(high=high_data, low=low_data, close=close_data, window=min(14, len(close_data)))
        atr_value = atr.average_true_range().iloc[-1]

        if atr_value > close_data.mean() * 0.05:  # ATR > 5% do preço médio
            return "Alta Volatilidade", 3
        else:
            return "Baixa Volatilidade", 1
    except Exception as e:
        return "Erro na análise de volatilidade", 0

def rank_assets_with_qwen(assets):
    """Classifica os criptoativos por vantagem para compra e atualiza recomendações via API Qwen."""
    recommendations = []
    output_dir = os.path.join(os.getcwd(), "recomendacoes")
    os.makedirs(output_dir, exist_ok=True)

    for asset in assets:
        try:
            data, ticker_column = fetch_crypto_data(asset)

            if data.empty:
                recommendations.append({"Ativo": asset, "Recomendação": "Sem dados disponíveis."})
                continue

            short, medium, long = analyze_trend(data, ticker_column)
            sentiment, sentiment_score = analyze_sentiment(asset)
            fundamentals, fundamentals_score = analyze_fundamentals(data, ticker_column)
            aggressive_analysis, aggressive_score = aggressive_fundamental_analysis(data, ticker_column)
            volatility, volatility_score = analyze_volatility(data, ticker_column)

            scores_text = (
                f"Ativo: {asset}\n"
                f"Curto prazo: {short}\n"
                f"Médio prazo: {medium}\n"
                f"Longo prazo: {long}\n"
                f"Sentimento: {sentiment} ({sentiment_score})\n"
                f"Fundamentalista: {fundamentals} ({fundamentals_score})\n"
                f"Análise agressiva: {aggressive_analysis} ({aggressive_score})\n"
                f"Volatilidade: {volatility} ({volatility_score})\n"
            )

            sleep(30)
            qwen_recommendation = groq_chat(scores_text)

            recommendations.append({"Ativo": asset, "Recomendação": qwen_recommendation})
            
            # Salva a recomendação em arquivo .txt
            file_name = f"{asset}.txt"
            file_path = os.path.join(output_dir, file_name)
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(f"Recomendações para {asset}:\n\n{scores_text}\n{qwen_recommendation}")
        except Exception as e:
            recommendations.append({"Ativo": asset, "Recomendação": f"Erro ao analisar {asset}: {e}"})
   
    return recommendations


def display_recommendations(recommendations):
    """Exibe recomendações em formato de tabela usando tabulate."""
    print("\n--- Recomendações de Compra ---")
    print(tabulate(recommendations, headers="keys", tablefmt="grid"))


def save_recommendations_to_files(recommendations, folder_name="recomendacoes_ativos"):
    """Salva as recomendações em arquivos .txt separados por ativo."""
    import os

    # Cria o diretório se não existir
    folder_path = os.path.join(os.getcwd(), "criptoativos", folder_name)
    os.makedirs(folder_path, exist_ok=True)

    for recommendation in recommendations:
        asset = recommendation["Ativo"]
        content = recommendation["Recomendação"]

        # Define o caminho do arquivo para o ativo
        file_name = f"{asset}.txt"
        file_path = os.path.join(folder_path, file_name)

        try:
            # Salva o conteúdo no arquivo
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(f"Ativo: {asset}\n\nRecomendação:\n{content}\n")
        except Exception as e:
            print(f"Erro ao salvar recomendação para {asset}: {e}")

    print(f"\nRecomendações salvas na pasta: {folder_path}")


