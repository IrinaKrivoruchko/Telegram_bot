import asyncio
import logging
import sys
from aiogram import Bot, Router, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, Message
from config import TOKEN
from api_weather import find_places_by_location, get_weather_by_city

dp = Dispatcher()
weather_router = Router()


# States
class WeatherFind(StatesGroup):
    find_places_by_location_state = State()
    user_choice_state = State()
    process_city_state = State()


@dp.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(WeatherFind.find_places_by_location_state)
    await message.answer(
        f'Hello, {message.from_user.first_name}! Please enter the name of the city for watching the weather:',
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message(Command("cancel"))
@dp.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        "Cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    )


@weather_router.message(WeatherFind.find_places_by_location_state)
async def find_places(message: Message, state: FSMContext) -> None:
    try:
        city_name = message.text
        places = find_places_by_location(city_name)

        await state.update_data(data=places)

        if places['error']:
            await message.answer(f'Not found information about the city {city_name}. Try again')
            return

        if len(places['data']) == 1:
            await message.answer(f'You requested weather information for {city_name}')
            place_id = places['data'][0]['place_id']
            await without_choice(message, state, place_id)
            return

        if len(places['data']) > 1:
            result = ''
            for place in places['data']:
                result += f"Number: {place['id']}; City: {place['name']}; Country: {place['country']}\n"

            await message.answer(result)
            await message.reply("Please choose number of city: ")
            await state.set_state(WeatherFind.user_choice_state)

    except Exception as ex:
        await message.answer(f"Something went wrong. Repeat your request")


# # Handle user's response to the city

@weather_router.message(WeatherFind.user_choice_state)
async def user_choice(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        places = data['data']
        number_choice = message.text

        place_id = None
        for place in places:
            if place['id'] == int(number_choice):
                place_id = place['place_id']
                break

        # if place_id is None:
        #     await message.answer(f"Something went wrong. Repeat your request")
        #     return

        await message.reply(f"You requested weather information for {number_choice}")

        weather_info = get_weather_by_city(place_id)
        await message.answer(f"T: {weather_info['temperature']}")

        await ending(message, state)

    except Exception as ex:
        await message.answer(f"Something went wrong. Repeat your request")


async def without_choice(message: Message, state: FSMContext, city_name):
    try:
        weather_info = get_weather_by_city(city_name)
        await message.answer(f"T: {weather_info['temperature']}")

        await ending(message, state)

    except Exception as ex:
        await message.answer(f"Something went wrong. Repeat your request")


async def ending(message: Message, state: FSMContext) -> None:
    try:
        # Clear the state to return to the initial state
        await state.clear()
        await state.set_state(WeatherFind.find_places_by_location_state)
        await message.answer(
            f'Please enter the name of the city for watching the weather:',
            reply_markup=ReplyKeyboardRemove()
        )
    except Exception as ex:
        await message.answer(f"Something went wrong. Repeat your request")


async def main():
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await bot.delete_webhook(drop_pending_updates=True)
    dp.include_router(weather_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
