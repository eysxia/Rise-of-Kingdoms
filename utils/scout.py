import asyncio
from utils.utils import find_button, click_button


async def explore_fog(app):
    button = await find_button(app, "./icons/scout.png",  max_attempts=1)
    if button:
        await click_button(button)
        for _ in range(3):
            button = await find_button(app, "./icons/explore.png")
            if button:
                await click_button(button)
                await asyncio.sleep(1)

                button = await find_button(app, "./icons/explore.png")
                await click_button(button)

                button = await find_button(app, "./icons/send.png")
                await click_button(button)

                button = await find_button(app, "./icons/home.png")
                await click_button(button)
            else:
                break
