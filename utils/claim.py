import asyncio
from utils.utils import find_button, click_button


async def claim_quest_rewards(app):
    button = await find_button(app, f"./icons/quests.png", confidence=0.9)
    if button:
        await click_button(app, button)

        while True:
            await asyncio.sleep(1)
            button = await find_button(app, f"./icons/claim.png")
            if button:
                await click_button(app, button)
            else:
                break

        
        button = await find_button(app, f"./icons/quests_page_2.png", max_attempts=2)
        await click_button(app, button)

        while True:
            await asyncio.sleep(1)
            button = await find_button(app, f"./icons/claim.png")
            if button:
                await click_button(app, button)
            else:
                break

        button = await find_button(app, f"./icons/basic_menu_exit.png")
        await click_button(app, button)


async def claim_kingdom_event_rewards(app):
    
    button = await find_button(app, f"./icons/kingdom_events.png", confidence=0.9)
    if button:
        await click_button(app, button)
    
    while True:
        await asyncio.sleep(1)
        button = await find_button(app, f"./icons/claim.png")
        if button:
            await click_button(app, button)
        else:
            break
    
    async def claim_rewards():
        while True:
            button = await find_button(app, f"./icons/kingdom_events_new_secondary.png", confidence=0.9)
            if button: 
                await click_button(app, button)

                while True:
                    await asyncio.sleep(1)
                    button = await find_button(app, f"./icons/claim.png")
                    if button:
                        await click_button(app, button)
                    else:
                        break
            else:
                break
        return

    while True:
        await claim_rewards()
        button = await find_button(app, f"./icons/kingdom_events_new_main.png")
        if button:
            await click_button(app, button)
            await claim_rewards()
        else:
            break


async def claim_and_read_mail(app):
    button = await find_button(app, f"./icons/mail.png", confidence=0.9)
    if button:
        await click_button(app, button)
    
    await asyncio.sleep(1)
    button = await find_button(app, f"./icons/mail_claim_all.png")
    await click_button(app, button)

    while True:
        await asyncio.sleep(1)
        button = await find_button(app, f"./icons/mail_new.png", confidence=0.9)
        if button:
            await click_button(app, button)
            button = await find_button(app, f"./icons/mail_claim_all.png")
            await click_button(app, button)
        else:
            break

    button = await find_button(app, f"./icons/basic_menu_exit.png")
    await click_button(app, button)