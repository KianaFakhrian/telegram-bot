import hashlib
import re

from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters
)

from database import (
    init_db,
    is_duplicate,
    save_message_hash
)

import config



# -------------------------
# Normalize text
# -------------------------

def normalize_text(text):

    if not text:
        return ""

    text = text.strip()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.lower()



# -------------------------
# Check links
# -------------------------

def has_link(text):

    if not text:
        return False


    pattern = r"""
    (
    https?://
    |
    www\.
    |
    \.com
    |
    \.ir
    |
    \.org
    )
    """


    return re.search(
        pattern,
        text,
        re.IGNORECASE | re.VERBOSE
    ) is not None




# -------------------------
# Hash maker
# -------------------------

def create_hash(value):

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()




# -------------------------
# Create fingerprint
# -------------------------

def generate_content_hash(message):


    # PHOTO

    if message.photo:


        photo_id = message.photo[-1].file_unique_id


        caption = normalize_text(
            message.caption
        )


        if caption:

            data = (
                f"photo_{photo_id}"
                f"_caption_{caption}"
            )


        else:

            data = (
                f"photo_{photo_id}"
            )


        return create_hash(data)




    # VIDEO

    if message.video:


        video_id = message.video.file_unique_id


        caption = normalize_text(
            message.caption
        )


        if caption:

            data = (
                f"video_{video_id}"
                f"_caption_{caption}"
            )


        else:

            data = (
                f"video_{video_id}"
            )


        return create_hash(data)




    # TEXT

    if message.text:


        text = normalize_text(
            message.text
        )


        words = len(
            text.split()
        )


        # پیام کوتاه نادیده گرفته شود

        if words < 10:

            return None



        data = (
            f"text_{text}"
        )


        return create_hash(data)




    return None





# -------------------------
# Main handler
# -------------------------

async def message_handler(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):


    message = update.message


    if not message:

        return



    # بررسی لینک

    content = (
        message.text
        or
        message.caption
    )


    if has_link(content):

        await message.delete()

        return



    # ساخت fingerprint

    content_hash = generate_content_hash(
        message
    )



    # پیام کوتاه

    if content_hash is None:

        return




    # بررسی تکراری


    if is_duplicate(content_hash):


        try:

            await message.delete()


        except Exception as e:

            print(
                "Delete error:",
                e
            )


        return




    # ذخیره اولین پیام


    save_message_hash(
        message.chat.id,
        content_hash
    )






# -------------------------
# Start Bot
# -------------------------

def main():


    init_db()



    app = (
        Application
        .builder()
        .token(config.TOKEN)
        .build()
    )



    app.add_handler(

        MessageHandler(
            filters.ALL,
            message_handler
        )

    )



    print(
        "Bot Started..."
    )



    app.run_polling()




if __name__ == "__main__":

    main()