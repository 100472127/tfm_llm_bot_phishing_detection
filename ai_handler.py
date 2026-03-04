import asyncio

try:
    from google import genai
except ImportError:
    genai = None

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

try:
    from anthropic import AsyncAnthropic
except ImportError:
    AsyncAnthropic = None


class PhishingAI:
    def __init__(self, ai_api_key, ai_provider, ai_model):
        """
        Inicializa el manejador de IA.
        
        :param ai_api_key: La clave API del servicio.
        :param ai_provider: "gemini", "openai", "anthropic".
        :param ai_model: El nombre específico del modelo (ej: "gpt-4", "claude-3-opus").
        """
        self.api_key = ai_api_key
        self.provider = ai_provider
        self.model_name = ai_model
        self.client = None

        self._inicializar_cliente()


    def _inicializar_cliente(self):
        """Configura el cliente específico según el proveedor."""
        if self.provider == "gemini":
            if genai is None:
                raise ImportError("La librería 'google.generativeai' no está instalada.")
            self.client = genai.Client(api_key=self.api_key)
            
        elif self.provider == "openai":
            if AsyncOpenAI is None:
                raise ImportError("La librería 'openai' no está instalada.")
            self.client = AsyncOpenAI(api_key=self.api_key)
            
        elif self.provider == "anthropic":
            if AsyncAnthropic is None:
                raise ImportError("La librería 'anthropic' no está instalada.")
            self.client = AsyncAnthropic(api_key=self.api_key)
            
        else:
            raise ValueError(f"Proveedor de IA '{self.provider}' no soportado.")


    async def analyze_message(self, texto):
        """
        Método único y universal que llama el Bot.
        """
        # Creamos el prompt
        prompt = (
            "### ROL ###\n"
            "Actúa como un Analista Senior de SOC especializado en Inteligencia de Amenazas y Phishing.\n\n"
            
            "### TAREA ###\n"
            "Tu objetivo es clasificar el riesgo de un mensaje recibido por un usuario siguiendo estrictamente "
            "la taxonomía de riesgo definida a continuación.\n\n"
            
            "### TAXONOMÍA DE RIESGO ###\n"
            "1. NIVEL: BAJO -> Mensajes de remitentes conocidos, sin urgencia artificial, sin enlaces sospechosos o con enlaces a dominios oficiales verificados.\n"
            "2. NIVEL: MEDIO -> Mensajes con lenguaje persuasivo, errores gramaticales leves, o enlaces que usan acortadores (bit.ly, t.co) pero sin contenido malicioso evidente.\n"
            "3. NIVEL: ALTO -> Suplantación de identidad clara (spoofing), urgencia extrema ('cuenta bloqueada'), enlaces que imitan dominios oficiales (typosquatting como 'g00gle.com') o solicitudes de credenciales/pagos.\n\n"
            
            "### FORMATO DE RESPUESTA OBLIGATORIO ###\n"
            "Solo responde en el siguiente formato, sin texto introductorio ni conclusiones:\n"
            "NIVEL: [BAJO/MEDIO/ALTO]\n"
            "RAZÓN: [Breve explicación en español del vector de ataque o la falta de riesgo]\n\n"
            
            "### EJEMPLOS ###\n"
            "Mensaje: 'Hola, te mando el link de la reunión de Zoom: zoom.us/j/123'\n"
            "NIVEL: BAJO\n"
            "RAZÓN: El dominio es oficial de Zoom y el contexto es puramente informativo sin signos de urgencia.\n\n"
            
            "Mensaje: '¡URGENTE! Tu cuenta de Netflix será suspendida. Paga aquí: netfIix-pagos.com'\n"
            "NIVEL: ALTO\n"
            "RAZÓN: Uso de typosquatting (letra 'I' en lugar de 'l') y creación de urgencia artificial para obtener datos bancarios.\n\n"
            
            "### MENSAJE A ANALIZAR ###\n"
            f"'{texto}'"
        )

        max_intentos = 3
        intento_actual = 0

        while intento_actual < max_intentos:
            try:
                if self.provider == "gemini":
                    return await self._query_gemini(prompt)
                elif self.provider == "openai":
                    return await self._query_openai(prompt)
                elif self.provider == "claude":
                    return await self._query_claude(prompt)  

            except Exception as e:    
                intento_actual += 1
                error_str = str(e).lower()            
                # Si la API está sobrecargada, esperamos 5 segundos y reintentamos
                if ("503" in error_str or "429" in error_str or "overloaded" in error_str):
                    if intento_actual < max_intentos:
                        await asyncio.sleep(5)
                else:
                    # Si es un error 404 u otro devolvemos error
                    return None
        return None

    # --- Funciones para hacer las llamadas a las APIs con las IAs ---

    async def _query_gemini(self, prompt):
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text

    async def _query_openai(self, prompt):
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content

    async def _query_claude(self, prompt):
        response = await self.client.messages.create(
            model=self.model_name,
            max_tokens=500, # Aumentado de 10 a 500
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
