import yfinance as yf

# Baixar dados da ação (Exemplo: PETR4.SA)
acao = yf.Ticker("PETR4.SA")
historico = acao.history(period="1d")  # Último mês
print(historico)