import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Envíame la URL del video que quieres descargar.')

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    video_url = update.message.text
    await update.message.reply_text('Descargando el video, por favor espera...')
    
    current_dir = os.getcwd()
    output_dir = os.path.join(current_dir, 'Download')  
    video_path = await download_video(video_url, output_dir)
    
    if video_path == 'network_error':
        await update.message.reply_text('Error de red al intentar descargar el video. Por favor, verifica tu conexión a Internet.')
    elif video_path:
        with open(video_path, 'rb') as video_file:
            await context.bot.send_video(chat_id=update.message.chat_id, video=video_file)
        os.remove(video_path)
    else:
        await update.message.reply_text('Error al descargar el video.')

async def download_video(url: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    ydl_opts = {
        'format': 'best/bestvideo+bestaudio',
        'outtmpl': os.path.join(output_dir, '%(title).50s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info)
            return video_path
    except Exception as e:
        print(f"Error: {e}")
        if isinstance(e, OSError) and e.errno == 113:
            return 'network_error'
        return None

def main() -> None:
    application = Application.builder().token("7197823992:AAHNugUoPlT4momm6ZmRFEAhCbHpU3-OW8o").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))

    application.run_polling()

if __name__ == '__main__':
    main()