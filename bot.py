# BOT Version:5
# Change log:
# - Se incrementó el 'timeout' de 10 a 30 segundos en requests.head() para descargas.
# - Se agregó un manejo de error específico para el 'Timeout' para un mensaje más claro.
# Dependencias:
# - requests
# - telegram
# - bs4
# - google-api-python-client
# - google-auth-oauthlib
# - google-auth-httplib2
# - pickle
# - io
# - os
# - datetime
# - re

import re
import requests
from bs4 import BeautifulSoup
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import os
import io
import datetime
import time

# --- Google Drive ---
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

BOT_TOKEN = 'TU_TOKEN_AQUI'
SCOPES = ['https://www.googleapis.com/auth/drive.file']
LOG_FILE = "download_log.txt"
FOLDER_NAME = "TelegramDownloads"  # Carpeta fija en tu Drive

# -------------------- GOOGLE DRIVE --------------------
def get_gdrive_service():
    """Autentica y devuelve el servicio de Google Drive."""
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(open_browser=False, port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build("drive", "v3", credentials=creds)

def get_or_create_folder(service, folder_name):
    """Busca o crea la carpeta en Google Drive."""
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    if files:
        return files[0]["id"]
    # Crear si no existe
    folder_metadata = {"name": folder_name, "mimeType": "application/vnd.google-apps.folder"}
    folder = service.files().create(body=folder_metadata, fields="id").execute()
    return folder.get("id")

def upload_to_gdrive(file_path, filename):
    """Sube un archivo a Google Drive dentro de la carpeta fija y maneja duplicados."""
    service = get_gdrive_service()
    folder_id = get_or_create_folder(service, FOLDER_NAME)

    # Lógica para manejar duplicados
    file_size = os.path.getsize(file_path)
    file_extension = os.path.splitext(filename)[1].lower()
    
    # Excepciones para duplicar archivos de imagen y video
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv']
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    
    is_media_file = file_extension in video_extensions or file_extension in image_extensions

    if not is_media_file:
        query = f"name='{filename}' and '{folder_id}' in parents and trashed=false"
        results = service.files().list(q=query, fields="files(id, name, size)").execute()
        existing_files = results.get("files", [])

        for existing_file in existing_files:
            if existing_file['size'] == str(file_size):
                file_id = existing_file['id']
                # Otorgar permiso de lectura pública si aún no lo tiene
                try:
                    service.permissions().create(
                        fileId=file_id,
                        body={"role": "reader", "type": "anyone"},
                    ).execute()
                except Exception as e:
                    print(f"Error al intentar otorgar permisos a un archivo existente: {e}")
                return f"https://drive.google.com/file/d/{file_id}/view?usp=sharing", "exists"
    
    # Si es un medio o no existe un archivo con el mismo nombre y tamaño, se sube
    new_filename = filename
    if is_media_file:
        base_name, ext = os.path.splitext(filename)
        counter = 1
        while True:
            query = f"name='{new_filename}' and '{folder_id}' in parents and trashed=false"
            results = service.files().list(q=query, fields="files(id)").execute()
            if not results.get("files"):
                break
            new_filename = f"{base_name} ({counter}){ext}"
            counter += 1

    file_metadata = {"name": new_filename, "parents": [folder_id]}
    media = MediaFileUpload(file_path, resumable=True)
    uploaded = service.files().create(
        body=file_metadata, media_body=media, fields="id"
    ).execute()
    file_id = uploaded.get("id")
    
    service.permissions().create(
        fileId=file_id,
        body={"role": "reader", "type": "anyone"},
    ).execute()
    
    return f"https://drive.google.com/file/d/{file_id}/view?usp=sharing", "uploaded"

def copy_gdrive_file(file_id: str, new_name: str = None):
    """Copia un archivo dentro de Drive en la carpeta fija."""
    service = get_gdrive_service()
    folder_id = get_or_create_folder(service, FOLDER_NAME)
    body = {"parents": [folder_id]}
    if new_name:
        body["name"] = new_name
    copied = service.files().copy(fileId=file_id, body=body, fields="id").execute()
    new_id = copied.get("id")
    service.permissions().create(
        fileId=new_id,
        body={"role": "reader", "type": "anyone"},
    ).execute()
    return f"https://drive.google.com/file/d/{new_id}/view?usp=sharing"

def extract_gdrive_id(url: str) -> str:
    """Extrae el ID de un link de Google Drive."""
    patterns = [
        r"drive\.google\.com/file/d/([a-zA-Z0-9_-]+)",
        r"drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)",
        r"drive\.google\.com/uc\?id=([a-zA-Z0-9_-]+)",
    ]
    for p in patterns:
        match = re.search(p, url)
        if match:
            return match.group(1)
    return None

# -------------------- UTILS --------------------
def get_progress_bar(progress, total, length=20):
    if total == 0:
        return '*0%*'
    percent = (progress / total) * 100
    filled_length = int(length * progress // total)
    bar = '█' * filled_length + '░' * (length - filled_length)
    return f'`|{bar}| {percent:.2f}%`'

def resolve_mediafire(url: str) -> str:
    """Devuelve el enlace directo de MediaFire."""
    try:
        page = requests.get(url, timeout=15)
        page.raise_for_status()
        match = re.search(r'href="(https://download[^"]+)"', page.text)
        if match:
            return match.group(1)
        soup = BeautifulSoup(page.text, 'html.parser')
        download_button = soup.find('a', {'id': 'downloadButton'})
        if download_button and download_button['href']:
            return download_button['href']
    except requests.exceptions.RequestException as e:
        print(f"Error resolviendo MediaFire: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado resolviendo MediaFire: {e}")
        return None

def log_event(text: str):
    """Guarda un registro en download_log.txt"""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {text}\n")
        
# -------------------- MAIN BOT --------------------
async def download_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    local_filename = None

    if not context.args:
        await update.message.reply_text('Por favor, envía el comando /download seguido de un enlace.', parse_mode=telegram.constants.ParseMode.MARKDOWN)
        return

    url = context.args[0]
    
    # Caso Google Drive
    if "drive.google.com" in url:
        file_id = extract_gdrive_id(url)
        if not file_id:
            await update.message.reply_text("❌ No pude extraer el ID del enlace de Google Drive.", parse_mode=telegram.constants.ParseMode.MARKDOWN)
            return
        await update.message.reply_text("⏳ Copiando archivo en tu Google Drive...", parse_mode=telegram.constants.ParseMode.MARKDOWN)
        try:
            new_link = copy_gdrive_file(file_id)
            await update.message.reply_text(f"✅ Copiado en tu Drive (carpeta *{FOLDER_NAME}*): {new_link}", parse_mode=telegram.constants.ParseMode.MARKDOWN)
            log_event(f"GDrive Copia: {url} -> {new_link}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error copiando en Drive: {e}", parse_mode=telegram.constants.ParseMode.MARKDOWN)
            log_event(f"Error GDrive copia: {url} | {e}")
        return

    # Caso MediaFire
    if "mediafire.com" in url:
        await update.message.reply_text("⏳ Resolviendo enlace de MediaFire...", parse_mode=telegram.constants.ParseMode.MARKDOWN)
        direct_url = resolve_mediafire(url)
        if not direct_url:
            await update.message.reply_text("❌ No pude resolver el enlace de MediaFire. Es probable que la URL haya caducado o sea incorrecta.", parse_mode=telegram.constants.ParseMode.MARKDOWN)
            log_event(f"Error MediaFire: {url}")
            return
        url = direct_url

    # Descarga normal
    local_filename = url.split('/')[-1] or 'file_downloaded'
    local_filename = re.sub(r'[\\/:*?"<>|]', '', local_filename) # Limpiar el nombre de archivo de caracteres no permitidos

    # Headers para simular un navegador
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive'
    }

    try:
        response = requests.head(url, allow_redirects=True, timeout=30, headers=headers)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))

        message = await update.message.reply_text(f'Descargando: {get_progress_bar(0, total_size)}', parse_mode=telegram.constants.ParseMode.MARKDOWN)
        
        # --- Lógica de reintentos para la descarga ---
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # --- Lógica de descarga reanudable ---
                bytes_downloaded = 0
                if os.path.exists(local_filename):
                    bytes_downloaded = os.path.getsize(local_filename)
                
                # Añadir header 'Range' para continuar la descarga
                download_headers = headers.copy()
                if bytes_downloaded > 0:
                    download_headers['Range'] = f'bytes={bytes_downloaded}-'

                chunk_size = 5 * 1024 * 1024
                with requests.get(url, stream=True, timeout=600, headers=download_headers) as r:
                    r.raise_for_status()
                    with open(local_filename, 'ab') as f: # 'ab' para añadir al archivo si ya existe
                        last_update_percent = -1
                        for chunk in r.iter_content(chunk_size=chunk_size):
                            f.write(chunk)
                            bytes_downloaded += len(chunk)
                            current_percent = int((bytes_downloaded / total_size) * 10)
                            if current_percent > last_update_percent:
                                progress_text = get_progress_bar(bytes_downloaded, total_size)
                                try:
                                    await context.bot.edit_message_text(
                                        chat_id=chat_id,
                                        message_id=message.message_id,
                                        text=f'Descargando: {progress_text}',
                                        parse_mode=telegram.constants.ParseMode.MARKDOWN
                                    )
                                except telegram.error.BadRequest:
                                    pass
                                last_update_percent = current_percent
                break # Si la descarga fue exitosa, salimos del bucle de reintentos
            except requests.exceptions.Timeout as e:
                if attempt < max_retries - 1:
                    wait_time = 5 * (2 ** attempt) # Espera exponencial: 5s, 10s, 20s...
                    await context.bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text=f"⏳ Timeout. Reanudando descarga en {wait_time}s... (Intento {attempt + 2}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    raise e # Si se superan los reintentos, relanzamos la excepción para que sea manejada abajo

        # Subir a Google Drive
        gdrive_link, status = upload_to_gdrive(local_filename, local_filename)
        
        if status == "exists":
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message.message_id,
                text=f'✅ *¡El archivo ya existía en tu Google Drive!*\n\n{gdrive_link}\n\n📤 Enviando el archivo a Telegram...',
                parse_mode=telegram.constants.ParseMode.MARKDOWN
            )
            log_event(f"Archivo existente: {url} -> {gdrive_link}")
        else:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message.message_id,
                text=f'✅ Subido a Google Drive (carpeta *{FOLDER_NAME}*): {gdrive_link}\n\n📤 Enviando el archivo a Telegram...',
                parse_mode=telegram.constants.ParseMode.MARKDOWN
            )
            log_event(f"Subido a Drive: {url} -> {gdrive_link}")
        
        # Enviar también a Telegram como documento
        with open(local_filename, 'rb') as f:
            await context.bot.send_document(chat_id=chat_id, document=f, filename=local_filename)

        # Mensaje final
        await context.bot.send_message(
            chat_id=chat_id,
            text="✅ Archivo subido a Drive y enviado a Telegram.",
            parse_mode=telegram.constants.ParseMode.MARKDOWN
        )

    except requests.exceptions.HTTPError as e:
        error_message = f'❌ Ocurrió un error HTTP durante la descarga: {e}. Puede que la URL no sea válida o esté bloqueada.'
        print(error_message)
        await update.message.reply_text(error_message, parse_mode=telegram.constants.ParseMode.MARKDOWN)
        log_event(f"Error de descarga HTTP: {url} | {e}")
    except requests.exceptions.Timeout as e:
        error_message = f'❌ ¡Tiempo de espera agotado! El servidor tardó demasiado en responder: {e}.'
        print(error_message)
        await update.message.reply_text(error_message, parse_mode=telegram.constants.ParseMode.MARKDOWN)
        log_event(f"Error de Timeout: {url} | {e}")
    except requests.exceptions.RequestException as e:
        error_message = f'❌ Ocurrió un error de conexión con la URL: {e}'
        print(error_message)
        await update.message.reply_text(error_message, parse_mode=telegram.constants.ParseMode.MARKDOWN)
        log_event(f"Error de descarga: {url} | {e}")
    except Exception as e:
        error_message = f'❌ Ocurrió un error inesperado durante la descarga: {e}'
        print(error_message)
        await update.message.reply_text(error_message, parse_mode=telegram.constants.ParseMode.MARKDOWN)
        log_event(f"Error inesperado durante la descarga: {url} | {e}")
    finally:
        if local_filename and os.path.exists(local_filename):
            os.remove(local_filename)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f'¡Hola! Soy tu bot de descargas 🤖\n\n'
        f'Envía /download seguido de un enlace:\n'
        f'* Google Drive -> copia directo a tu Drive\n'
        f'* MediaFire -> resuelve y sube a tu Drive\n'
        f'* Enlaces directos -> descarga y sube a tu Drive\n'
        f'* Y ahora, con el comando /save, puedes guardar archivos subidos directamente a tu Drive.\n\n'
        f'Todo se guardará en la carpeta *{FOLDER_NAME}* en tu Google Drive ✅\n'
        f'Si Drive falla -> se envía directo a Telegram.\n'
        f'Cada acción queda registrada en `download_log.txt`.\n\n'
        f'Además, ya no crearé duplicados innecesarios. 😉',
        parse_mode=telegram.constants.ParseMode.MARKDOWN
    )

async def save_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    reply_to_message = message.reply_to_message
    
    if not reply_to_message:
        await message.reply_text("Por favor, responde a un archivo con el comando /save para guardarlo en Google Drive.")
        return

    # Check for document or photo
    file = None
    file_name = None
    if reply_to_message.document:
        file = reply_to_message.document
        file_name = file.file_name
    elif reply_to_message.photo:
        file = reply_to_message.photo[-1]  # Get the highest resolution photo
        file_name = f"photo_{file.file_unique_id}.jpg"
    else:
        await message.reply_text("❌ No pude encontrar un archivo (documento o foto) en el mensaje al que respondiste.")
        return
        
    local_path = file_name
    try:
        await message.reply_text("⏳ Descargando archivo desde Telegram...")
        file_obj = await file.get_file()
        await file_obj.download_to_drive(local_path)
        
        await message.reply_text("⏳ Subiendo a Google Drive...")
        gdrive_link, status = upload_to_gdrive(local_path, file_name)
        
        if status == "exists":
            await message.reply_text(f"✅ ¡El archivo ya existía en tu Google Drive!\n\n{gdrive_link}")
            log_event(f"Archivo existente (save): {file_name} -> {gdrive_link}")
        else:
            await message.reply_text(f"✅ ¡Archivo guardado en Google Drive!\n\n{gdrive_link}")
            log_event(f"Guardado (save): {file_name} -> {gdrive_link}")

    except Exception as e:
        await message.reply_text(f"❌ Ocurrió un error al guardar el archivo: {e}")
        log_event(f"Error al guardar archivo (save): {file_name} | {e}")
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('download', download_and_send))
    application.add_handler(CommandHandler('save', save_command))
    application.run_polling(poll_interval=3)

if __name__ == '__main__':
    main()
