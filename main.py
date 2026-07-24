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





# -----------------------------
# Normalize Text
# -----------------------------

def normalize_text(text):

    if not text:

        return ""


    text=text.strip()


    text=re.sub(
        r"\s+",
        " ",
        text
    )


    return text.lower()





# -----------------------------
# Detect Link
# -----------------------------

def has_link(text):

    if not text:

        return False



    pattern=r"""
    (
        https?://
        |
        www\.
        |
        t\.me/
        |
        telegram\.me/
        |
        [a-zA-Z0-9-]+\.(com|ir|org|net|io|co)
    )
    """



    return re.search(
        pattern,
        text,
        re.IGNORECASE | re.VERBOSE
    ) is not None



# -----------------------------
# Detect Telegram IDs
# -----------------------------

def has_telegram_id(text):

    if not text:
        return False


    pattern = r"""
    (
        @[a-zA-Z0-9_]{3,}
        |
        t\.me/[a-zA-Z0-9_]+
        |
        telegram\.me/[a-zA-Z0-9_]+
    )
    """


    return re.search(
        pattern,
        text,
        re.IGNORECASE | re.VERBOSE
    ) is not None

# -----------------------------
# Hash Generator
# -----------------------------

def create_hash(data):

    return hashlib.sha256(
        data.encode("utf-8")
    ).hexdigest()





# -----------------------------
# Generate Fingerprint
# -----------------------------

def generate_content_hash(message):


    # -----------------
    # PHOTO
    # -----------------

    if message.photo:


        photo_id = message.photo[-1].file_unique_id


        caption = normalize_text(
            message.caption
        )


        if caption:

            data = (
                f"photo:"
                f"{photo_id}:"
                f"{caption}"
            )


        else:

            data = (
                f"photo:"
                f"{photo_id}"
            )



        return create_hash(data)





    # -----------------
    # VIDEO
    # -----------------

    if message.video:


        video_id = message.video.file_unique_id



        caption = normalize_text(
            message.caption
        )



        if caption:

            data = (
                f"video:"
                f"{video_id}:"
                f"{caption}"
            )


        else:

            data = (
                f"video:"
                f"{video_id}"
            )



        return create_hash(data)






    # -----------------
    # TEXT
    # -----------------

    if message.text:


        text = normalize_text(
            message.text
        )



        word_count=len(
            text.split()
        )



        # پیام های کوتاه حذف نشوند

        if word_count < 10:

            return None



        data = (
            f"text:"
            f"{text}"
        )



        return create_hash(data)



    return None





# -----------------------------
# Main Message Handler
# -----------------------------

async def message_handler(
        update:Update,
        context:ContextTypes.DEFAULT_TYPE
):


    message=update.message



    if not message:

        return





    # -----------------
    # Link Detection
    # -----------------


    content_parts=[]



    if message.text:

        content_parts.append(
            message.text
        )



    if message.caption:

        content_parts.append(
            message.caption
        )



    full_content=" ".join(
        content_parts
    )



    if (has_link(full_content) or has_telegram_id(full_content)):

        try:

            await message.delete()


        except Exception as e:

            print(e)


        return






    # -----------------
    # Create Hash
    # -----------------

    content_hash = generate_content_hash(
        message
    )



    if content_hash is None:

        return





    # -----------------
    # Duplicate Check
    # -----------------

    if is_duplicate(content_hash):


        try:

            await message.delete()


        except Exception as e:

            print(
                "Delete Error:",
                e
            )


        return






    # -----------------
    # Save First Message
    # -----------------

    save_message_hash(
        message.chat.id,
        content_hash
    )






# -----------------------------
# Start Bot
# -----------------------------

def main():



    init_db()



    application=(

        Application
        .builder()
        .token(config.TOKEN)
        .build()

    )




    application.add_handler(

        MessageHandler(
            filters.ALL,
            message_handler
        )

    )




    print(
        "Bot Started..."
    )



    application.run_polling()





if __name__=="__main__":

    main()