import json
import os
import logging
from ai_handler import PhishingAI
from telegram_bot import MyTelegramBot
from discord_bot import MyDiscordBot


def configurar_logging():
    """
    Configura el sistema de logs para que salga por consola y tenga un formato legible.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.StreamHandler() 
        ]
    )


def obtener_configuracion_manual():
    """
    Solicita los datos al usuario por consola paso a paso.
    """
    print("\n--- Configuración Manual ---")
    print("Por favor, introduce los siguientes datos:")
    
    config = {}
    config["bot_platform"] = input("1. Plataforma (telegram/discord): ").lower().strip()
    config["bot_token"] = input("2. Token del Bot: ").strip()
    config["ai_provider"] = input("3. Proveedor de IA (gemini/openai/claude): ").lower().strip()
    config["ai_api_key"] = input("4. API Key de la IA: ").strip()
    config["ai_model"] = input("5. Modelo (ej: gemini-1.5-flash): ").strip()
    return config


def main():
    configurar_logging()
    logger = logging.getLogger("Main")

    print("==================================")
    print("   DETECTOR DE PHISHING - SETUP   ")
    print("==================================")
    print("¿Cómo deseas cargar la configuración?")
    print("1. Usar archivo 'config.json'")
    print("2. Introducir datos manualmente")
    
    opcion = input("\nSelecciona una opción (1 o 2): ").strip()
    
    config = {}

    # --- BLOQUE 1: CARGA DE DATOS ---
    if opcion == "1":
        archivo_json = 'config.json'
        if os.path.exists(archivo_json):
            try:
                with open(archivo_json, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"✅ Configuración cargada desde {archivo_json}")
            except json.JSONDecodeError:
                logger.error("❌ El archivo config.json está mal formateado.")
                return
        else:
            logger.error(f"❌ No se encuentra el archivo {archivo_json}")
            return
            
    elif opcion == "2":
        config = obtener_configuracion_manual()
    
    else:
        logger.warning("❌ Opción no válida seleccionada. Saliendo.")
        return

    # --- BLOQUE 2: VALIDACIÓN ---
    logger.info("Validando configuración...")
    # 1. Definición de reglas
    claves_necesarias = ["ai_api_key", "ai_provider", "ai_model", "bot_platform", "bot_token"]
    valid_bot_platforms = ["telegram", "discord"]
    valid_ai_providers = ["gemini", "openai", "claude"]
    valid_ai_models = {
        "gemini": ["gemini-1.5-flash", "gemini-2.5-flash", "gemini-pro"],
        "openai": ["gpt-3.5-turbo", "gpt-4", "gpt-4o"],
        "claude": ["claude-2", "claude-3-opus", "claude-3-sonnet"]
    }

    # 2. Comprobar que no faltan campos
    for clave in claves_necesarias:
        if clave not in config or not config[clave]:
            logger.error(f"❌ Falta el parámetro obligatorio '{clave}' en la configuración.")
            return

    # 3. Validar valores permitidos
    if config["bot_platform"] not in valid_bot_platforms:
        logger.error(f"❌ Plataforma '{config['bot_platform']}' no válida.")
        logger.info(f"ℹ️  Opciones permitidas: {', '.join(valid_bot_platforms)}")
        return

    if config["ai_provider"] not in valid_ai_providers:
        logger.error(f"❌ Proveedor de IA '{config['ai_provider']}' no soportado.")
        logger.info(f"ℹ️  Opciones permitidas: {', '.join(valid_ai_providers)}")
        return

    proveedor_actual = config["ai_provider"]
    modelo_actual = config["ai_model"]
    
    # Verificamos si el modelo está en la lista del proveedor elegido
    if modelo_actual not in valid_ai_models[proveedor_actual]:
        logger.error(f"❌ El modelo '{modelo_actual}' no es válido para el proveedor '{proveedor_actual}'.")
        logger.info(f"ℹ️  Modelos disponibles para {proveedor_actual}: {', '.join(valid_ai_models[proveedor_actual])}")
        return

    logger.info("✅ Configuración validada correctamente.")

    # --- BLOQUE 3: INICIALIZACIÓN DE LA IA ---
    print(f"\nInicializando cerebro IA ({config['ai_provider']} - {config['ai_model']})...")
    try:
        cerebro = PhishingAI(
            ai_api_key=config["ai_api_key"], 
            ai_provider=config["ai_provider"],
            ai_model=config["ai_model"]
        )
    except Exception as e:
        logger.critical(f"❌ Error fatal al conectar con la IA: {e}")
        return

    # --- BLOQUE 4: ARRANQUE DEL BOT ---
    platform = config["bot_platform"]
    token = config["bot_token"]

    logger.info(f"🤖 Preparando arranque en plataforma: {platform.upper()}...")

    if platform == "telegram":
        # Instanciamos y ejecutamos Telegram
        try:
            telegram_bot = MyTelegramBot(token, cerebro)
            telegram_bot.run()
        except Exception as e:
            logger.critical(f"❌ Error al iniciar Telegram: {e}")

    elif platform == "discord":
        # Instanciamos y ejecutamos Discord
        try:
            discord_bot = MyDiscordBot(token, cerebro)
            discord_bot.run()
        except Exception as e:
            logger.critical(f"❌ Error al iniciar Discord: {e}")

if __name__ == "__main__":
    main()