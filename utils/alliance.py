import asyncio
from utils.utils import find_button, click_button


async def help_alliance(app):
    button = await find_button(app, f"./icons/alliance_help_requested.png")
    if button:
        await click_button(app, button)


async def check_alliance_notifications(app):
    button = await find_button(app, f"./icons/alliance.png", confidence=0.9)
    if button:
        await click_button(app, button)

        async def check_tech():
            button = await find_button(app, f"./icons/alliance_donate_tech.png", confidence=1)
            if button:
                await click_button(app, button)

                button = await find_button(app, f"./icons/alliance_recommended_upgrade.png", confidence=0.9)
                if button:
                    await click_button(app, button)

                    while True:
                        await asyncio.sleep(2)
                        button = await find_button(app, f"./icons/donate.png", confidence=0.9)
                        if button:
                            await click_button(app, button)
                        else:
                            break
                
                    for _ in range(2):
                        button = await find_button(app, f"./icons/basic_menu_exit.png")
                        await click_button(app, button)
                else:
                    button = await find_button(app, f"./icons/basic_menu_exit.png")
                    await click_button(app, button)
            else:
                return

        async def check_gifts():
            await asyncio.sleep(5)
            
            button = await find_button(app, f"./icons/alliance_gifts.png", confidence=1)
            if button:
                await click_button(app, button)

                while True:
                    button = await find_button(app, f"./icons/claim.png")
                    if button:
                        await click_button(app, button)
                    else:
                        break
                
                button = await find_button(app, f"./icons/alliance_new.png")
                if button:
                    await click_button(app, button)
                    
                    button = await find_button(app, f"./icons/claim_all.png")
                    await click_button(app, button)
                    
                    button = await find_button(app, f"./icons/confirm.png")
                    await click_button(app, button)

                    button = await find_button(app, f"./icons/basic_menu_exit.png")
                    await click_button(app, button)

            else:
                return

        if app.active_functions["help_alliance_research"]:
            await check_tech()
        if app.active_functions["claim_alliance_rewards"]:
            await check_gifts()

        button = await find_button(app, f"./icons/basic_menu_exit.png")
        await click_button(app, button)   

                



                
            