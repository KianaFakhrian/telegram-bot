import hashlib

from telegram import Update

from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters
)


from config import TOKEN

import database



database.create_table()



def make_hash(text):

    return hashlib.md5(
        text.encode("utf-8")
    ).hexdigest()



def has_link(message):


    if message.entities:

        for e in message.entities:

            if e.type in [
                "url",
                "text_link"
            ]:

                return True


    if message.caption_entities:

        for e in message.caption_entities:

            if e.type in [
                "url",
                "text_link"
            ]:

                return True


    return False





async def check_message(
        update:Update,
        context:ContextTypes.DEFAULT_TYPE):


    message=update.message


    text = message.text.strip()


    # پیام های کوتاه را نادیده بگیر
    word_count = len(text.split())

    if word_count < 10:
        return



    # حذف لینک

    if has_link(message):

        await message.delete()

        print("Link deleted")

        return



    text=""



    if message.text:

        text=message.text



    elif message.caption:

        text=message.caption



    else:

        return



    hash_value=make_hash(text)



    # پیام تکراری

    if database.exists(hash_value):


        await message.delete()


        print(
        "Duplicate deleted:",
        text
        )


        return



    username="unknown"


    if message.from_user:

        username=message.from_user.username



    database.save(
        hash_value,
        username
    )


    print(
    "Saved:",
    text
    )





app=Application.builder()\
.token(TOKEN)\
.build()



handler=MessageHandler(
    filters.ALL,
    check_message
)



app.add_handler(handler)



print("Bot Started...")


app.run_polling()