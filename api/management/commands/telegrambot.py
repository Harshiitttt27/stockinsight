import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from api.models import Prediction, TelegramUser
from api.ml import predict_stock_and_generate_plots
from django.conf import settings
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)

# Rate limit: max 10 predictions per user per minute
USER_RATE_LIMIT = {}

def rate_limited(user_id):
    now = datetime.now()
    timestamps = USER_RATE_LIMIT.get(user_id, [])
    timestamps = [ts for ts in timestamps if now - ts < timedelta(minutes=1)]
    if len(timestamps) >= 10:
        return True
    timestamps.append(now)
    USER_RATE_LIMIT[user_id] = timestamps
    return False
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.effective_chat.id
        username = update.effective_user.username

        if not username:
            await update.message.reply_text("❌ You don't have a Telegram username. Please set one in Telegram settings.")
            return

        user = await sync_to_async(User.objects.filter(username=username).first)()
        if not user:
            await update.message.reply_text("❌ You must register and login on the platform first.")
            return

        telegram_user = await sync_to_async(TelegramUser.objects.filter(user=user).first)()
        if telegram_user:
            telegram_user.chat_id = chat_id
        else:
            telegram_user = TelegramUser(user=user, chat_id=chat_id)

        await sync_to_async(telegram_user.save)()

        await update.message.reply_text("✅ Telegram account linked successfully!")

    except Exception as e:
        import logging
        logging.exception("Error in /start handler")
        await update.message.reply_text(f"⚠️ Error: {str(e)}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start – Link Telegram to your account\n"
        "/predict <TICKER> – Predict next-day price\n"
        "/latest – View your latest prediction\n"
        "/help – Show this help message"
    )

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    telegram_user = await sync_to_async(TelegramUser.objects.filter(chat_id=chat_id).first)()
    if not telegram_user:
        await update.message.reply_text("❌ Use /start first to link your account.")
        return

    if rate_limited(chat_id):
        await update.message.reply_text("⏳ Rate limit exceeded (10 predictions/min). Please wait.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Usage: /predict <TICKER>")
        return

    ticker = context.args[0].upper()

    try:
        
        price, mse, rmse, r2, plot1, plot2 = await sync_to_async(predict_stock_and_generate_plots)(ticker)

        rel_plot1 = os.path.relpath(plot1, settings.MEDIA_ROOT)
        rel_plot2 = os.path.relpath(plot2, settings.MEDIA_ROOT)

       
        user = await sync_to_async(lambda: telegram_user.user)()

       
        prediction = await sync_to_async(Prediction.objects.create)(
            user=user,
            ticker=ticker,
            next_day_price=price,
            mse=mse,
            rmse=rmse,
            r2=r2,
            plot_1=rel_plot1,
            plot_2=rel_plot2
        )

        await update.message.reply_text(
            f"📊 Prediction for {ticker}\n"
            f"Next-Day Price: {price:.2f}\nMSE: {mse:.4f}\nRMSE: {rmse:.4f}\nR²: {r2:.4f}"
        )

        await update.message.reply_photo(photo=open(plot1, 'rb'))
        await update.message.reply_photo(photo=open(plot2, 'rb'))

    except Exception as e:
        import logging
        logging.exception("Error in /predict")
        await update.message.reply_text(f"⚠️ Error: {str(e)}")


async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    telegram_user = await sync_to_async(TelegramUser.objects.filter(chat_id=chat_id).first)()
    if not telegram_user:
        await update.message.reply_text("❌ Use /start first.")
        return

    latest_prediction = await sync_to_async(
        lambda: Prediction.objects.filter(user=telegram_user.user).order_by('-created_at').first()
    )()

    if not latest_prediction:
        await update.message.reply_text("📭 No predictions found.")
        return

    await update.message.reply_text(
        f"📈 Latest Prediction for {latest_prediction.ticker}\n"
        f"Price: {latest_prediction.next_day_price:.2f}\n"
        f"Date: {latest_prediction.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    await update.message.reply_photo(photo=open(os.path.join(settings.MEDIA_ROOT, latest_prediction.plot_1.name), 'rb'))
    await update.message.reply_photo(photo=open(os.path.join(settings.MEDIA_ROOT, latest_prediction.plot_2.name), 'rb'))


class Command(BaseCommand):
    help = 'Run the Telegram bot using long polling.'

    def handle(self, *args, **kwargs):
        token = os.environ.get('BOT_TOKEN')
        if not token:
            raise Exception("BOT_TOKEN is not set in the environment variables.")

        application = ApplicationBuilder().token(token).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("predict", predict))
        application.add_handler(CommandHandler("latest", latest))

        self.stdout.write("Telegram bot started...")
        application.run_polling()
