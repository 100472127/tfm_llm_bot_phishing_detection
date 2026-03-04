import discord
import logging
import re

logger = logging.getLogger("DiscordBot")

class MyDiscordBot(discord.Client):
    def __init__(self, token, ai_brain):
        """
        Configura el cliente de Discord.
        Acepta el token y el cerebro de IA, igual que la clase de Telegram.
        """
        # 1. Configuración interna de Intents
        intents = discord.Intents.default()
        intents.message_content = True
        
        # 2. Inicializamos la clase padre (discord.Client)
        super().__init__(intents=intents)

        self.ai_brain = ai_brain
        self.token = token


    @staticmethod
    def messageWithURL(mensaje: str) -> bool:
        """
        Función para detectar si un mensaje contiene una URL.
        """
        url_pattern = re.compile(
            r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)'
        )
        return bool(url_pattern.search(mensaje))


    async def on_ready(self):
        logger.info(f'🚀 Bot de Discord conectado y listo como: {self.user}')


    async def on_message(self, message):
        # Evitar que el bot se responda a sí mismo
        if message.author == self.user:
            return
            
        # Lógica de detección usando el cerebro compartido
        if self.messageWithURL(message.content):
            result = await self.ai_brain.analyze_message(message.content)
        
            if result is None:
                await message.reply("❌ Lo siento, no pude analizar el mensaje en este momento.")
                return
            
            # En caso de detectar phishing (ALTO o MEDIO), enviar alerta
            if "ALTO" in result:
                mensaje_alto = (
                    "🚨🚨 **¡PELIGRO EXTREMO!** 🚨🚨\n\n"
                    "Este mensaje ha sido identificado como una **estafa muy probable**.\n"
                    "**NO abras el enlace** bajo ninguna circunstancia.\n\n"
                    f"🔍 **Análisis:**\n{result}"
                )
                await message.reply(mensaje_alto)

            elif "MEDIO" in result:
                mensaje_medio = (
                    "⚠️ **AVISO DE PRECAUCIÓN** ⚠️\n\n"
                    "El sistema detectó elementos sospechosos en este mensaje.\n"
                    "Procede con cuidado y verifica la fuente antes de hacer clic.\n\n"
                    f"🔍 **Análisis:**\n{result}"
                )
                await message.reply(mensaje_medio)
        

    def run(self):
        """
        Arranca el bot. Sobrescribe el método run estándar para
        usar el token guardado en self.token automáticamente.
        """
        # Llamamos al método run() original de la librería discord.Client
        super().run(self.token)