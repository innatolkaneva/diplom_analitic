from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import BOT_TOKEN
from handlers import start, help_command, receive_file, column_callback, chart_type_callback, set_color, color_callback

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.ATTACHMENT, receive_file))
    application.add_handler(CallbackQueryHandler(column_callback, pattern=r"^col_|^cols_done"))
    application.add_handler(CallbackQueryHandler(chart_type_callback, pattern=r"^chart_"))
    application.add_handler(CallbackQueryHandler(color_callback, pattern=r"^color_"))
    application.run_polling()

if __name__ == "__main__":
    main()