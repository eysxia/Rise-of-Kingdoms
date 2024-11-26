import random
from utils.utils import find_button, click_button


async def use_resource_items(app):
    async def use_resource_item(app, resource):
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

    button = await find_button(app, f"./icons/items.png", max_attempts=1)
    if button:
        await click_button(app, button)
        resources = ["food", "wood", "stone", "gold", "gems", "chest"]
        random.shuffle(resources)

        for resource in resources:
            buttons = await find_button(app, f"./icons/items_{resource}.png", confidence=0.9, return_all=True)
            if buttons:
                button = await find_button(app, f"./icons/items_{resource}.png", confidence=0.9)
                await click_button(app, button)
                if resource == "chest":
                    await use_resource_item(app, "chest")
                else:
                    await use_resource_item(app, None)

                while True:
                    button = await find_button(app, f"./icons/items_{resource}.png", confidence=0.9)
                    if button and button != buttons[0]:
                        await click_button(app, button)
                        if resource == "chest":
                            await use_resource_item(app, "chest")
                        else:
                            await use_resource_item(app, None)

                        if resource == "chest":
                            button = await find_button(app, f"./icons/items_other.png", max_attempts=2)
                            await click_button(app, button)

                            while True:
                                button = await find_button(app, f"./icons/items_{resource}.png", confidence=0.9) 
                                if button:
                                    await click_button(app, button)
                                    await use_resource_item(app, "chest")
                                else:
                                    break
                    else:
                        break

        button = await find_button(app, f"./icons/basic_menu_exit.png")
        await click_button(app, button)