import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from db import Database
from parsers import fetch_all_sites
from config import BOT_TOKEN, CHECK_INTERVAL_MIN, DEFAULT_MAX_PRICE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
db = Database()

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    db.save_user(user_id)
    await update.message.reply_text("Ты подписан! Объявления будут приходить лично тебе.")

async def background_checker(app):
    logger.info("Background checker started")
    while True:
        ads = fetch_all_sites(max_price=DEFAULT_MAX_PRICE)
        logger.info(f"Fetched {len(ads)} ads from parsers")
        stats = db.get_stats() or {"min_price": 0, "max_price": 0, "avg_price": 0}
        for ad in ads:
            if not db.exists(ad['id']):
                db.insert_ad(ad)
                rec = "✅ Стоит рассмотреть" if ad['price'] < stats['avg_price'] else "⛔ Слишком дорого"
                caption = (f"{ad['title']}, {ad.get('year', '')}\n"
                           f"{ad.get('location', '')}\n"
                           f"Пробег: {ad.get('km', '')}\n"
                           f"Цена: €{ad['price']}\n\n"
                           f"Рыночная цена: €{stats['min_price']}–{stats['max_price']}\n"
                           f"Рекомендация: {rec}\n\n"
                           f"Ссылка: {ad['url']}")
                for user_id in db.get_all_users():
                    try:
                        await app.bot.send_photo(chat_id=user_id, photo=ad.get('image_url'), caption=caption)
                    except Exception as e:
                        logger.warning(f"Failed to send ad to user {user_id}: {e}")
        logger.info(f"Sleeping for {CHECK_INTERVAL_MIN} minutes")
        await asyncio.sleep(CHECK_INTERVAL_MIN * 60)

async def on_startup(app):
    logger.info("Starting background task")
    asyncio.create_task(background_checker(app))

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.post_init = on_startup
    app.run_polling()

if __name__ == "__main__":
    main()

