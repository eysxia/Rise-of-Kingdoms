import random
import asyncio
from utils.utils import find_button, click_button


async def gather_resources(app):
    resources = ["farm", "lumber_mill", "quarry", "gold"]
    random.shuffle(resources)
    for resource in resources:
        button = await find_button(app, f"./icons/{resource}.png", max_attempts=1)
        if button:
            await click_button(app, button)


async def gather_and_train_troops(app):
    troops = ["barracks", "siege_workshop", "archery_range", "stable"]
    random.shuffle(troops)
    for troop in troops:
        for num in range(2):
            button = await find_button(app, f"./icons/{troop}_{num+1}.png", max_attempts=1)
            if button:
                if app.active_functions["train_troops"]:
                    await click_button(app, button, double_click=True)
                
                    await asyncio.sleep(1)
                    button = await find_button(app, f"./icons/{troop}_train.png", max_attempts=2)
                    await click_button(app, button)

                    await asyncio.sleep(1)
                    button = await find_button(app, f"./icons/train.png", max_attempts=2)
                    await click_button(app, button)
                    break
                else:
                    await click_button(app, button)
                    break
        