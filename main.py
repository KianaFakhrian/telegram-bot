import hashlib
import re

from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters
)

from config import TOKEN
import database


# ساخت جدول دیتابیس
database.create_table()



# -----------------------------
# تبدیل متن به hash
# -----------------------------

def make_hash(text):

    return hashlib.md5(
        text.encode("utf-8")
    ).hexdigest()



# -----------------------------
# تمیز کردن متن
# -----------------------------

def normalize_text(text):

    text = text.lower()

    # حذف فاصله‌های اضافی
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()



# -----------------------------
# تشخیص لینک
# -----------------------------

def has_link(message):

    text = ""

    if message.text:
        text = message.text

    elif message.caption:
        text = message.caption


    # لینک‌هایی مثل:
    # https://google.com
    # www.google.com
    # quera.org

    pattern = r"""
    (?ix)
    (
        https?://\S+
        |
        www\.\S+
        |
        \b[a-z0-9-]+\.(com|org|net|ir|io|edu|ai)(/\S*)?
    )
    """


    result = re.search(
        pattern,
        text
    )


    # برای تست در لاگ Railway
    print(
        "LINK CHECK:",
        text,
        result
    )


    if result:
        return True



    # بررسی لینک‌هایی که خود تلگرام تشخیص داده

    if message.entities:

        for entity in message.entities:

            if entity.type in [
                "url",
                "text_link"
            ]:
                return True



    if message.caption_entities:

        for entity in message.caption_entities:

            if entity.type in [
                "url",
                "text_link"
            ]:
                return True


    return False



# -----------------------------
# بررسی پیام‌ها
# -----------------------------

async def check_message(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE):


    message = update.message


    if not message:
        return

    print("NEW MESSAGE:", update.message.text)


    # =========================
    # مرحله اول: حذف لینک
    # =========================

    if has_link(message):

        try:

            await message.delete()

            print(
                "LINK DELETED"
            )

        except Exception as e:

            print(
                "DELETE ERROR:",
                e
            )


        return




    # =========================
    # گرفتن متن
    # =========================

    text = ""


    if message.text:

        text = message.text


    elif message.caption:

        text = message.caption


    else:

        return



    text = normalize_text(text)



    # =========================
    # پیام کوتاه دست نخورَد
    # =========================

    word_count = len(
        text.split()
    )


    if word_count < 10:

        print(
            "SHORT MESSAGE IGNORED:",
            text
        )

        return




    # =========================
    # بررسی تکراری بودن
    # =========================


    hash_value = make_hash(text)



    if database.exists(hash_value):


        try:

            await message.delete()

            print(
                "DUPLICATE DELETED:",
                text
            )


        except Exception as e:

            print(
                "DELETE ERROR:",
                e
            )


        return




    # =========================
    # ذخیره پیام اول
    # =========================


    username = "unknown"


    if message.from_user:

        username = (
            message.from_user.username
            or "unknown"
        )



    database.save(
        hash_value,
        username
    )


    print(
        "MESSAGE SAVED:",
        text
    )





# -----------------------------
# اجرای ربات
# -----------------------------


app = Application.builder()\
    .token(TOKEN)\
    .build()



app.add_handler(
    MessageHandler(
        filters.ALL,
        check_message
    )
)



print(
    "Bot Started..."
)



app.run_polling()