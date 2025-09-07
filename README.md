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

- **Git**: Necesitarás tener Git instalado. En Termux, puedes instalarlo con `pkg install git`.
- Python 3.8 o superior.
- Una cuenta de Google.
- Un bot de Telegram (créalo hablando con @BotFather).

### 2. Instalación

1.  **Clonar el Repositorio**
    Abre tu terminal (o Termux) y clona el repositorio con el siguiente comando:
    ```bash
    git clone https://github.com/elmendezz/telegram-bot-url-downloader.git
    ```
    Luego, navega al directorio del proyecto:
    ```bash
    cd telegram-bot-url-downloader
    ```

2.  **Instalar Dependencias**
    Ejecuta el siguiente comando para instalar las librerías necesarias:
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

# Telegram & Google Drive Downloader Bot

This is a multifunctional Telegram bot designed to download files from direct links, MediaFire, and Google Drive, manage them, and upload them to a specific folder in your Google Drive account. Additionally, it sends the downloaded files directly to the Telegram chat if they do not exceed the size limit.

## ✨ Features

- **Download from Multiple Sources**:
  - **Direct Links**: Download any file from a direct URL.
  - **MediaFire**: Automatically resolves MediaFire links to get the direct download link.
  - **Google Drive**: Quickly copies files from Google Drive to your own account without needing to download and re-upload them.
- **Google Drive Integration**:
  - All files are uploaded to a configurable folder in your Google Drive (defaults to `TelegramDownloads`).
  - **Duplicate Handling**: Avoids uploading duplicate files (except for images and videos) if one with the same name and size already exists.
  - **Automatic Renaming**: Automatically renames images and videos if a file with the same name already exists to prevent overwriting.
- **Send to Telegram**:
  - Downloaded files are sent as documents to the Telegram chat.
  - **Size Limit**: Does not attempt to upload files larger than 1.9 GB to Telegram to avoid errors, notifying the user that the file is only available on Drive.
- **Useful Commands**:
  - `/start`: Displays a welcome message with instructions.
  - `/download <URL>`: Starts the download from the provided URL.
  - `/save`: When replying to a message with a file (document or photo), it saves it to your Google Drive.
- **Real-Time Feedback**:
  - Shows a progress bar during the download.
  - Notifies at each step of the process (resolving link, downloading, uploading, etc.).
- **Activity Logging**:
  - All operations (successful and failed) are logged in a `download_log.txt` file.

## 🚀 Setup

Follow these steps to get your bot up and running.

### 1. Prerequisites

- **Git**: You will need Git installed. In Termux, you can install it with `pkg install git`.
- Python 3.8 or higher.
- A Google account.
- A Telegram bot (create one by talking to @BotFather).

### 2. Installation

1.  **Clone the Repository**
    Open your terminal (or Termux) and clone the repository with the following command:
    ```bash
    git clone https://github.com/elmendezz/telegram-bot-url-downloader.git
    ```
    Then, navigate to the project directory:
    ```bash
    cd telegram-bot-url-downloader
    ```

2.  **Install Dependencies**
    Run the following command to install the necessary libraries:
```bash
pip install python-telegram-bot requests beautifulsoup4 google-api-python-client google-auth-oauthlib google-auth-httplib2
```

### 3. Google Drive API Configuration

1.  Go to the Google API Console.
2.  Create a new project (or select an existing one).
3.  Search for and enable the **Google Drive API**.
4.  Go to "Credentials" in the left-hand menu.
5.  Click "Create credentials" -> "OAuth client ID".
6.  Select "Desktop app" as the application type.
7.  Download the credentials JSON file. Rename it to `credentials.json` and place it in the same folder as `bot.py`.

### 4. Bot Configuration

Open the `bot.py` file and edit the line 35 with your Telegram bot token:

```python
BOT_TOKEN = 'TU_TOKEN_AQUI'
```

### 5. First Run and Authentication

The first time you run the bot, you will need to authorize access to your Google Drive account.

1.  Run the script from your terminal:
    ```bash
    python bot.py
    ```
2.  A URL will be printed in the console. Copy and paste it into your browser.
3.  Log in with your Google account and grant the requested permissions.
4.  After authorization, you will be redirected to a page that might show an error (this is normal). The bot will create a `token.pickle` file in the directory. This file will store your access credentials for future runs.

That's it! Your bot is now up and running.

## 🤖 Commands

- `/start`
  - Displays the welcome message and a brief user guide.

- `/download <URL>`
  - Downloads the content from the `<URL>`.
  - *Example*: `/download https://example.com/archive.zip`

- `/save`
  - Must be used in reply to a message containing a file (document or photo).
  - Saves that file directly to your Google Drive.

## 📝 Notes
- The bot is designed to be asynchronous, allowing it to handle multiple tasks without blocking.

---
