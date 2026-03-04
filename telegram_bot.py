# telegram_module.py
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import re
import logging

logger = logging.getLogger("TelegramBot")

class MyTelegramBot:
    def __init__(self, token, ai_brain):
        """
        Inicializamos la clase con el token y el cerebro de la IA.
        """
        self.token = token
        self.ai_brain = ai_brain


    @staticmethod
    def messageWithURL(mensaje: str) -> bool:
        """
        Función para detectar si un mensaje contiene una URL.
        """
        url_pattern = re.compile(
            r'https?://(?:www\.)?[-\w\u00C0-\u024F\u0370-\u03FF\u0400-\u04FF@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-\w\u00C0-\u024F\u0370-\u03FF\u0400-\u04FF@:%_\+.~#?&\/=]*)'
        )
        return bool(url_pattern.search(mensaje))


    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Manejador de mensajes. Se ejecuta cada vez que llega texto.
        """
        if not update.message or not update.message.text:
            return
        
        # Extraemos el texto del mensaje del usuario
        texto_usuario = update.message.text
        if self.messageWithURL(texto_usuario):
            # Usamos el cerebro de la IA para analizar el mensaje
            result = await self.ai_brain.analyze_message(texto_usuario)

            # Obtener el ID del mensaje original para que el bot responda al mensaje
            original_message_id = update.message.message_id

            if result is None:
                await update.message.reply_text("❌ Lo siento, no pude analizar el mensaje en este momento.",
                                          reply_to_message_id=original_message_id)
                return

            # En caso de detectar phishing (ALTO o MEDIO), enviar alerta
            if "ALTO" in result:
                mensaje_alto = (
                    "🚨🚨 **¡PELIGRO EXTREMO!** 🚨🚨\n\n"
                    "Este mensaje ha sido identificado como una **estafa muy probable**.\n"
                    "**NO abras el enlace** bajo ninguna circunstancia.\n\n"
                    f"🔍 **Análisis:**\n{result}"
                )
                await update.message.reply_text(mensaje_alto, 
                                                parse_mode='Markdown',
                                                reply_to_message_id=original_message_id)

            elif "MEDIO" in result:
                mensaje_medio = (
                    "⚠️ **AVISO DE PRECAUCIÓN** ⚠️\n\n"
                    "El sistema detectó elementos sospechosos en este mensaje.\n"
                    "Procede con cuidado y verifica la fuente antes de hacer clic.\n\n"
                    f"🔍 **Análisis:**\n{result}"
                )
                await update.message.reply_text(mensaje_medio, 
                                                parse_mode='Markdown',
                                                reply_to_message_id=original_message_id)
        

    def run(self):
        """
        Configura y arranca el bot.
        """
        # 1. Construimos la aplicación
        app = ApplicationBuilder().token(self.token).build()

        # 2. Añadimos el manejador
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))

        # 3. Arrancamos
        logger.info("🚀 Bot de Telegram iniciado y listo.")
        app.run_polling()