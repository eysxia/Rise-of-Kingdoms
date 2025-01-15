import asyncio
from utils.utils import find_button, click_button


async def explore_fog(app):
    button = await find_button(app, "./icons/scout.png",  max_attempts=1)
    if button:
        await click_button(button)
        for _ in range(3):
            button = await find_button(app, "./icons/explore.png")
            if button:
                await click_button(app, button)
                await asyncio.sleep(1)

                button = await find_button(app, "./icons/explore.png")
                await click_button(app, button)

                button = await find_button(app, "./icons/send.png")
                await click_button(app, button)

                button = await find_button(app, "./icons/home.png")
                await click_button(app, button)
            else:
                break


async def use_kingdom_maps(app):
    button = await find_button(app, "./icons/items.png")
    if button: 
        await click_button(button)

        button = await find_button(app, "./icons/items_other.png")
        await click_button(app, button)

        button = await find_button(app, "./icons/kingdom_maps.png")
        if button:
            await click_button(app, button)

            button = await find_button(app, f"./icons/items_max.png", max_attempts=2)
            await click_button(app, button)

            button = await find_button(app, f"./icons/items_use.png", max_attempts=2)
            await click_button(app, button)
        
            button = await find_button(app, "./icons/home.png")
            await click_button(app, button)
        
            button = await find_button(app, "./icons/home.png")
            await click_button(app, button)
        else:
            button = await find_button(app, f"./icons/basic_menu_exit.png")
            await click_button(app, button)