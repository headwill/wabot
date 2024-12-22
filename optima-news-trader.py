import time
import requests
from googletrans import Translator

# Configuração do Telegram
BOT_TOKEN = '7526642542:AAEu_z0DMl1k0YvtlA_GvLTRu81KEbNxp7I'
CHAT_ID = '-1002258491083'

# Função para enviar a mensagem para o canal do Telegram
def enviar_mensagem_telegram(mensagem):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {
        'chat_id': CHAT_ID,
        'text': mensagem
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print("Mensagem enviada com sucesso para o canal do Telegram!")
    else:
        print(f"Erro ao enviar a mensagem. Status code: {response.status_code}")

# Função para obter e traduzir as notícias
def obter_noticias(noticias_enviadas):
    url = "https://cryptopanic.com/api/free/v1/posts/"
    auth_token = "a621ea399c5ebf8b4d70068feb22d358e8482066"
    params = {"auth_token": auth_token, "page": 1}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        translator = Translator()

        # Processa as notícias
        for noticia in data['results']:
            titulo = noticia['title']
            if titulo not in noticias_enviadas:  # Verifica se já foi enviada
                titulo_traduzido = translator.translate(titulo, src='en', dest='pt').text
                url_noticia = noticia['url']
                data_publicacao = noticia['published_at']
                mensagem = f"Título: {titulo_traduzido}\nPublicado em: {data_publicacao}\nLeia mais: {url_noticia}"
                
                # Envia a mensagem para o Telegram
                enviar_mensagem_telegram(mensagem)
                noticias_enviadas.add(titulo)  # Adiciona ao histórico
    else:
        print(f"Erro ao buscar notícias. Status code: {response.status_code}")

# Loop para enviar notícias de hora em hora
def enviar_noticias_periodicamente():
    noticias_enviadas = set()  # Mantém o histórico das notícias enviadas
    while True:
        obter_noticias(noticias_enviadas)
        time.sleep(3600)  # Aguarda 1 hora

# Inicia o envio periódico de notícias
enviar_noticias_periodicamente()
