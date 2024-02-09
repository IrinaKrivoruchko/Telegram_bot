import pyjokes
import random
from aiogram import types, F, Router

router = Router()

# @router.message(F.text == 'anekdot')
# async def anekdot(message: types.Message):
#     joke = pyjokes.get_joke()
#     await message.answer(joke)
#
# @router.message(F.text == 'Second button')
# async def number(message: types.Message):
#     ran = random.randint(1, 100000)
#     await message.answer(str(ran))

