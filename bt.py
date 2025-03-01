from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
import math

# Ваш токен
TOKEN = "8117266193:AAFwa_oo4U5TcfZXIFdek30A_tF1xnHgN60"

# Состояния для ConversationHandler
RADIUS, ARC, EDGE = range(3)
TOLERANCE, PASSES = range(2)
HOLES_ON_TAPE, HOLES_IN_TEMPLATE = range(2)
DIFFERENCE_RADIUS, DIFFERENCE_ARC = range(5, 7)  # Новые состояния

# Обновленная клавиатура
main_keyboard = ReplyKeyboardMarkup(
    [["Разница дуги"],
     ["Шаблон", "Шаги шаблона", "Разгон шаблона"]],
    resize_keyboard=True
)

# Обработчик команды /start
async def start(update: Update, context: CallbackContext) -> int:
    context.user_data.clear()
    await update.message.reply_text("Внешний радиус:", reply_markup=main_keyboard)
    return RADIUS

# Обработчик ответа на вопрос "Радиус?"
async def get_radius(update: Update, context: CallbackContext) -> int:
    try:
        radius = float(update.message.text)
        context.user_data["radius"] = radius
        await update.message.reply_text("Расстояние между креплениями:")
        return ARC
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.", reply_markup=main_keyboard)
        return RADIUS

# Обработчик ответа на вопрос "Дуга?"
async def get_arc(update: Update, context: CallbackContext) -> int:
    try:
        arc = float(update.message.text)
        context.user_data["arc"] = arc
        await update.message.reply_text("Отступ крепления от края:")
        return EDGE
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.", reply_markup=main_keyboard)
        return ARC

# Обработчик ответа на вопрос "Отступ?"
async def get_edge(update: Update, context: CallbackContext) -> int:
    try:
        edge = float(update.message.text)
        context.user_data["edge"] = edge

        # Получаем значения из контекста
        radius = context.user_data["radius"]
        initial_arc = context.user_data["arc"]
        edge = context.user_data["edge"]

        # Выполняем 20 расчетов
        results = []
        for i in range(1, 21):  # 20 расчетов
            current_arc = initial_arc * i  # Увеличиваем дугу
            result = 2 * (radius - edge) * math.sin((current_arc / (radius - edge)) / 2)
            result_rounded = round(result, 1)  # Округляем до одного знака
            results.append(f"{result_rounded}")  # Добавляем только результат

        # Отправляем результаты пользователю (в столбик)
        await update.message.reply_text("Результаты расчетов:\n" + "\n".join(results), reply_markup=main_keyboard)
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.", reply_markup=main_keyboard)
        return EDGE

# Обработчик кнопки "Разгон шаблона"
async def start_template_run(update: Update, context: CallbackContext) -> int:
    context.user_data.clear()
    await update.message.reply_text("Погрешность:", reply_markup=main_keyboard)
    return TOLERANCE

# Обработчик ответа на вопрос "Погрешность?"
async def get_tolerance(update: Update, context: CallbackContext) -> int:
    try:
        tolerance = float(update.message.text)
        context.user_data["tolerance"] = tolerance
        await update.message.reply_text("Сколько проходов?")
        return PASSES
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.", reply_markup=main_keyboard)
        return TOLERANCE

# Обработчик ответа на вопрос "Сколько проходов?"
async def get_passes(update: Update, context: CallbackContext) -> int:
    try:
        passes = float(update.message.text)
        if passes <= 0:
            await update.message.reply_text("Пожалуйста, введите положительное число.", reply_markup=main_keyboard)
            return PASSES

        tolerance = context.user_data["tolerance"]

        # Вычисляем значения
        step = tolerance / passes
        results = []
        for i in range(1, int(passes) + 1):
            value = step * i
            results.append(f"{round(value, 1)}")  # Округляем до одного знака

        # Отправляем результаты пользователю
        await update.message.reply_text("Результаты разгона шаблона:\n" + "   ".join(results), reply_markup=main_keyboard)
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.", reply_markup=main_keyboard)
        return PASSES

# Обработчик кнопки "Шаги шаблона"
async def start_template_steps(update: Update, context: CallbackContext) -> int:
    context.user_data.clear()
    await update.message.reply_text("Количество отверстий на ленте:", reply_markup=main_keyboard)
    return HOLES_ON_TAPE

# Обработчик ответа на вопрос "Количество отверстий на ленте?"
async def get_holes_on_tape(update: Update, context: CallbackContext) -> int:
    try:
        holes_on_tape = int(update.message.text)
        if holes_on_tape <= 0:
            await update.message.reply_text("Пожалуйста, введите положительное число.", reply_markup=main_keyboard)
            return HOLES_ON_TAPE
        context.user_data["holes_on_tape"] = holes_on_tape
        await update.message.reply_text("Количество отверстий в шаблоне:")
        return HOLES_IN_TEMPLATE
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите целое число.", reply_markup=main_keyboard)
        return HOLES_ON_TAPE

# Обработчик ответа на вопрос "Количество отверстий в шаблоне?"
async def get_holes_in_template(update: Update, context: CallbackContext) -> int:
    try:
        holes_in_template = int(update.message.text)
        if holes_in_template <= 0:
            await update.message.reply_text("Пожалуйста, введите положительное число.", reply_markup=main_keyboard)
            return HOLES_IN_TEMPLATE

        holes_on_tape = context.user_data["holes_on_tape"]

        # Формируем отчет
        results = []
        current_value = holes_in_template
        while current_value <= holes_on_tape:
            results.append(str(current_value))
            current_value += (holes_in_template - 1)

        # Вычисляем число в скобках
        ratio = round(holes_on_tape / (holes_in_template - 1), 1)
        results.append(f"({ratio})")

        # Отправляем результаты пользователю
        await update.message.reply_text("Результаты шагов шаблона:\n" + "  ".join(results), reply_markup=main_keyboard)
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите целое число.", reply_markup=main_keyboard)
        return HOLES_IN_TEMPLATE

# Новые обработчики для кнопки "Разница дуги"
async def start_difference(update: Update, context: CallbackContext) -> int:
    context.user_data.clear()
    await update.message.reply_text("Внешний радиус:")
    return DIFFERENCE_RADIUS

async def get_difference_radius(update: Update, context: CallbackContext) -> int:
    try:
        radius = float(update.message.text)
        context.user_data["diff_radius"] = radius
        await update.message.reply_text("Внешняя дуга:")
        return DIFFERENCE_ARC
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.", reply_markup=main_keyboard)
        return DIFFERENCE_RADIUS

async def get_difference_arc(update: Update, context: CallbackContext) -> int:
    try:
        arc = float(update.message.text)
        radius = context.user_data["diff_radius"]

        # Расчет вариантов корректора
        variants = [
            radius * 2 * math.pi,
            radius * math.pi,
            radius * math.pi / 2,
            radius * 2 * math.pi / 3,
            radius * 2 * math.pi / 6
        ]

        closest = min(variants, key=lambda x: abs(x - arc))
        difference = arc - closest
        angle = (arc * (180 / math.pi)) / radius

        # Округляем до целых чисел
        await update.message.reply_text(
            f"Разница дуг:      {round(difference)}\n"
            f"Угол:      {round(angle)}°",
            reply_markup=main_keyboard
        )
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.", reply_markup=main_keyboard)
        return DIFFERENCE_ARC

def main():
    application = Application.builder().token(TOKEN).build()

    # Обработчики для существующих функций
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), MessageHandler(filters.TEXT & filters.Regex("^Шаблон$"), start)],
        states={
            RADIUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_radius)],
            ARC: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_arc)],
            EDGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_edge)]
        },
        fallbacks=[]
    )

    template_run_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex("^Разгон шаблона$"), start_template_run)],
        states={
            TOLERANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_tolerance)],
            PASSES: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_passes)]
        },
        fallbacks=[]
    )

    template_steps_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex("^Шаги шаблона$"), start_template_steps)],
        states={
            HOLES_ON_TAPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_holes_on_tape)],
            HOLES_IN_TEMPLATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_holes_in_template)]
        },
        fallbacks=[]
    )

    # Новый обработчик для кнопки "Разница дуги"
    difference_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex("^Разница дуги$"), start_difference)],
        states={
            DIFFERENCE_RADIUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_difference_radius)],
            DIFFERENCE_ARC: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_difference_arc)]
        },
        fallbacks=[]
    )

    application.add_handler(conv_handler)
    application.add_handler(template_run_handler)
    application.add_handler(template_steps_handler)
    application.add_handler(difference_handler)  # Добавляем новый обработчик

    print("Бот запущен. Ожидание сообщений...")
    application.run_polling()

if __name__ == "__main__":
    main()