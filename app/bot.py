import os
from dotenv import load_dotenv
from tools.groq_config import groc_chat
from tools.fetch_crypto import fetch_cryptos
from config.log_config import logger
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
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
        self.default_message_reply = "Olá! Gostaria de conversar com Nalim's BOT?"
        self.TELEGRAM_TOKEN = API_KEY
        self.esperando_resposta = False

    def start_message(self):
        logger.info("Menu loaded...")
        try:
            menu = self.default_message_reply
            return menu
        
        except Exception as e:
            logger.error(f"Erro ao carregar o menu: {e}")
            raise
            
    def generate_keyboard(self, menu, prefix_menu="submenu_", prefix_action="action_"):
        logger.info("Gerando teclado inline")
        keyboard = [
            [InlineKeyboardButton("Sim", callback_data=f"{prefix_action}1")],
            [InlineKeyboardButton("Não", callback_data=f"{prefix_action}2")],
        ]
        logger.info("Teclado inline gerado com sucesso")
        return keyboard
    
    async def button(self, update: Update, context: CallbackContext):
        query = update.callback_query
        await query.answer()

        # Condicional baseado na escolha do usuário
        if query.data == "action_1":
            response_text = """Ok, caso queira sair da conversa, é só digitar "sair"!\nFaça sua pergunta:"""
            self.esperando_resposta = True
        elif query.data == "action_2":
            response_text = "OK! Quando precisar de mim, estarei à disposição!"
        else:
            response_text = "Opção desconhecida."
        
        logger.info('Opção selecionada pelo usuário')
        # Edita a mensagem original com a resposta
        await query.edit_message_text(text=response_text)
        
    async def handle_message(self, update: Update, context: CallbackContext):
        user_message = update.message.text.lower()
        cripto_name, cripto_price = fetch_cryptos()
        
        if not self.esperando_resposta:
            # Inicia a conversa com a mensagem padrão e teclado
            menu = self.start_message()
            keyboard = self.generate_keyboard(menu)
            await update.message.reply_text(
                text=menu, reply_markup=InlineKeyboardMarkup(keyboard)
            )
        elif user_message != "sair":
            logger.info('Groq está sendo chamado...')
            response_text = groc_chat(cripto_name, cripto_price, user_message)
            await update.message.reply_text(text=response_text)
        else:
            self.esperando_resposta = False
            await update.message.reply_text(text="Encerrando a conversa. Até logo!")
            
    def start_bot(self):
        try:
            logger.info("Inicializando a aplicação do bot")
            application = (
                ApplicationBuilder()
                .token(self.TELEGRAM_TOKEN)
                .pool_timeout(20)
                .connect_timeout(15)
                .read_timeout(60)  # Aumentar o tempo de leitura
                .write_timeout(60)  # Aumentar o tempo de escrita
                .build()
            )
            
            # Handler para lidar com as respostas do teclado inline
            button_handler = CallbackQueryHandler(self.button)
            application.add_handler(button_handler)
            
            # Handler para lidar com todas as mensagens de texto
            message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message)
            application.add_handler(message_handler)
            
            # Iniciar o bot
            application.run_polling()
            
        except Exception as e:
            logger.error(f"Erro ao iniciar o bot: {e}")
            raise
