import asyncio
import tkinter
import os
import ctypes
import time
import json
from tkinter import ttk, Canvas, Frame
from PIL import Image, ImageDraw, ImageTk
from utils.gather import gather_resources, gather_and_train_troops
from utils.alliance import help_alliance, check_alliance_notifications
from utils.build import upgrade_buildings
from utils.claim import claim_quest_rewards, claim_kingdom_event_rewards, claim_and_read_mail
from utils.items import use_resource_items
from utils.scout import explore_fog


def create_colored_square(color, size=20, border_color=(255, 255, 255, 255), border_width=2):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.rectangle(
        [0, 0, size - 1, size - 1],
        outline=border_color,
        width=border_width
    )

    inner_size = size - 2 * border_width
    if inner_size > 0:  
        draw.rectangle(
            [border_width, border_width, size - border_width - 1, size - border_width - 1],
            fill=color
        )

    return ImageTk.PhotoImage(img)


class ScrollableFrame(Frame):
    def __init__(self, parent, bg="#2E2E2E", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.canvas = Canvas(self, bg=bg, bd=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas, bg=bg)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<KeyPress-Up>", self._on_arrow_up)
        self.canvas.bind_all("<KeyPress-Down>", self._on_arrow_down)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def _on_arrow_up(self, event):
        self.canvas.yview_scroll(-1, "units")

    def _on_arrow_down(self, event):
        self.canvas.yview_scroll(1, "units")

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        

class App:
    def __init__(self, root, branch, console):
        self.start_time = time.time()
        self.root, self.branch, self.console = root, branch, console
        self.running = False
        self.active_functions = json.loads(open("./bot_config.json", "r").read())
        self.config = json.loads(open("./config.json", "r").read())
        self.loop = None
        self.red_square = create_colored_square((76, 175, 80, 255))
        self.green_square = create_colored_square((244, 67, 54, 255) )

        self.logo = ImageTk.PhotoImage(Image.open("./icons/logo.png").resize((75, 75), Image.Resampling.LANCZOS))
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", self.config["keep_window_pinned"])
        self.root.geometry("400x700")
        self.root.configure(bg="#2E2E2E")
        self.root.update_idletasks()
        rx, ry, rwidth = self.root.winfo_x(), self.root.winfo_y(), self.root.winfo_width()

        self.logo_holder = tkinter.Label(self.root, image=self.logo)
        self.logo_holder.pack(side="top", pady=(30, 10))
        self.root_title = tkinter.Label(self.root, text="Rise of Kingdoms Bot", font=("Helvetica", 18, "bold"), bg="#3A3A3A", fg="white")
        self.root_title.pack(side="top", pady=(10, 20))

        self.buttons = tkinter.Frame(self.root, bg="#3A3A3A", height=60)
        self.buttons.pack(pady=5, fill="x")
        self.start_button = tkinter.Button(self.buttons, text="Start", command=self.toggle_status, font=("Helvetica", 14, "bold"), width=12, relief="solid", bg="#4CAF50", fg="white", activebackground="#45a049")
        self.start_button.pack(side="left", padx=5, expand=True)
        self.close_button = tkinter.Button(self.buttons, text="Close", command=self.close_app, font=("Helvetica", 14, "bold"), width=12, relief="solid", bg="#F44336", fg="white", activebackground="#e41c1c")
        self.close_button.pack(side="left", padx=5, expand=True)

        self.info = tkinter.Frame(self.root, bg="#2E2E2E")
        self.info.pack(pady=10, fill="x")
        self.active_label = tkinter.Label(self.info, text="Active: None", font=("Helvetica", 12, "bold"), bg="#2E2E2E", fg="white", wraplength=350)
        self.active_label.pack(pady=5)
        self.status_bubble = tkinter.Label(self.info, text="●", font=("Helvetica", 18), fg="red", bg="#2E2E2E")
        self.status_bubble.pack(pady=5)
        self.root_separator_one = ttk.Separator(self.root, orient="horizontal")
        self.root_separator_one.pack(fill="x", pady=5)

        self.checkboxs = Frame(self.root, bg="#2E2E2E")
        self.checkboxs.pack(pady=10, fill="x")
        self.bot_options = tkinter.Label(self.checkboxs, text="Bot Configuration", font=("Helvetica", 18, "bold", "underline"), bg="#2E2E2E", fg="white")
        self.bot_options.pack(pady=(5, 15))

        self.scrollable_frame = ScrollableFrame(self.checkboxs, bg="#2E2E2E")
        self.scrollable_frame.pack(pady=5, fill="both", expand=True)

        for idx, func in enumerate(self.active_functions.keys()):
            var = tkinter.BooleanVar()
            var.set(self.active_functions[func])
            checkbox = tkinter.Checkbutton(
                self.scrollable_frame.scrollable_frame,
                text=func.replace("_", " ").title(),
                variable=var,
                font=("Helvetica", 12, "bold"),
                bg="#2E2E2E",
                fg="white",
                activebackground="#2E2E2E",
                selectcolor="#2E2E2E",
                image=self.green_square,
                selectimage=self.red_square,
                compound="left",
                indicatoron=False,
                highlightthickness=0,
                bd=0,
                relief="flat",
                padx=10,
                command=lambda func=func, var=var: self.toggle_function(func, var)
            )
            checkbox.grid(row=idx, column=0, padx=20, pady=5, sticky="w")

        self.root.bind("<Escape>", lambda event: self.close_app())

        self.branch.overrideredirect(True)
        self.branch.attributes("-topmost", self.config["keep_window_pinned"])
        self.branch.geometry("400x600")
        self.branch.configure(bg="#2E2E2E")
        self.branch.geometry(f"+{rx + rwidth + 10}+{ry}")
        self.branch.update_idletasks()
        bx, by, bwidth = self.branch.winfo_x(), self.branch.winfo_y(), self.branch.winfo_width()

        self.branch_title = tkinter.Label(self.branch, text="Game and App Configuration", font=("Helvetica", 18, "bold"), bg="#3A3A3A", fg="white")
        self.branch_title.pack(side="top", pady=(30, 10))
        self.branch_separator_one = ttk.Separator(self.branch, orient="horizontal")
        self.branch_separator_one.pack(fill="x", pady=(30, 20))

        self.branch_pinned_info = tkinter.Frame(self.branch, bg="#2E2E2E")
        self.branch_pinned_info.pack(pady=20, fill="x")
        self.branch_pinned_info_title = tkinter.Label(self.branch_pinned_info, text="Keep Tool Pinned", font=("Helvetica", 16, "bold"), bg="#3A3A3A", fg="white")
        self.branch_pinned_info_title.pack(pady=(10, 10))
        self.branch_pinned_buttons = tkinter.Frame(self.branch_pinned_info, bg="#3A3A3A", height=60)
        self.branch_pinned_buttons.pack(pady=5, fill="x")
        if self.config["keep_window_pinned"]:
            self.branch_pinned_button = tkinter.Button(self.branch_pinned_buttons, text="True", command=self.toggle_pinned, font=("Helvetica", 14, "bold"), width=12, relief="solid", bg="#4CAF50", fg="white", activebackground="#45a049")
        else:
            self.branch_pinned_button = tkinter.Button(self.branch_pinned_buttons, text="False", command=self.toggle_pinned, font=("Helvetica", 14, "bold"), width=12, relief="solid", bg="#F44336", fg="white", activebackground="#e41c1c")
        self.branch_pinned_button.pack(padx=5, expand=True)
        self.branch_separator_two = ttk.Separator(self.branch, orient="horizontal")
        self.branch_separator_two.pack(fill="x", pady=(30, 20))

        self.branch_close_info = tkinter.Frame(self.branch, bg="#2E2E2E")
        self.branch_close_info.pack(pady=20, fill="x")
        self.branch_close_info.grid_columnconfigure(0, weight=1)
        self.branch_close_info.grid_columnconfigure(1, weight=3)
        self.branch_close_info.grid_rowconfigure(0, weight=1)
        self.branch_close_info.grid_rowconfigure(1, weight=1)
        self.branch_close_info.grid_rowconfigure(2, weight=1)
        self.branch_close_info_title = tkinter.Label(self.branch_close_info, text="Close Bot After", font=("Helvetica", 16, "bold"), bg="#3A3A3A", fg="white")
        self.branch_close_info_title.grid(columnspan=2, pady=(10, 10))
        self.branch_close_info_hour_label = tkinter.Label(self.branch_close_info, text="Hours:", bg="#2E2E2E", fg="white", font=("Helvetica", 12, "bold"))
        self.branch_close_info_hour_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.branch_close_info_hour_input = tkinter.Entry(self.branch_close_info, width=5)
        self.branch_close_info_hour_input.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.branch_close_info_min_label = tkinter.Label(self.branch_close_info, text="Minutes:", bg="#2E2E2E", fg="white", font=("Helvetica", 12, "bold"))
        self.branch_close_info_min_label.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.branch_close_info_min_input = tkinter.Entry(self.branch_close_info, width=5)
        self.branch_close_info_min_input.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        self.branch_close_info_sec_label = tkinter.Label(self.branch_close_info, text="Seconds:", bg="#2E2E2E", fg="white", font=("Helvetica", 12, "bold"))
        self.branch_close_info_sec_label.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        self.branch_close_info_sec_input = tkinter.Entry(self.branch_close_info, width=5)
        self.branch_close_info_sec_input.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")
        self.branch_close_info_buttons = tkinter.Frame(self.branch, bg="#3A3A3A", height=60)
        self.branch_close_info_buttons.pack(pady=10, fill="x")
        self.branch_close_info_set_button = tkinter.Button(
            self.branch_close_info_buttons, 
            text="Set", 
            command=lambda: (
                self.close_after(self.branch_close_info_hour_input.get(), self.branch_close_info_min_input.get(), self.branch_close_info_sec_input.get())
                if self.branch_close_info_hour_input.get().isdigit() and self.branch_close_info_min_input.get().isdigit() and self.branch_close_info_sec_input.get().isdigit() 
                else None
            ),
            font=("Helvetica", 16, "bold"), width=12, relief="solid", bg="#4CAF50", fg="white", activebackground="#45a049")
        self.branch_close_info_set_button.pack(padx=5, expand=True)

        self.console.overrideredirect(True)
        self.console.attributes("-topmost", self.config["keep_window_pinned"])
        self.console.geometry("400x400")
        self.console.configure(bg="#2E2E2E")
        self.console.geometry(f"+{bx + bwidth + 10}+{by}")

        self.console_title = tkinter.Label(self.console, text="Logs & Data", font=("Helvetica", 18, "bold"), bg="#3A3A3A", fg="white")
        self.console_title.pack(side="top", pady=(30, 10))
        self.console_separator_one = ttk.Separator(self.console, orient="horizontal")
        self.console_separator_one.pack(fill="x", pady=(30, 20))

        self.console_info = tkinter.Frame(self.console, bg="#2E2E2E")
        self.console_info.pack(pady=20, fill="x")
        self.console_activity_label = tkinter.Label(self.console_info, text="Finding button: None", font=("Helvetica", 14, "bold"), bg="#2E2E2E", fg="white", wraplength=300)
        self.console_activity_label.pack(pady=5)
        self.console_attempt_label = tkinter.Label(self.console_info, text="Attempt: 0/0", font=("Helvetica", 14, "bold"), bg="#2E2E2E", fg="white", wraplength=300)
        self.console_attempt_label.pack(pady=5)
        self.console_confidence_label = tkinter.Label(self.console_info, text="Current Confidence: NaN", font=("Helvetica", 14, "bold"), bg="#2E2E2E", fg="white",)
        self.console_confidence_label.pack(pady=5)
        self.console_separator_two = ttk.Separator(self.console_info, orient="horizontal")
        self.console_separator_two.pack(fill="x", pady=(30, 30))
        self.console_elasped_time_label = tkinter.Label(self.console_info, text="Elapsed Time: NaN", font=("Helvetica", 14, "bold"), bg="#2E2E2E", fg="white", wraplength=300)
        self.console_elasped_time_label.pack(pady=5)

        self.console.bind("<Escape>", lambda event: self.close_app())

    def close_app(self):
        self.root.destroy()
        os._exit(0)

    def close_after(self, hours, mins, secs):
        self.branch_close_info_hour_input.config(state="disabled")
        self.branch_close_info_min_input.config(state="disabled")
        self.branch_close_info_sec_input.config(state="disabled")
        self.branch_close_info_set_button.config(state="disabled")
        hours = int(hours) * 3600
        mins = int(mins) * 60
        total_seconds = hours + mins + int(secs)
        self.countdown(total_seconds)
        
    def countdown(self, total_seconds):
        if total_seconds > 0:
            total_seconds -= 1
            self.branch.after(1000, lambda: self.countdown(total_seconds))
        else:
            self.close_app()

    def toggle_pinned(self):
        self.config["keep_window_pinned"] = not self.config["keep_window_pinned"]
        open("./config.json", "w").write(json.dumps(self.config, indent=4))
        self.root.attributes("-topmost", self.config["keep_window_pinned"])
        self.branch.attributes("-topmost", self.config["keep_window_pinned"])
        self.console.attributes("-topmost", self.config["keep_window_pinned"])
        if self.config["keep_window_pinned"]:
            self.branch_pinned_button.config(text="True", bg="#4CAF50", activebackground="#45a049")
        else:
            self.branch_pinned_button.config(text="False", bg="#F44336", activebackground="#e41c1c")

    def toggle_function(self, func, var):
        self.active_functions[func] = var.get()
        open("./bot_config.json", "w").write(json.dumps(self.active_functions, indent=4))
        self.update_active_label()

    def update_active_label(self):
        active_list = [name.replace("_", " ").title() for name, active in self.active_functions.items() if active]
        self.active_label.config(text="Active: " + ", ".join(active_list) if active_list else "Active: None")

    def toggle_status(self):
        self.running = not self.running
        if self.running:
            self.start_button.config(text="Stop", bg="#F44336", activebackground="#e41c1c")
            self.status_bubble.config(fg="green")
            self.loop = asyncio.create_task(self.run_main_loop())
        else:
            self.start_button.config(text="Start", bg="#4CAF50", activebackground="#45a049")
            self.status_bubble.config(fg="red")
            self.console_activity_label.config(text=f"Finding Button: None")
            self.console_attempt_label.config(text=f"Attempt: 0/0")
            self.console_confidence_label.config(text=f"Current Confidence: NaN")
            if self.loop:
                self.loop.cancel()

    def update_elapsed_time(self):
        elapsed_time = time.time() - self.start_time
        days = elapsed_time // (24 * 3600)
        elapsed_time %= (24 * 3600)    
        hours = elapsed_time // 3600
        elapsed_time %= 3600
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        self.console_elasped_time_label.config(text=f"Elapsed Time: {int(days)} days, {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds")
        self.console.after(1000, self.update_elapsed_time)


    async def run_main_loop(self):
        while self.running:
            try:
                if self.active_functions["gather_resources"] and self.running: 
                    await gather_resources(self)
                if self.active_functions["gather_troops"] and self.running: 
                    await gather_and_train_troops(self)
                if self.active_functions["help_alliance"] and self.running: 
                    await help_alliance(self)
                if self.active_functions["help_alliance_research"] and self.running:   
                    await check_alliance_notifications(self)
                if self.active_functions["upgrade_buildings"] and self.running: 
                    await upgrade_buildings(self)
                if self.active_functions["claim_quest_rewards"] and self.running:
                    await claim_quest_rewards(self)
                if self.active_functions["claim_event_rewards"] and self.running:
                    await claim_kingdom_event_rewards(self)
                if not self.active_functions["help_alliance_research"] and self.active_functions["claim_alliance_rewards"] and self.running: 
                    await check_alliance_notifications(self)
                if self.active_functions["claim_mail"] and self.running:
                    await claim_and_read_mail(self)
                if self.active_functions["use_resource_items"] and self.running:
                    await use_resource_items(self)
                if self.active_functions["auto_scout"] and self.running:
                    await explore_fog(self)
                await asyncio.sleep(300)
            except: 
                pass

    def on_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    async def update_asyncio_loop(self):
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 6)
        self.update_active_label()
        self.update_elapsed_time()
        while True:
            self.root.update()
            await asyncio.sleep(0.01)


async def main():
    root = tkinter.Tk()
    branch = tkinter.Toplevel(root)
    console = tkinter.Toplevel(root)
    app = App(root, console, branch)
    await app.update_asyncio_loop()


if __name__ == "__main__":
    asyncio.run(main())