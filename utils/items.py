import random
from utils.utils import find_button, click_button


async def use_items(app):
    button = await find_button(app, f"./icons/items.png", max_attempts=1)
    if button:
        await click_button(app, button)

        async def use_resource_items():
            resources = ["chest", "food", "wood", "stone"]
            random.shuffle(resources)

            for resource in resources:
                while True:
                    button = await find_button(app, f"./icons/items_{resource}.png", confidence=0.9)
                    if button:
                        await click_button(app, button)

                        button = await find_button(app, f"./icons/items_max.png", max_attempts=2)
                        await click_button(app, button)
                        button = await find_button(app, f"./icons/items_use.png", max_attempts=2)
                        await click_button(app, button)
                        if resource == "chest":
                            button = await find_button(app, f"./icons/confirm.png", max_attempts=2)
                            await click_button(app, button)
                        else:
                            button = await find_button(app, f"./icons/items_yes.png", max_attempts=2)
                            if button:
                                await click_button(app, button)
                    else:
                        break

            button = await find_button(app, f"./icons/basic_menu_exit.png")
            await click_button(app, button)