import asyncio
import mss
import cv2
import numpy as np
import random
from pathlib import Path
from pynput.mouse import Controller, Button


mouse = Controller()


async def take_screenshot(app):
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        if app.config["keep_window_pinned"]:
            app.root.withdraw()
            app.console.withdraw()
        screenshot = np.array(sct.grab(monitor))
        if app.config["keep_window_pinned"]:
            await asyncio.sleep(1)
            app.root.deiconify()
            app.console.deiconify()
        return screenshot[..., :3]


async def find_button(app, button, confidence=0.7, max_attempts=3):
    app.console_activity_label.config(text=f"Finding Button: {Path(button).stem.replace("_", " ").capitalize()}")
    button = cv2.imread(button)
    attempt = 0

    while attempt < max_attempts:
        await asyncio.sleep(1)
        screen = await take_screenshot(app)
        app.console_attempt_label.config(text=f"Attempt: {attempt + 1}/{max_attempts}")
        result = cv2.matchTemplate(screen, button, cv2.TM_CCOEFF_NORMED)
        _, value, _, location = cv2.minMaxLoc(result)

        app.console_confidence_label.config(text=f"Current Confidence: {value:.4f}")

        if value >= confidence:
            center = (
                location[0] + button.shape[1] // 2,
                location[1] + button.shape[0] // 2,
            )
            return center

        attempt += 1
        await asyncio.sleep(3)

    return None


async def click_button(app, position, double_click=False):
    if position:
        x, y = position
        x += random.randint(-1, 1)
        y += random.randint(-1, 1)

        cx, cy = mouse.position
        dx = x - cx
        dy = y - cy
        distance = (dx ** 2 + dy ** 2) ** 0.5
        steps = max(20, int(distance / 3) + random.randint(-5, 5)) 

        curve_factor = random.uniform(0.2, 0.5) * distance
        curve_direction = random.choice([-1, 1])

        for step in range(steps):
            progress = step / steps

            ease = (progress ** 2) * (3 - 2 * progress)
            curve_offset = curve_factor * curve_direction * (1 - (2 * abs(0.5 - progress)))
            deviation = random.uniform(-2, 2) * (1 - ease)

            ix = int(cx + dx * ease + curve_offset * (1 - ease) + deviation)
            iy = int(cy + dy * ease + deviation)
            mouse.position = (ix, iy)
            await asyncio.sleep(0.01)


        if app.config["keep_window_pinned"]:
            app.root.withdraw()
            app.console.withdraw()
        await asyncio.sleep(random.uniform(0.1, 0.2))
        mouse.click(Button.left, 1)
        if double_click:
            await asyncio.sleep(1)
            mouse.click(Button.left, 1)
        if app.config["keep_window_pinned"]:
            await asyncio.sleep(1)
            app.root.deiconify()
            app.console.deiconify()

        app.console_confidence_label.config(text=f"Current Confidence: None")
        app.console_attempt_label.config(text=f"Attempt: 0/0")
        app.console_activity_label.config(text=f"Finding Button: NaN")