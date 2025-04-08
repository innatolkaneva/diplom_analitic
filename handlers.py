import os
import pandas as pd
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import USER_DATA, CHART_TYPES, COLOR_OPTIONS
from plotter import create_and_send_chart, generate_plot
from utils import load_file_with_encoding

logging.basicConfig(level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Отправьте CSV или Excel-файл — и я построю график."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Как использовать:\n"
        "1. Отправьте CSV/Excel\n"
        "2. Выберите столбцы и тип графика\n"
        "3. Получите изображение!"
    )


async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    file = update.message.document
    file_name = file.file_name

    if not file_name.endswith(('.csv', '.xlsx')):
        await update.message.reply_text("Формат файла должен быть CSV или Excel (.xlsx)")
        return

    await update.message.reply_text("⏳ Обрабатываю файл...")
    file_info = await context.bot.get_file(file.file_id)
    file_path = f"temp_{user_id}_{file_name}"
    await file_info.download_to_drive(file_path)

    try:
        df = load_file_with_encoding(file_path)
        for col in df.select_dtypes(include=['number']):
            df[col] = df[col].fillna(df[col].median())

        USER_DATA[user_id] = {'dataframe': df, 'file_path': file_path}
        await show_column_selection(update, df)

    except Exception as e:
        await update.message.reply_text(f"Ошибка при обработке: {str(e)}")

    if os.path.exists(file_path):
        os.remove(file_path)


async def show_column_selection(update: Update, df: pd.DataFrame):
    user_id = update.effective_user.id
    keyboard = [[InlineKeyboardButton(col, callback_data=f"col_{col}")] for col in df.columns]
    keyboard.append([InlineKeyboardButton("✅ Готово", callback_data="cols_done")])
    USER_DATA[user_id]['selected_columns'] = []

    await update.message.reply_text(
        "Выберите столбцы для графика:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def column_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in USER_DATA:
        await query.edit_message_text("Начните заново с отправки файла.")
        return

    if query.data.startswith("col_"):
        col = query.data[4:]
        selected = USER_DATA[user_id]['selected_columns']
        selected.remove(col) if col in selected else selected.append(col)
        selected_text = ", ".join(selected) or "нет"
        await query.edit_message_text(
            f"Выбраны: {selected_text}\nНажмите 'Готово'.",
            reply_markup=query.message.reply_markup
        )

    elif query.data == "cols_done":
        if not USER_DATA[user_id]['selected_columns']:
            await query.edit_message_text("Выберите хотя бы один столбец.")
            return
        await show_chart_type_selection(query)


async def show_chart_type_selection(query):
    keyboard = [[InlineKeyboardButton(name, callback_data=f"chart_{key}")]
                for key, name in CHART_TYPES.items()]
    await query.edit_message_text("Выберите тип графика:", reply_markup=InlineKeyboardMarkup(keyboard))


async def chart_type_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in USER_DATA:
        await query.edit_message_text("Начните заново с отправки файла.")
        return

    chart_type = query.data[6:]
    USER_DATA[user_id]['chart_type'] = chart_type
    await set_color(query, context)


async def set_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"color_{color}")]
        for color, name in COLOR_OPTIONS.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎨 Выберите цвет для вашего графика:",
        reply_markup=reply_markup
    )

# async def color_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     await query.answer()
#     user_id = query.from_user.id
#     selected_color = query.data.split("_")[1]  # Получаем выбранный цвет
#
#     if user_id not in USER_DATA:
#         await query.edit_message_text("Сначала отправьте файл")
#         return
#
#     if 'settings' not in USER_DATA[user_id]:
#         USER_DATA[user_id]['settings'] = {}
#     USER_DATA[user_id]['settings']['color'] = selected_color
#
#     await query.edit_message_text(
#         f"Выбран цвет: {COLOR_OPTIONS[selected_color]}\n"
#         "Строю график..."
#     )
#     await create_and_send_chart(query, context)
async def color_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in USER_DATA:
        await query.edit_message_text("Сначала отправьте файл")
        return

    color = query.data.split('_')[1]

    context.user_data['color'] = color

    if 'settings' not in USER_DATA[user_id]:
        USER_DATA[user_id]['settings'] = {}
    USER_DATA[user_id]['settings']['color'] = color
    await query.edit_message_text(
                 f"Выбран цвет: {COLOR_OPTIONS[color]}\n"
                 "Строю график..."
             )

    await create_and_send_chart(query, context)