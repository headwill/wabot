import time
import requests
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from datetime import datetime

print("CRIADO POR: WILLIAN DE OLIVEIRA")

# Configuração do Telegram
TELEGRAM_BOT_TOKEN = "7526642542:AAEu_z0DMl1k0YvtlA_GvLTRu81KEbNxp7I"
TELEGRAM_GROUP_ID = "-4659620768"

# Parâmetros
symbol = 'BTCUSDT'
interval = '5m'
limit = 100
stop_loss_percentage = 0.02
take_profit_percentage = 0.03

# Função para obter dados da Binance
def obter_dados_binance():
    try:
        url = f"https://api.binance.com/api/v3/klines"
        params = {'symbol': symbol, 'interval': interval, 'limit': limit}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                         'close_time', 'quote_asset_volume', 'number_of_trades',
                                         'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        return df
    except Exception as e:
        print(f"Erro ao obter dados da Binance: {e}")
        return None

# Funções para indicadores técnicos
def calcular_rsi(df, period=14):
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calcular_ema(df, period=10):
    return df['close'].ewm(span=period, adjust=False).mean()

def calcular_sma(df, period=10):
    return df['close'].rolling(window=period).mean()

def calcular_bollinger_bands(df, period=20):
    sma = df['close'].rolling(window=period).mean()
    std_dev = df['close'].rolling(window=period).std()
    upper_band = sma + (std_dev * 2)
    lower_band = sma - (std_dev * 2)
    return upper_band, lower_band

def calcular_macd(df, short_period=12, long_period=26, signal_period=9):
    short_ema = df['close'].ewm(span=short_period, adjust=False).mean()
    long_ema = df['close'].ewm(span=long_period, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal_period, adjust=False).mean()
    return macd, signal_line

# Modelo LSTM para previsão de preços
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_layer_size, output_size):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_layer_size, batch_first=True)
        self.linear = nn.Linear(hidden_layer_size, output_size)
    
    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.linear(out[:, -1, :])  # Pega a última saída da sequência
        return out

# Função para prever a tendência com LSTM
def prever_tendencia_lstm(df):
    # Preparar os dados de entrada para o LSTM
    close_prices = df['close'].values
    close_prices = close_prices.reshape(-1, 1)  # Ajusta para uma coluna
    close_prices = torch.tensor(close_prices, dtype=torch.float32).unsqueeze(0)  # Adiciona a dimensão do batch
    
    # Definir o modelo LSTM
    model = LSTMModel(input_size=1, hidden_layer_size=64, output_size=1)
    model.eval()  # Definir como modo de avaliação
    
    # Prever o próximo valor
    with torch.no_grad():
        predicted_price = model(close_prices)
    
    return predicted_price.item()  # Retorna o valor previsto

# Função principal para análise e sinal
def calcular_sinal(df):
    if df is None or df.empty:
        return "Erro ao calcular sinal: Dados insuficientes."

    # Cálculo dos indicadores
    df['rsi'] = calcular_rsi(df)
    df['ema'] = calcular_ema(df)
    df['sma'] = calcular_sma(df)
    df['upper_band'], df['lower_band'] = calcular_bollinger_bands(df)
    df['macd'], df['signal_line'] = calcular_macd(df)

    # Últimos valores
    last_close = df['close'].iloc[-1]
    last_rsi = df['rsi'].iloc[-1]
    last_ema = df['ema'].iloc[-1]
    last_macd = df['macd'].iloc[-1]
    last_signal = df['signal_line'].iloc[-1]
    last_upper = df['upper_band'].iloc[-1]
    last_lower = df['lower_band'].iloc[-1]

    stop_loss = last_close * (1 - stop_loss_percentage)
    take_profit = last_close * (1 + take_profit_percentage)

    # Previsão do preço com LSTM
    predicted_price = prever_tendencia_lstm(df)
    
    # Lógica de compra/venda
    if last_rsi < 30 and last_close < last_lower and last_macd > last_signal and predicted_price > last_close:
        action = "⚖️ Comprar agora!"
    elif last_rsi > 70 and last_close > last_upper and last_macd < last_signal and predicted_price < last_close:
        action = "⚖️ Vender agora!"
    else:
        action = "⚖️ Nenhuma ação recomendada."

    message = (
        f"{action}\n"
        f"RSI: {last_rsi:.2f}\n"
        f"Preço atual: ${last_close:.2f}\n"
        f"🎯 Take Profit: ${take_profit:.2f}\n"
        f"🛑 Stop Loss: ${stop_loss:.2f}\n"
        f"Bollinger Bands: [{last_lower:.2f}, {last_upper:.2f}]\n"
        f"MACD: {last_macd:.2f}, Signal: {last_signal:.2f}\n"
        f"Previsão de preço (LSTM): ${predicted_price:.2f}\n"
        f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    return message

# Função para enviar mensagem ao Telegram
def enviar_mensagem_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_GROUP_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("Mensagem enviada com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

# Mensagem inicial
enviar_mensagem_telegram(
    "Preparem suas contas, iniciaremos a negociação.\n"
    "Sou um auxílio para as suas negociações. Boa sorte!"
)

time.sleep(1)

# Loop para envio a cada 10 minutos
while True:
    print("Iniciando análise...")
    df = obter_dados_binance()
    mensagem = calcular_sinal(df)
    enviar_mensagem_telegram(mensagem)
    print("Aguardando 10 minutos...")
    time.sleep(600)
