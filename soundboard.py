""""
Copyright (C) 2026 basilisezkid23   

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import tkinter as tk
import pygame

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()

class SirenController:
    def __init__(self, root):
        self.root = root
        self.root.title("Tactical Siren Amplifier")
        self.root.configure(bg="#0f172a")
        self.root.geometry("640x480")
        self.root.minsize(400, 300)

        self.man_channel = pygame.mixer.Channel(0)
        self.yelp_channel = pygame.mixer.Channel(1)

        self.sounds = {}
        # ShadowDev7 commit: Removed .mp3 files, you don't have them
        # Addition: Organized using assets/ folder
        self.load_sound("BRBR", ["assets/BRBR.wav"])
        self.load_sound("SIREN2", ["assets/SIREN2.wav"])
        self.load_sound("SIREN3", ["assets/SIREN3.wav"])

        self.yelp_active = False
        self.man_active = False
        self.active_momentary_sounds = {}

        self.fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)
        self.root.bind("<Configure>", self.on_window_resize)

        self.setup_ui()

    def load_sound(self, key, filenames):
        for filename in filenames:
            if os.path.exists(filename):
                try:
                    self.sounds[key] = pygame.mixer.Sound(filename)
                    print(f"Loaded {key} from {filename}")
                    return
                except Exception as error:
                    print(f"Failed to load {filename}: {error}")

        print(f"Could not find audio file for {key}")
        self.sounds[key] = None

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)
        return "break"

    def exit_fullscreen(self, event=None):
        self.fullscreen = False
        self.root.attributes("-fullscreen", False)
        return "break"

    def on_window_resize(self, event):
        if event.widget != self.root:
            return

        size = min(event.width, event.height)

        button_font = max(11, int(size / 26))
        title_font = max(12, int(size / 22))
        status_font = max(10, int(size / 30))

        if hasattr(self, "title_label"):
            self.title_label.config(
                font=("Consolas", title_font, "bold")
            )

        if hasattr(self, "status_label"):
            self.status_label.config(
                font=("Consolas", status_font, "bold")
            )

        for button in self.mode_buttons.values():
            button.config(font=("Helvetica", button_font, "bold"))

    def update_status(self, text, mode="standby"):
        if not hasattr(self, "status_label"):
            return

        colors = {
            "standby": "#10b981",
            "active": "#ef4444",
            "warning": "#f59e0b"
        }

        color = colors.get(mode, "#10b981")
        self.status_label.config(
            text=f"● STATUS: {text}",
            fg=color
        )

    def start_momentary(self, sound_key, button_key):
        sound = self.sounds.get(sound_key)

        if sound:
            channel = sound.play(loops=-1)
            self.active_momentary_sounds[button_key] = (sound, channel)

            self.mode_buttons[button_key].config(
                bg="#ef4444",
                fg="#ffffff",
                relief="sunken"
            )

            self.update_status(
                f"OVERRIDE: {button_key}",
                mode="warning"
            )

    def stop_momentary(self, sound_key, button_key):
        if button_key in self.active_momentary_sounds:
            sound, channel = self.active_momentary_sounds[button_key]

            if channel:
                channel.stop()

            del self.active_momentary_sounds[button_key]

        self.mode_buttons[button_key].config(
            bg="#334155",
            fg="#f8fafc",
            relief="raised"
        )

        self.refresh_status_display()

    def toggle_man_mode(self):
        if self.man_active:
            self.stop_man_mode()
            return

        sound = self.sounds.get("SIREN3")

        if sound:
            self.man_channel.stop()
            self.man_channel.play(sound, loops=-1)
            self.man_active = True

            self.mode_buttons["MAN"].config(
                bg="#ef4444",
                fg="#ffffff",
                relief="sunken"
            )

            self.refresh_status_display()

    def stop_man_mode(self):
        self.man_channel.stop()
        self.man_active = False

        self.mode_buttons["MAN"].config(
            bg="#334155",
            fg="#f8fafc",
            relief="raised"
        )

        self.refresh_status_display()

    def toggle_yelp(self):
        if self.yelp_active:
            self.stop_yelp_toggle()
            return

        sound = self.sounds.get("SIREN2")

        if sound:
            self.yelp_channel.stop()
            self.yelp_channel.play(sound, loops=-1)
            self.yelp_active = True

            self.mode_buttons["YELP"].config(
                bg="#ef4444",
                fg="#ffffff",
                relief="sunken"
            )

            self.refresh_status_display()

    def stop_yelp_toggle(self):
        self.yelp_channel.stop()
        self.yelp_active = False

        self.mode_buttons["YELP"].config(
            bg="#334155",
            fg="#f8fafc",
            relief="raised"
        )

        self.refresh_status_display()

    def refresh_status_display(self):
        if self.active_momentary_sounds:
            active_button = next(iter(self.active_momentary_sounds))

            self.update_status(
                f"OVERRIDE: {active_button}",
                mode="warning"
            )
        elif self.man_active and self.yelp_active:
            self.update_status(
                "DUAL TONE (YELP + MAN)",
                mode="active"
            )
        elif self.man_active:
            self.update_status(
                "MANUAL OVERRIDE ACTIVE",
                mode="active"
            )
        elif self.yelp_active:
            self.update_status(
                "YELP SIREN ACTIVE",
                mode="active"
            )
        else:
            self.update_status(
                "STANDBY - ALL QUIET",
                mode="standby"
            )

    def setup_ui(self):
        outer = tk.Frame(
            self.root,
            bg="#1e293b",
            bd=2,
            relief="flat"
        )
        outer.pack(
            padx=20,
            pady=20,
            fill="both",
            expand=True
        )

        self.title_label = tk.Label(
            outer,
            text="EMERGENCY SIREN CONTROL UNIT\n[F11: Fullscreen | ESC: Windowed]",
            font=("Consolas", 12, "bold"),
            bg="#1e293b",
            fg="#94a3b8",
            pady=10
        )
        self.title_label.pack(
            side="top",
            fill="x"
        )

        self.status_label = tk.Label(
            outer,
            text="● STATUS: STANDBY - ALL QUIET",
            font=("Consolas", 11, "bold"),
            bg="#0f172a",
            fg="#10b981",
            bd=2,
            relief="sunken",
            anchor="center",
            padx=10,
            pady=8
        )
        self.status_label.pack(
            fill="x",
            side="bottom",
            padx=15,
            pady=(0, 15)
        )

        grid_frame = tk.Frame(
            outer,
            bg="#1e293b"
        )
        grid_frame.pack(
            expand=True,
            fill="both",
            padx=15,
            pady=10
        )

        self.mode_buttons = {}

        button_style = {
            "font": ("Helvetica", 12, "bold"),
            "bd": 4,
            "relief": "raised",
            "bg": "#334155",
            "fg": "#f8fafc",
            "activebackground": "#475569",
            "activeforeground": "#ffffff",
            "cursor": "hand2"
        }

        yelp_button = tk.Button(
            grid_frame,
            text="YELP\n(TOGGLE)",
            command=self.toggle_yelp,
            **button_style
        )
        yelp_button.grid(
            row=0,
            column=0,
            padx=10,
            pady=10,
            sticky="nsew"
        )
        self.mode_buttons["YELP"] = yelp_button

        man_button = tk.Button(
            grid_frame,
            text="MAN\n(TOGGLE)",
            command=self.toggle_man_mode,
            **button_style
        )
        man_button.grid(
            row=0,
            column=1,
            padx=10,
            pady=10,
            sticky="nsew"
        )
        self.mode_buttons["MAN"] = man_button

        wail_button = tk.Button(
            grid_frame,
            text="WAIL\n(HOLD)",
            **button_style
        )
        wail_button.bind(
            "<ButtonPress-1>",
            lambda event: self.start_momentary("SIREN2", "WAIL")
        )
        wail_button.bind(
            "<ButtonRelease-1>",
            lambda event: self.stop_momentary("SIREN2", "WAIL")
        )
        wail_button.grid(
            row=1,
            column=0,
            padx=10,
            pady=10,
            sticky="nsew"
        )
        self.mode_buttons["WAIL"] = wail_button

        brr_button = tk.Button(
            grid_frame,
            text="BRR BRR\n(HOLD)",
            **button_style
        )
        brr_button.bind(
            "<ButtonPress-1>",
            lambda event: self.start_momentary("BRBR", "BRR BRR")
        )
        brr_button.bind(
            "<ButtonRelease-1>",
            lambda event: self.stop_momentary("BRBR", "BRR BRR")
        )
        brr_button.grid(
            row=1,
            column=1,
            padx=10,
            pady=10,
            sticky="nsew"
        )
        self.mode_buttons["BRR BRR"] = brr_button

        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)
        grid_frame.rowconfigure(0, weight=1)
        grid_frame.rowconfigure(1, weight=1)

    def on_close(self):
        pygame.mixer.stop()
        pygame.mixer.quit()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SirenController(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

print('EZ KIDDDDDDDD LOL (easter egg)')
