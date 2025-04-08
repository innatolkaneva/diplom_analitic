import io
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import seaborn as sns
from config import USER_DATA, CHART_TYPES


async def create_and_send_chart(query, context):
    user_id = query.from_user.id
    df = USER_DATA[user_id]['dataframe']
    cols = USER_DATA[user_id]['selected_columns']
    chart_type = USER_DATA[user_id]['chart_type']
    color = context.user_data.get('color')
    if color is None:
        if 'settings' not in USER_DATA[user_id]:
            USER_DATA[user_id]['settings'] = {}
            USER_DATA[user_id]['settings']['color'] = 'blue'
        color = USER_DATA[user_id]['settings'].get('color', 'blue')
    if chart_type == 'pie' or chart_type == 'heatmap':
        await query.edit_message_text("Данный график будет стандартного цвета, независимо от выбранного пользователем")

    if chart_type == 'pie' and len(cols) != 2:
        await query.edit_message_text("Для круговой диаграммы необходимо выбрать ровно 2 столбца.")
        return
    elif chart_type == 'heatmap' and len(cols) < 3:
        await query.edit_message_text("Для тепловой карты необходимо выбрать минимум 3 столбца.")
        return
    elif chart_type == 'line' and len(cols) != 2:
        await query.edit_message_text("Для линейного графика необходимо выбрать ровно 2 столбца.")
        return

    plt.figure(figsize=(10, 6))
    try:
        generate_plot(df, cols, chart_type, color)

        x_data = df[cols[0]]
        unique_x = x_data.nunique()
        if unique_x > 20:
            plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=20))
        plt.xticks(rotation=45, ha='right')
        if len(cols) > 1:
            y_data = df[cols[1]]
            unique_y = y_data.nunique()
            if unique_y > 20:
                plt.gca().yaxis.set_major_locator(MaxNLocator(nbins=20))
            plt.yticks(rotation=0)

        sns.despine()
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300)
        buf.seek(0)

        await query.message.reply_photo(
            photo=buf,
            caption=f"График: {CHART_TYPES[chart_type]}"
        )
        buf.close()

    except Exception as e:
        await query.edit_message_text(f"Ошибка: {str(e)}")
    finally:
        plt.close()

def generate_plot(df, cols, chart_type, color):
    if chart_type == 'line':
        sns.lineplot(data=df, x=cols[0], y=cols[1], color=color)
        plt.title('Линейный график')
        plt.xlabel(cols[0])
        plt.ylabel(cols[1])

    elif chart_type == 'bar':
        sns.barplot(data=df, x=cols[0], y=cols[1] if len(cols) > 1 else None, color=color)
        plt.title('Столбчатый график')


    elif chart_type == 'scatter':
        sns.scatterplot(data=df, x=cols[0], y=cols[1] if len(cols) > 1 else df.index, color=color)
        plt.title('Точечный график')

    elif chart_type == 'hist':
        for col in cols:
            sns.histplot(data=df, x=col, kde=True, color=color)
        plt.title('Гистограмма')

    elif chart_type == 'box':
        sns.boxplot(data=df[cols], palette=[color] * len(cols))
        plt.title('Ящик с усами')
        plt.xticks(rotation=45)

    elif chart_type == 'heatmap':
        sns.heatmap(df[cols].corr(), annot=True, cmap='coolwarm')
        plt.title('Тепловая карта')
        plt.xticks(rotation=45)

    elif chart_type == 'pie':

        plt.pie(df[cols[1]], labels=df[cols[0]], autopct='%1.1f%%', startangle=90,
                colors=sns.color_palette("husl", len(df)))
        plt.axis('equal')
        plt.title('Круговая диаграмма')
