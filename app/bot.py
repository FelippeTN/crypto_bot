import os
from dotenv import load_dotenv
from tools.groq_config import groq_chat
from tools.fetch_crypto import *
from config.log_config import logger
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackContext,
    MessageHandler,
    filters,
)

# Carregar variáveis de ambiente
load_dotenv()
API_KEY = os.getenv('API_KEY')

class TelegramBot:
    def __init__(self):
        logger.info("Inicializando o TelegramChatbot")
        self.TELEGRAM_TOKEN = API_KEY
        self.esperando_resposta = False
        self.file_path = "./data/crypto_keywords.txt"

    def start_message(self):
        logger.info("Mensagem inicial carregada...")
        return self.default_message_reply

    async def handle_message(self, update: Update, context: CallbackContext):
        user_message = update.message.text.lower()
        chat_type = update.message.chat.type
        crypto_assets = ["BTC-USD", "ETH-USD"]
        
        with open(self.file_path, "r") as file:
            crypto_content = file.read()

        if chat_type in ["group", "supergroup"] and f"@{context.bot.username}" not in user_message:
            return

        if any(word in user_message for word in crypto_content.split()):
            logger.info('Groq está sendo chamado...')
            analyze_crypto = rank_assets_with_qwen(crypto_assets)
            response_text = groq_chat(analyze_crypto)
            await update.message.reply_text(text=response_text)
        else:
            response_text = groq_chat(user_message)
            await update.message.reply_text(text=response_text)

    async def start_command(self, update: Update, context: CallbackContext):
        """Responde ao comando /start sem teclado"""
        menu = self.start_message()
        await update.message.reply_text(text=menu)

    def start_bot(self):
        try:
            logger.info("Inicializando a aplicação do bot")
            application = (
                ApplicationBuilder()
                .token(self.TELEGRAM_TOKEN)
                .pool_timeout(20)
                .connect_timeout(15)
                .read_timeout(60)
                .write_timeout(60)
                .build()
            )

            start_handler = CommandHandler("start", self.start_command)
            application.add_handler(start_handler)
            
            message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message)
            application.add_handler(message_handler)
            
            application.run_polling()
            
        except Exception as e:
            logger.error(f"Erro ao iniciar o bot: {e}")
            raise
