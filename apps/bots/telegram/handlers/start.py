from telegrinder import Dispatch, Message
from telegrinder.rules import Text
from telegrinder.tools.formatting import HTMLFormatter

dp = Dispatch()


@dp.message(Text("/start"))
async def start(message: Message):
    await message.reply(
        HTMLFormatter("Hello, {:italic}!!!").format(message.from_user.first_name),
        parse_mode=HTMLFormatter.PARSE_MODE,
    )
