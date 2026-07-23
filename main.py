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


# ساخت دیتابیس
database.create_table()


# -----------------------------
# نرمال سازی متن
# -----------------------------

def normalize_text(text):

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()



# -----------------------------
# ساخت شناسه پیام
# -----------------------------

def make_hash(text):

    return hashlib.md5(
        text.encode("utf-8")
    ).hexdigest()



# -----------------------------
# تشخیص لینک
# -----------------------------

def has_link(message):

    text = ""

    if message.text:
        text = message.text

    elif message.caption:
        text = message.caption


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


    print(
        "LINK CHECK:",
        text,
        result
    )


    if result:
        return True



    # بررسی تشخیص خود تلگرام

    if message.entities:

        for entity in message.entities:

            print(
                "ENTITY:",
                entity.type
            )

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
# بررسی پیام
# -----------------------------

async def check_message(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE):


    print("UPDATE RECEIVED")


    message = update.message


    if not message:

        print("NO MESSAGE")

        return



    print(
        "TEXT:",
        message.text
    )



    # -------------------------
    # اول لینک
    # -------------------------

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



    # -------------------------
    # گرفتن متن
    # -------------------------

    text = ""


    if message.text:

        text = message.text


    elif message.caption:

        text = message.caption


    else:

        return



    text = normalize_text(text)



    # -------------------------
    # پیام کوتاه آزاد است
    # -------------------------

    words = len(
        text.split()
    )


    if words < 10:

        print(
            "SHORT MESSAGE:",
            text
        )

        return



    # -------------------------
    # بررسی تکراری
    # -------------------------

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



    # -------------------------
    # ذخیره پیام اول
    # -------------------------

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