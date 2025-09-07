# Bot de Descargas para Telegram y Google Drive

Este es un bot de Telegram multifuncional diseñado para descargar archivos desde enlaces directos, MediaFire y Google Drive, gestionarlos y subirlos a una carpeta específica en tu cuenta de Google Drive. Además, envía los archivos descargados directamente al chat de Telegram si no superan el límite de tamaño.

## ✨ Características

- **Descarga desde Múltiples Fuentes**:
  - **Enlaces Directos**: Descarga cualquier archivo desde una URL directa.
  - **MediaFire**: Resuelve automáticamente los enlaces de MediaFire para obtener el link de descarga directa.
  - **Google Drive**: Realiza una copia rápida de archivos de Google Drive a tu propia cuenta, sin necesidad de descargarlos y volverlos a subir.
- **Integración con Google Drive**:
  - Todos los archivos se suben a una carpeta configurable en tu Google Drive (`TelegramDownloads` por defecto).
  - **Manejo de Duplicados**: Evita subir archivos duplicados (excepto imágenes y videos) si ya existe uno con el mismo nombre y tamaño.
  - **Renombrado Automático**: Renombra automáticamente imágenes y videos si ya existe un archivo con el mismo nombre para evitar sobreescrituras.
- **Envío a Telegram**:
  - Los archivos descargados se envían como documentos al chat de Telegram.
  - **Límite de Tamaño**: No intenta subir archivos de más de 1.9 GB a Telegram para evitar errores, notificando al usuario que el archivo solo está disponible en Drive.
- **Comandos Útiles**:
  - `/start`: Muestra un mensaje de bienvenida con instrucciones.
  - `/download <URL>`: Inicia la descarga desde la URL proporcionada.
  - `/save`: Respondiendo a un archivo (documento o foto) en Telegram, lo guarda en tu Google Drive.
- **Feedback en Tiempo Real**:
  - Muestra una barra de progreso durante la descarga.
  - Notifica cada paso del proceso (resolviendo enlace, descargando, subiendo, etc.).
- **Registro de Actividad**:
  - Todas las operaciones (exitosas y fallidas) se registran en un archivo `download_log.txt`.

## 🚀 Configuración

Sigue estos pasos para poner en marcha tu bot.

### 1. Prerrequisitos

- Python 3.8 o superior.
- Una cuenta de Google.
- Un bot de Telegram (créalo hablando con @BotFather).

### 2. Instalación de Dependencias

Clona o descarga este repositorio y ejecuta el siguiente comando para instalar las librerías necesarias:

```bash
pip install python-telegram-bot requests beautifulsoup4 google-api-python-client google-auth-oauthlib google-auth-httplib2
```

### 3. Configuración de la API de Google Drive

1.  Ve a la Consola de APIs de Google.
2.  Crea un nuevo proyecto (o selecciona uno existente).
3.  Busca y habilita la **API de Google Drive**.
4.  Ve a "Credenciales" en el menú de la izquierda.
5.  Haz clic en "Crear credenciales" -> "ID de cliente de OAuth".
6.  Selecciona "Aplicación de escritorio" como tipo de aplicación.
7.  Descarga el archivo JSON de credenciales. Renómbralo a `credentials.json` y colócalo en la misma carpeta que `bot.py`.

### 4. Configuración del Bot

Abre el archivo `bot.py` y edita la siguiente línea con el token de tu bot de Telegram:

```python
# Reemplaza 'TU_BOT_TOKEN' con el token que te dio BotFather
BOT_TOKEN = 'TU_BOT_TOKEN'
```

### 5. Primera Ejecución y Autenticación

La primera vez que ejecutes el bot, necesitarás autorizar el acceso a tu cuenta de Google Drive.

1.  Ejecuta el script desde tu terminal:
    ```bash
    python bot.py
    ```
2.  Se imprimirá una URL en la consola. Cópiala y pégala en tu navegador.
3.  Inicia sesión con tu cuenta de Google y concede los permisos solicitados.
4.  Después de la autorización, serás redirigido a una página que podría mostrar un error (esto es normal). El bot creará un archivo `token.pickle` en el directorio. Este archivo almacenará tus credenciales de acceso para futuras ejecuciones.

¡Listo! Tu bot ya está en funcionamiento.

## 🤖 Comandos

- `/start`
  - Muestra el mensaje de bienvenida y una breve guía de uso.

- `/download <URL>`
  - Descarga el contenido de la `<URL>`.
  - *Ejemplo*: `/download https://example.com/archivo.zip`

- `/save`
  - Debe ser usado como respuesta a un mensaje que contenga un archivo (documento o foto).
  - Guarda ese archivo directamente en tu Google Drive.

## 📝 Notas
- El bot está diseñado para ser asíncrono, lo que le permite manejar múltiples tareas sin bloquearse.

---