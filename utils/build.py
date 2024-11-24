from utils.utils import find_button, click_button


async def upgrade_buildings(app):
    for _ in range(2):
        button = await find_button(app, f"./icons/upgradable.png", max_attempts=1)
        if button:
            await click_button(app, button)

            button = await find_button(app, f"./icons/upgrade.png", max_attempts=2)
            await click_button(app, button)

            button = await find_button(app, f"./icons/upgrade_confirm.png", max_attempts=2)
            if button:
                await click_button(app, button)
            else:
                button = await find_button(app, f"./icons/basic_menu_exit.png", max_attempts=2)
                await click_button(app, button)

            button = await find_button(app, f"./icons/request_alliance_help.png", max_attempts=2)
            await click_button(app, button)
        else:
            break