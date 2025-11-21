# Choose your own adventure game
import tkinter as tk
from tkinter import font as tkFont
try:
    from PIL import Image, ImageTk
    from tkinter import messagebox
except ImportError:
    print("="*60)
    print("ERROR: The 'Pillow' library is required but not found.")
    print("Even if you have installed it before, it might not be available")
    print("to the specific Python interpreter running this script.")
    print("\nTo fix this, please run the following command in your terminal:")
    print("python -m pip install Pillow")
    print("="*60)
    exit()
try:
    import pygame
except ImportError:
    print("="*60)
    print("ERROR: The 'pygame' library is required for sound effects.")
    print("\nTo fix this, please run the following command in your terminal:")
    print("python -m pip install pygame")
    print("="*60)
    exit()
try:
    import requests
except ImportError:
    print("="*60)
    print("ERROR: The 'requests' library is required for auto-downloading assets.")
    print("\nTo fix this, please run the following command in your terminal:")
    print("python -m pip install requests")
    print("="*60)
    exit()
import os
import json

class AdventureGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Your Awesome Adventure")
        self.geometry("800x600")
        self.maxsize(1200, 900) # Set maximum width to 1200 and maximum height to 900
        self.resizable(True, True) # Allow resizing, but constrained by maxsize

        # To handle image resizing
        self.bg_image = None
        self.original_img = None

        # Create a container frame
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Define the path to the images folder on the desktop
        self.image_dir = os.path.join(os.path.expanduser("~"), "Desktop", "images")
        
        # Define path for save files
        self.save_dir = os.path.join(os.path.expanduser("~"), "Desktop", "adventure_saves")
        os.makedirs(self.save_dir, exist_ok=True)

        # --- Sound Setup ---
        self.sound_enabled = True
        # Try to initialize the mixer with a few common settings
        configs = [
            {'frequency': 44100, 'size': -16, 'channels': 2, 'buffer': 512},
            {'frequency': 22050, 'size': -16, 'channels': 2, 'buffer': 512},
            {}, # Default
        ]
        for config in configs:
            try:
                pygame.mixer.init(**config)
                self.sound_enabled = True
                print(f"Pygame mixer initialized successfully with settings: {pygame.mixer.get_init()}")
                break # Success, exit the loop
            except (NotImplementedError, pygame.error):
                continue # Try next config
        else: # This 'else' belongs to the 'for' loop, runs if loop completes without break
            self.sound_enabled = False
            print("="*60)
            print("WARNING: Pygame mixer could not be initialized. Sound will be disabled.")
            print("\nThis usually means there's an issue with your Pygame installation or audio drivers.")
            print("On macOS, the recommended fix is to use Homebrew to install dependencies:")
            print("brew install sdl2 sdl2_image sdl2_mixer sdl2_ttf portmidi")
            print("Then, reinstall pygame: python -m pip install --force-reinstall pygame")
            print("="*60)

        self.sound_dir = os.path.join(os.path.expanduser("~"), "Desktop", "sounds")
        self.click_sound = self.load_sound("button_click.wav")
        self.scene_change_sound = self.load_sound("scene_change.wav")
        self.win_sound = self.load_sound("win.wav")
        self.lose_sound = self.load_sound("lose.wav")

        # Load menu music separately using the music stream
        self.load_menu_music("menu_music.mp3")

        self.story_font = tkFont.Font(family="Helvetica", size=14)
        self.button_font = tkFont.Font(family="Helvetica", size=12)

        self.show_main_menu()

    def download_asset(self, url, file_path):
        """Downloads a file from a URL if it doesn't exist."""
        if os.path.exists(file_path):
            return True
        print(f"Downloading missing asset: {os.path.basename(file_path)}...")
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise an exception for bad status codes
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("Download complete.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {url}: {e}")
            return False

    def load_sound(self, sound_file):
        """Loads a sound file from the sound directory. Returns None on error."""
        if not self.sound_enabled:
            return type('DummySound', (object,), {'play': lambda: None})()
        path = os.path.join(self.sound_dir, sound_file)
        # Define URLs for default sounds
        sound_urls = {
            "button_click.wav": "https://www.soundjay.com/buttons/button-1.wav",
            "scene_change.wav": "https://www.soundjay.com/misc/wind-chime-1.wav",
            "win.wav": "https://www.soundjay.com/misc/bell-ringing-05.wav",
            "lose.wav": "https://www.soundjay.com/misc/fail-trombone-01.wav"
        }
        # Download if the file is missing and a URL is available
        if not os.path.exists(path) and sound_file in sound_urls:
            self.download_asset(sound_urls[sound_file], path)

        if not os.path.exists(path): # Check again after attempting download
            print(f"Warning: Could not load sound file at {path}")
            return type('DummySound', (object,), {'play': lambda: None})() # Return dummy sound
        return pygame.mixer.Sound(path)

    def load_menu_music(self, music_file):
        """Loads the background music file."""
        if not self.sound_enabled:
            return
        path = os.path.join(self.sound_dir, music_file)
        music_url = "https://www.soundjay.com/music/sounds/dream-a-little-dream-of-me-jazz-version-115.mp3"
        if not os.path.exists(path):
            self.download_asset(music_url, path)
        
        if os.path.exists(path):
            pygame.mixer.music.load(path)
        else:
            print(f"Warning: Could not load menu music file at {path}")

    def quit(self):
        """Gracefully quits the application by shutting down Pygame first."""
        pygame.quit()
        super().quit()

    def load_image(self, image_file):
        """Loads an image, downloading it if it's missing."""
        path = os.path.join(self.image_dir, image_file)
        # Using a placeholder service for demonstration.
        # You would replace this with your actual image URLs.
        image_url = f"https://via.placeholder.com/800x600.png/000000/FFFFFF?text={image_file.replace('.png', '')}"
        
        if not os.path.exists(path):
            self.download_asset(image_url, path)
        return path

    def _resize_image(self, event):
        """Resizes the background image to fill the window when it's resized."""
        if not hasattr(self, 'original_img') or self.original_img is None:
            return

        # Get the new size of the container
        new_width = self.container.winfo_width()
        new_height = self.container.winfo_height()

        # Avoid resizing to 1x1 at startup or if window is minimized
        if new_width < 2 or new_height < 2:
            return

        # Resize the original image (stretches to fit)
        try:
            # For modern Pillow versions (>= 9.1.0)
            from PIL.Image import Resampling
            resample_filter = Resampling.LANCZOS
        except ImportError:
            # For older Pillow versions
            from PIL import Image
            resample_filter = Image.LANCZOS

        resized_img = self.original_img.resize((new_width, new_height), resample_filter)
        self.bg_image = ImageTk.PhotoImage(resized_img)

        # Update the background label's image
        if hasattr(self, 'bg_label'):
            self.bg_label.config(image=self.bg_image)

    def start_game(self):
        """Initializes/resets the game state and starts Chapter 1."""
        if self.sound_enabled:
            # Stop menu music when the game starts
            pygame.mixer.music.stop()

        self.inventory = []
        self.companions = []
        self.current_chapter_start_method = self.chapter_one_start
        self.current_scene_method = self.chapter_one_start # Track current scene for saving
        # You can ask for the player's name here if you wish
        # For simplicity, we'll jump right into the story.
        self.chapter_one_start()

    def clear_frame(self):
        """Clears all widgets from the container frame."""
        for widget in self.container.winfo_children():
            widget.destroy()

    def create_status_bar(self):
        """Creates and displays the status bar for inventory and companions."""
        status_frame = tk.Frame(self.container, bg="#222222")
        status_frame.place(relx=0, rely=0, relwidth=1, anchor="nw")

        inventory_text = "Inventory: " + (", ".join(self.inventory) if self.inventory else "Empty")
        inv_label = tk.Label(status_frame, text=inventory_text, fg="gold", bg="#222222", font=("Courier", 10, "bold"), padx=10, pady=5, anchor="w")
        inv_label.pack(side="left")

        companions_text = "Companions: " + (", ".join(self.companions) if self.companions else "None")
        comp_label = tk.Label(status_frame, text=companions_text, fg="gold", bg="#222222", font=("Courier", 10, "bold"), padx=10, pady=5, anchor="e")
        comp_label.pack(side="right")


    def show_scene(self, image_path, story_text, choices, sound_to_play=None):
        """Displays a new scene with an image, text, and buttons."""
        self.clear_frame()
        self.container.unbind("<Configure>") # Unbind previous listener

        # Play the specified sound, or the default scene change sound
        if self.sound_enabled and sound_to_play:
            sound_to_play.play()
        elif self.sound_enabled:
            self.scene_change_sound.play()

        # --- Background Image Display ---
        full_image_path = self.load_image(image_path)
        self.bg_label = tk.Label(self.container)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        try:
            self.original_img = Image.open(full_image_path)
            self.container.bind("<Configure>", self._resize_image)
            # Force an update to get initial size and trigger configure event
            self.container.update_idletasks()
            # Manually call the resize function once to draw the initial image
            self._resize_image(None)
        except FileNotFoundError:
            print(f"Error: Image not found at {full_image_path}")
            self.original_img = None
            # Show a placeholder text on the background label
            self.bg_label.config(text=f"Image not found:\n{image_path}", compound="center")

        # --- Status Bar ---
        self.create_status_bar()

        # --- Content Frame for text and buttons ---
        # Using a frame to provide a background for readability
        content_frame = tk.Frame(self.container) # Removed background
        content_frame.place(relx=0.5, rely=0.98, anchor="s") # Place at bottom-center

        # --- Story Text ---
        story_label = tk.Label(content_frame, text=story_text, font=self.story_font, wraplength=750, justify="center", bg="black", fg="white")
        story_label.pack(pady=(10, 20), padx=20)

        # --- Choice Buttons ---
        buttons_frame = tk.Frame(content_frame, bg="black") # Set background to black to match label
        buttons_frame.pack(pady=(0, 10), padx=10)

        for text, command in choices.items():
            # Wrap the original command to play a sound first
            def button_action(cmd=command):
                if self.sound_enabled:
                    self.click_sound.play()
                # Update the current scene method name before executing
                self.current_scene_method = cmd.__name__
                cmd()

            button = tk.Button(buttons_frame, text=text, command=button_action, font=self.button_font, padx=10, pady=5)
            button.pack(side="left", padx=10)
            
        # Add a menu button to every scene
        menu_button = tk.Button(self.container, text="Menu", command=self.show_pause_menu, font=self.button_font)
        menu_button.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=40)

    def show_end_scene(self, image_path, story_text, is_win):
        """Displays a final win/lose scene with an option to restart."""
        self.clear_frame() # Clear first to stop previous sound
        end_text = f"{story_text}\n"
        choices = {}

        if is_win:
            end_text += "You Win!"
            sound = self.win_sound
            choices["Play Again"] = self.show_main_menu # Return to main menu on win
        else:
            end_text += "You Lose."
            sound = self.lose_sound
            choices["Try Again"] = self.current_chapter_start_method # Restart from chapter

        choices["Quit"] = self.quit
        # Call the main show_scene method, passing the appropriate win/lose sound
        self.show_scene(image_path, end_text, choices, sound_to_play=sound)

    def show_main_menu(self):
        """Displays the main menu screen."""
        self.clear_frame()
        self.container.unbind("<Configure>") # Unbind previous listener

        if self.sound_enabled:
            pygame.mixer.music.play(loops=-1) # Play music on a loop

        # --- Optional Menu Image ---
        menu_image_path = self.load_image("main_menu.png")
        self.bg_label = tk.Label(self.container)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        try:
            self.original_img = Image.open(menu_image_path)
            self.container.bind("<Configure>", self._resize_image)
            self.container.update_idletasks()
            # Manually call the resize function once to draw the initial image
            self._resize_image(None)
            
            # If image exists, show title over it
            title_font = tkFont.Font(family="Papyrus", size=32, weight="bold")
            # Create a frame for the title to give it a semi-transparent background
            title_frame = tk.Frame(self.container, bg='white')
            title_label = tk.Label(title_frame, text="Your Awesome Adventure", font=title_font, fg="darkblue", bg=title_frame['bg'], padx=10, pady=5)
            title_label.pack()
            title_frame.pack(pady=(100,20))

        except FileNotFoundError:
            self.original_img = None
            # If no image, just show a title
            title_font = tkFont.Font(family="Papyrus", size=32, weight="bold")
            title_label = tk.Label(self.container, text="Your Awesome Adventure", font=title_font, fg="darkblue")
            title_label.pack(pady=(100, 20))

        # --- Menu Buttons ---
        # Place buttons directly in the container instead of a separate frame
        start_button = tk.Button(self.container, text="New Game", command=self.start_game, font=self.button_font, padx=20, pady=10, highlightthickness=0, bd=0)
        start_button.pack(side="top")

        load_button = tk.Button(self.container, text="Load Game", command=lambda: self.show_load_menu(from_pause=False), font=self.button_font, padx=20, pady=10, highlightthickness=0, bd=0)
        load_button.pack(side="top", pady=10)

        quit_button = tk.Button(self.container, text="Quit", command=self.quit, font=self.button_font, padx=20, pady=10, highlightthickness=0, bd=0)
        quit_button.pack(side="top")

    def show_pause_menu(self):
        """Displays the pause menu over the current scene."""
        pause_frame = tk.Frame(self.container, bg="black")
        pause_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(pause_frame, text="Paused", font=("Helvetica", 24, "bold"), bg="black", fg="white").pack(pady=20, padx=50)

        resume_button = tk.Button(pause_frame, text="Resume", command=pause_frame.destroy, font=self.button_font, padx=20, pady=10)
        resume_button.pack(pady=5)

        save_button = tk.Button(pause_frame, text="Save Game", command=self.show_save_menu, font=self.button_font, padx=20, pady=10)
        save_button.pack(pady=5)

        load_button = tk.Button(pause_frame, text="Load Game", command=lambda: self.show_load_menu(from_pause=True), font=self.button_font, padx=20, pady=10)
        load_button.pack(pady=5)

        main_menu_button = tk.Button(pause_frame, text="Main Menu", command=self.show_main_menu, font=self.button_font, padx=20, pady=10)
        main_menu_button.pack(pady=(5, 20))

    def show_save_menu(self):
        """Shows the menu for choosing a save slot."""
        self.show_slot_menu("save")

    def show_load_menu(self, from_pause):
        """Shows the menu for choosing a load slot."""
        self.show_slot_menu("load", from_pause)

    def show_slot_menu(self, mode, from_pause=False):
        """Generic menu for save/load slots."""
        slot_frame = tk.Frame(self.container, bg="black")
        slot_frame.place(relx=0.5, rely=0.5, anchor="center")

        title = "Save Game" if mode == "save" else "Load Game"
        tk.Label(slot_frame, text=title, font=("Helvetica", 24, "bold"), bg="black", fg="white").pack(pady=20, padx=50)

        for i in range(1, 3):
            slot_path = os.path.join(self.save_dir, f"save_{i}.json")
            slot_text = f"Slot {i}: "
            if os.path.exists(slot_path):
                slot_text += "In Use"
            else:
                slot_text += "Empty"

            if mode == "save":
                action = lambda s=i: self.save_game(s)
            else:
                action = lambda s=i: self.load_game(s)

            tk.Button(slot_frame, text=slot_text, command=action, font=self.button_font, padx=20, pady=10).pack(pady=5)

        back_cmd = slot_frame.destroy if from_pause else self.show_main_menu
        tk.Button(slot_frame, text="Back", command=back_cmd, font=self.button_font, padx=20, pady=10).pack(pady=(5, 20))

    def save_game(self, slot_number):
        """Saves the current game state to a file."""
        state = {
            "inventory": self.inventory,
            "companions": self.companions,
            "current_chapter_start_method_name": self.current_chapter_start_method.__name__,
            "current_scene_method_name": self.current_scene_method
        }
        save_path = os.path.join(self.save_dir, f"save_{slot_number}.json")
        with open(save_path, 'w') as f:
            json.dump(state, f)
        
        messagebox.showinfo("Game Saved", f"Game saved to Slot {slot_number}.")
        # After saving, just destroy the menus and return to the paused game.
        self.container.winfo_children()[-1].destroy() # Destroys the slot menu
        self.container.winfo_children()[-1].destroy() # Destroys the pause menu

    def load_game(self, slot_number):
        """Loads the game state from a file."""
        save_path = os.path.join(self.save_dir, f"save_{slot_number}.json")
        if not os.path.exists(save_path):
            messagebox.showerror("Error", "Save file not found.")
            return

        with open(save_path, 'r') as f:
            state = json.load(f)

        self.inventory = state["inventory"]
        self.companions = state["companions"]
        self.current_chapter_start_method = getattr(self, state["current_chapter_start_method_name"])
        self.current_scene_method = state["current_scene_method_name"] # Store the name
        scene_to_load_func = getattr(self, self.current_scene_method) # Get the function
        
        # Stop menu music if it's playing before loading the scene
        if self.sound_enabled:
            pygame.mixer.music.stop()

        # Call the function to load the scene
        scene_to_load_func()


    # --- Chapter 1 Scenes ---
    # Goal: Find the path to the village.
    def chapter_one_start(self):
        self.current_chapter_start_method = self.chapter_one_start
        story = "Your adventure begins on a dusty road that splits. A weathered signpost points in different directions. Where do you go?"
        choices = {
            "Follow the sign towards the woods": self.chapter_one_step_2,
            "Take the path towards the mountains": self.chapter_one_fail_cliff,
            "Follow the river downstream": self.chapter_one_fail_rapids,
            "Rest under a nearby tree": self.chapter_one_fail_sleep
        }
        self.show_scene("road_fork.png", story, choices)

    def chapter_one_step_2(self):
        story = "The woods grow dark. You hear a rustling in the bushes. What do you do?"
        choices = {
            "Investigate the sound": self.chapter_one_fail_wolf,
            "Shout loudly": self.chapter_one_fail_bandits,
            "Continue cautiously on the path": self.chapter_one_step_3,
            "Climb a tree to hide": self.chapter_one_fail_stuck
        }
        self.show_scene("dark_woods.png", story, choices)

    def chapter_one_step_3(self):
        story = "You find a wobbly rope bridge over a chasm. It looks risky."
        choices = {
            "Cross the bridge carefully": self.chapter_one_step_4,
            "Try to find another way around": self.chapter_one_fail_lost,
            "Test the bridge by throwing a rock on it": self.chapter_one_fail_bridge_collapse,
            "Turn back": self.chapter_one_start
        }
        self.show_scene("wobbly_bridge.png", story, choices)

    def chapter_one_step_4(self):
        story = "After crossing, you see smoke rising in the distance. It could be a sign of civilization or danger."
        choices = {
            "Head towards the smoke": self.chapter_one_step_5,
            "Avoid the smoke and go the other way": self.chapter_one_fail_swamp,
            "Wait and observe from a distance": self.chapter_one_fail_nightfall,
            "Shout 'Hello!'": self.chapter_one_fail_goblins
        }
        self.show_scene("distant_smoke.png", story, choices)

    def chapter_one_step_5(self):
        story = "You find a peaceful village. The villagers welcome you warmly. You have completed Chapter 1!"
        choices = {"Continue to Chapter 2": self.chapter_two_start}
        self.show_scene("village.png", story, choices)

    # --- Chapter 1 Fails ---
    def chapter_one_fail_cliff(self):
        self.show_end_scene("cliff_edge.png", "The mountain path leads to a dead end at a sheer cliff.", is_win=False)
    def chapter_one_fail_rapids(self):
        self.show_end_scene("rapids.png", "The river quickly turns into dangerous rapids, and you are swept away.", is_win=False)
    def chapter_one_fail_sleep(self):
        self.show_end_scene("forest_night.png", "You fall into a deep sleep and wake up to find your pack has been stolen.", is_win=False)
    def chapter_one_fail_wolf(self):
        self.show_end_scene("wolf.png", "A hungry wolf leaps from the bushes!", is_win=False)
    def chapter_one_fail_bandits(self):
        self.show_end_scene("bandits.png", "Your shouting attracts bandits, who rob you of your belongings.", is_win=False)
    def chapter_one_fail_stuck(self):
        self.show_end_scene("tree_stuck.png", "You climb the tree, but get stuck on a branch until nightfall.", is_win=False)
    def chapter_one_fail_lost(self):
        self.show_end_scene("deep_woods.png", "You wander for hours trying to find another way and become hopelessly lost.", is_win=False)
    def chapter_one_fail_bridge_collapse(self):
        self.show_end_scene("broken_bridge.png", "The rock's impact is enough to make the old bridge crumble into the chasm.", is_win=False)
    def chapter_one_fail_swamp(self):
        self.show_end_scene("swamp.png", "Avoiding the smoke leads you directly into a foul-smelling swamp.", is_win=False)
    def chapter_one_fail_nightfall(self):
        self.show_end_scene("forest_night.png", "You wait too long. Night falls, and strange creatures begin to howl.", is_win=False)
    def chapter_one_fail_goblins(self):
        self.show_end_scene("goblins.png", "Your shout is answered by a band of goblins who were tending the fire.", is_win=False)

    # --- Chapter 2 Scenes ---
    # Goal: Accept the quest and leave the village.
    def chapter_two_start(self):
        self.current_chapter_start_method = self.chapter_two_start
        story = "The village elder approaches you, his face etched with worry. 'Stranger,' he says, 'we are in grave need of help.'"
        choices = {
            "Listen intently": self.chapter_two_step_2,
            "Ask for payment first": self.chapter_two_fail_insult,
            "Dismiss him as a local rambler": self.chapter_two_fail_leave,
            "Offer to help without question": self.chapter_two_fail_naive
        }
        self.show_scene("village_elder.png", story, choices)

    def chapter_two_step_2(self):
        story = "'A dragon has made its lair in the mountains,' he explains. 'Its presence sours our crops. We need someone to defeat it.'"
        choices = {
            "Agree to help the village": self.chapter_two_step_3,
            "Decline the quest": self.chapter_two_fail_leave,
            "Say the task is impossible": self.chapter_two_fail_coward,
            "Demand a map and supplies": self.chapter_two_fail_greedy
        }
        self.show_scene("elder_talking.png", story, choices)

    def chapter_two_step_3(self):
        story = "The elder is relieved. 'Thank you, brave traveler. We don't have much, but we can offer you this sturdy shield.'"
        self.inventory.append("Sturdy Shield")
        choices = {
            "Accept the shield and prepare to leave": self.chapter_two_step_4,
            "Refuse the shield, saying you travel light": self.chapter_two_fail_no_shield,
            "Ask for a weapon instead": self.chapter_two_fail_unprepared,
            "Ask for gold instead": self.chapter_two_fail_greedy
        }
        self.show_scene("village_shield.png", story, choices)

    def chapter_two_step_4(self):
        story = "As you prepare to depart, a young woman approaches. 'I am a healer,' she says. 'May I join you? My skills could be useful.'"
        choices = {
            "Accept her offer": self.chapter_two_step_5_companion,
            "Politely decline": self.chapter_two_step_5_solo,
            "Question her motives": self.chapter_two_fail_distrust,
            "Tell her it's too dangerous": self.chapter_two_fail_arrogant
        }
        self.show_scene("healer_companion.png", story, choices)

    def chapter_two_step_5_companion(self):
        story = "You agree, and Elara the healer joins your party. Together, you leave the village. You have completed Chapter 2!"
        self.companions.append("Elara the Healer")
        choices = {"Continue to Chapter 3": self.chapter_three_start}
        self.show_scene("leaving_village_party.png", story, choices)

    def chapter_two_step_5_solo(self):
        story = "You decide to go alone and leave the village, shield in hand. You have completed Chapter 2!"
        choices = {"Continue to Chapter 3": self.chapter_three_start}
        self.show_scene("leaving_village.png", story, choices)

    # --- Chapter 2 Fails ---
    def chapter_two_fail_insult(self):
        self.show_end_scene("elder_angry.png", "The elder is insulted by your avarice and asks you to leave the village at once.", is_win=False)
    def chapter_two_fail_leave(self):
        self.show_end_scene("leaving_village.png", "You leave the village to its fate, your adventure ending before it truly began.", is_win=False)
    def chapter_two_fail_naive(self):
        self.show_end_scene("goblins.png", "Your blind trust leads you into a goblin trap just outside the village.", is_win=False)
    def chapter_two_fail_coward(self):
        self.show_end_scene("village_disappointed.png", "The villagers see you as a coward and shun you.", is_win=False)
    def chapter_two_fail_greedy(self):
        self.show_end_scene("elder_angry.png", "The elder sees greed in your heart and rescinds his offer.", is_win=False)
    def chapter_two_fail_no_shield(self):
        self.show_end_scene("leaving_village.png", "You leave without the shield. A sense of regret follows you.", is_win=False)
    def chapter_two_fail_unprepared(self):
        self.show_end_scene("village_disappointed.png", "The village has no weapons to spare. They see you as unprepared and doubt your abilities.", is_win=False)
    def chapter_two_fail_distrust(self):
        self.show_end_scene("healer_sad.png", "Your distrust offends the healer, and she turns away.", is_win=False)
    def chapter_two_fail_arrogant(self):
        self.show_end_scene("healer_sad.png", "Your arrogance wounds her pride. She wishes you luck, but stays behind.", is_win=False)

    # --- Chapter 3 Scenes ---
    # Goal: Navigate the forest and find the second companion.
    def chapter_three_start(self):
        self.current_chapter_start_method = self.chapter_three_start
        story = "The path leads into a dense, ancient forest. The trail splits. One path is overgrown, the other seems well-trodden."
        choices = {
            "Take the overgrown path": self.chapter_three_step_2,
            "Take the well-trodden path": self.chapter_three_fail_trap,
            "Try to go through the middle": self.chapter_three_fail_thorns,
            "Rest and eat": self.chapter_three_fail_ants
        }
        self.show_scene("forest_path_split.png", story, choices)

    def chapter_three_step_2(self):
        story = "The overgrown path is difficult, but you find a set of tracks. They look humanoid, but large."
        choices = {
            "Follow the tracks": self.chapter_three_step_3,
            "Ignore them and make your own path": self.chapter_three_fail_lost,
            "Set a trap here": self.chapter_three_fail_self_trap,
            "Call out to see who is there": self.chapter_three_fail_spiders
        }
        self.show_scene("forest_tracks.png", story, choices)

    def chapter_three_step_3(self):
        story = "The tracks lead to a clearing where a large, gruff-looking dwarf is struggling with a broken axe."
        choices = {
            "Offer to help him": self.chapter_three_step_4,
            "Draw your weapon": self.chapter_three_fail_dwarf_fight,
            "Sneak around him": self.chapter_three_fail_dwarf_spot,
            "Watch from a distance": self.chapter_three_fail_dwarf_leaves
        }
        self.show_scene("dwarf_clearing.png", story, choices)

    def chapter_three_step_4(self):
        story = "'Hmph. Thanks,' the dwarf grunts as you help fix the axe. 'I am Borin. You're heading to the mountain? A fool's errand... but I like your spirit. I'll join you.'"
        choices = {
            "Welcome Borin to the group": self.chapter_three_step_5,
            "Say you work alone": self.chapter_three_fail_dwarf_insult,
            "Ask what's in it for him": self.chapter_three_fail_dwarf_suspicious,
            "Stay silent": self.chapter_three_fail_dwarf_awkward
        }
        self.show_scene("dwarf_joins.png", story, choices)

    def chapter_three_step_5(self):
        story = "Borin the dwarf, a powerful warrior, is now your companion. The forest path seems less daunting. You have completed Chapter 3!"
        if len(self.companions) < 2:
            self.companions.append("Borin the Warrior")
        choices = {"Continue to Chapter 4": self.chapter_four_start}
        self.show_scene("forest_with_party.png", story, choices)

    # --- Chapter 3 Fails ---
    def chapter_three_fail_trap(self):
        self.show_end_scene("snare_trap.png", "The well-trodden path was a lure. You step into a hunter's snare.", is_win=False)
    def chapter_three_fail_thorns(self):
        self.show_end_scene("thorn_bush.png", "You try to forge your own path and get hopelessly tangled in thorn bushes.", is_win=False)
    def chapter_three_fail_ants(self):
        self.show_end_scene("ant_hill.png", "You accidentally sit on a giant ant hill. They are not happy.", is_win=False)
    def chapter_three_fail_lost(self):
        self.show_end_scene("deep_woods.png", "You ignore the tracks and quickly become lost in the dense, featureless woods.", is_win=False)
    def chapter_three_fail_spiders(self):
        self.show_end_scene("giant_spider.png", "Your call is answered by giant spiders descending from the canopy.", is_win=False)
    def chapter_three_fail_self_trap(self):
        self.show_end_scene("snare_trap.png", "You are clumsy while setting the trap and catch your own foot.", is_win=False)
    def chapter_three_fail_dwarf_fight(self):
        self.show_end_scene("dwarf_angry.png", "The dwarf is a seasoned warrior and easily disarms you.", is_win=False)
    def chapter_three_fail_dwarf_spot(self):
        self.show_end_scene("dwarf_angry.png", "The dwarf's keen eyes spot you. 'A spy!' he yells, and attacks.", is_win=False)
    def chapter_three_fail_dwarf_leaves(self):
        self.show_end_scene("dwarf_walking_away.png", "You wait too long. The dwarf fixes his axe and leaves, ignoring you.", is_win=False)
    def chapter_three_fail_dwarf_insult(self):
        self.show_end_scene("dwarf_angry.png", "'Fine! See if I care!' Borin shouts, offended. He storms off.", is_win=False)
    def chapter_three_fail_dwarf_suspicious(self):
        self.show_end_scene("dwarf_angry.png", "Borin eyes you with suspicion. 'I don't travel with mercenaries.' He leaves.", is_win=False)
    def chapter_three_fail_dwarf_awkward(self):
        self.show_end_scene("dwarf_walking_away.png", "Your silence makes things awkward. Borin shrugs and wanders off.", is_win=False)


    # --- Chapter 4 Scenes ---
    # Goal: Find the legendary sword.
    def chapter_four_start(self):
        self.current_chapter_start_method = self.chapter_four_start
        story = "You arrive at the entrance to a dark cave, the air thick with an ancient stillness. This must be the dragon's lair. You can light a torch or proceed in the dark."
        choices = {}
        # Add choices based on companions and items
        choices["Light a torch"] = self.chapter_four_step_2
        choices["Proceed in darkness"] = self.chapter_four_fail_chasm
        if "Borin the Warrior" in self.companions:
            choices["Have Borin use his darkvision"] = self.chapter_four_step_2
        if "Elara the Healer" in self.companions:
            choices["Ask Elara to cast a light spell"] = self.chapter_four_step_2

        self.show_scene("cave_entrance.png", story, choices)

    def chapter_four_step_2(self):
        story = "The light reveals two tunnels. One smells faintly of sulfur. The other is silent."
        choices = {
            "Right (Silent)": self.chapter_four_step_3,
            "Left (Sulfur Smell)": self.chapter_four_fail_early_dragon,
            "Check for traps": self.chapter_four_fail_no_traps,
            "Send a companion to scout": self.chapter_four_fail_split_party
        }
        self.show_scene("two_tunnels.png", story, choices)

    def chapter_four_step_3(self):
        story = "The right tunnel leads to a small chamber where an ancient, gleaming sword rests on a stone altar. It is protected by a magical barrier."
        choices = {
            "Try to break it with force": self.chapter_four_fail_barrier_blast,
            "Ask Elara to dispel it": self.chapter_four_step_4 if "Elara the Healer" in self.companions else self.chapter_four_fail_no_elara,
            "Have Borin smash it": self.chapter_four_fail_barrier_blast,
            "Look for a switch": self.chapter_four_fail_no_switch
        }
        self.show_scene("sword_in_barrier.png", story, choices)

    def chapter_four_step_4(self):
        story = "Elara chants an ancient phrase, and the barrier dissolves. You take the sword and add it to your inventory."
        self.inventory.append("Ancient Sword")
        choices = {
            "Return to the main cavern": self.chapter_four_step_5
        }
        self.show_scene("ancient_sword_taken.png", story, choices)

    def chapter_four_step_5(self):
        story = "You return to the main cavern, now holding the Ancient Sword. The only way forward is the tunnel smelling of sulfur. You have completed Chapter 4!"
        choices = {"Continue to Chapter 5": self.chapter_five_start}
        self.show_scene("two_tunnels.png", story, choices)

    # --- Chapter 4 Fails ---
    def chapter_four_fail_chasm(self):
        self.show_end_scene("chasm.png", "You try to navigate in the pitch black but misstep and fall into a deep, hidden chasm.", is_win=False)
    def chapter_four_fail_no_borin(self):
        self.show_end_scene("cave_entrance.png", "'I can't see in the dark!' you exclaim to no one in particular.", is_win=False)
    def chapter_four_fail_no_elara_magic(self):
        self.show_end_scene("cave_entrance.png", "Elara is a healer, not a mage. She has no light spell.", is_win=False)
    def chapter_four_fail_early_dragon(self):
        self.show_end_scene("dragon_fire.png", "This tunnel leads directly to the dragon's main chamber. Unprepared, you are instantly incinerated.", is_win=False)
    def chapter_four_fail_no_traps(self):
        self.show_end_scene("two_tunnels.png", "You spend an hour searching for traps and find nothing, wasting precious time.", is_win=False)
    def chapter_four_fail_split_party(self):
        self.show_end_scene("goblins.png", "You send your companion alone, and they are ambushed by cave goblins.", is_win=False)
    def chapter_four_fail_barrier_blast(self):
        self.show_end_scene("magic_explosion.png", "Touching the barrier unleashes a powerful blast of energy, knocking you out.", is_win=False)
    def chapter_four_fail_no_elara(self):
        self.show_end_scene("sword_in_barrier.png", "You don't have anyone who can dispel magic. The sword is unattainable.", is_win=False)
    def chapter_four_fail_no_switch(self):
        self.show_end_scene("sword_in_barrier.png", "You search fruitlessly for a switch. There is none.", is_win=False)

    # --- Placeholder Chapters 5-9 ---
    # Goal: Navigate the swamp and find a hidden shortcut.
    def chapter_five_start(self):
        self.current_chapter_start_method = self.chapter_five_start
        story = "The path from the cave leads into a vast, murky swamp. The air is thick and the ground is treacherous. Which way do you proceed?"
        choices = {
            "Follow mossy stones across the water": self.chapter_five_step_2,
            "Wade directly through the murky water": self.chapter_five_fail_leeches,
            "Try to swing on vines like in stories": self.chapter_five_fail_vine_snap,
            "Ask Borin to clear a path in the reeds": self.chapter_five_fail_snake_nest
        }
        self.show_scene("swamp_entrance.png", story, choices)

    def chapter_five_step_2(self):
        story = "The stones lead to a large, stagnant pool. Bubbles occasionally rise to the surface, suggesting something is below."
        choices = {
            "Carefully skirt the edge of the pool": self.chapter_five_step_3,
            "Throw a rock in to see what happens": self.chapter_five_fail_monster,
            "Attempt to build a raft from old logs": self.chapter_five_fail_raft_sinks,
            "Try to swim across quickly": self.chapter_five_fail_monster
        }
        self.show_scene("swamp_pool.png", story, choices)

    def chapter_five_step_3(self):
        story = "While moving along the edge, you find a strange, glowing plant. It pulses with a soft, calming light."
        choices = {
            "Ask Elara to examine it": self.chapter_five_step_4 if "Elara the Healer" in self.companions else self.chapter_five_fail_no_elara_plant,
            "Touch the plant": self.chapter_five_fail_paralysis,
            "Ignore it and keep moving": self.chapter_five_fail_lost_in_fog,
            "Harvest it for later": self.chapter_five_fail_paralysis
        }
        self.show_scene("glowing_plant.png", story, choices)

    def chapter_five_step_4(self):
        story = "Elara identifies it as Glimmer-root, known to repel swamp pests. She carefully harvests some. As you continue, a thick, disorienting fog rolls in."
        choices = {
            "Use the Glimmer-root to light the way": self.chapter_five_step_5,
            "Huddle together and wait for it to pass": self.chapter_five_fail_ambush,
            "Shout for help": self.chapter_five_fail_will_o_wisp,
            "Walk forward blindly": self.chapter_five_fail_lost_in_fog
        }
        self.show_scene("swamp_fog.png", story, choices)

    def chapter_five_step_5(self):
        story = "The Glimmer-root's light cuts through the fog, revealing a hidden, stable path. You navigate the rest of the swamp with ease. You have completed Chapter 5!"
        choices = {"Continue to Chapter 6": self.chapter_six_start}
        self.show_scene("swamp_exit.png", story, choices)

    # --- Chapter 5 Fails ---
    def chapter_five_fail_leeches(self):
        self.show_end_scene("swamp_leeches.png", "You are swarmed by giant leeches that drain your strength.", is_win=False)
    def chapter_five_fail_vine_snap(self):
        self.show_end_scene("broken_vine.png", "The vine snaps mid-swing, dropping you into the murky water below.", is_win=False)
    def chapter_five_fail_snake_nest(self):
        self.show_end_scene("swamp_snakes.png", "Borin's clearing of the reeds disturbs a nest of venomous snakes.", is_win=False)
    def chapter_five_fail_monster(self):
        self.show_end_scene("swamp_monster.png", "A tentacled beast erupts from the pool and pulls you under.", is_win=False)
    def chapter_five_fail_raft_sinks(self):
        self.show_end_scene("sinking_raft.png", "The logs are rotten and your makeshift raft falls apart, leaving you stranded.", is_win=False)
    def chapter_five_fail_no_elara_plant(self):
        self.show_end_scene("glowing_plant.png", "Without Elara's knowledge, you don't know what to do with the plant and wander into a disorienting fog.", is_win=False)
    def chapter_five_fail_paralysis(self):
        self.show_end_scene("paralyzed.png", "Touching the plant releases spores that paralyze you, leaving you helpless.", is_win=False)
    def chapter_five_fail_lost_in_fog(self):
        self.show_end_scene("swamp_fog.png", "You press on without a light and become hopelessly lost in the thick, magical fog.", is_win=False)
    def chapter_five_fail_ambush(self):
        self.show_end_scene("frogmen_ambush.png", "Waiting in the fog was a mistake. A tribe of frogmen ambush your party.", is_win=False)
    def chapter_five_fail_will_o_wisp(self):
        self.show_end_scene("will_o_wisp.png", "Your shouts attract a malevolent Will-o'-Wisp, which leads you to your doom.", is_win=False)
        
    # --- Chapter 6 Scenes ---
    # Goal: Ascend the mountain to reach the higher peaks.
    def chapter_six_start(self):
        self.current_chapter_start_method = self.chapter_six_start
        story = "Leaving the swamp, you stand at the base of the mountain. A steep, direct climb is ahead, but a narrow, winding path snakes along the cliff."
        choices = {
            "Take the winding path": self.chapter_six_step_2,
            "Attempt the steep direct climb": self.chapter_six_fail_fall,
            "Rest before starting the climb": self.chapter_six_fail_storm,
            "Ask Borin to find a secret passage": self.chapter_six_fail_no_passage
        }
        self.show_scene("mountain_base.png", story, choices)

    def chapter_six_step_2(self):
        story = "The narrow path is treacherous. You reach a wide gap in the ledge, too far to jump safely. A sturdy-looking rock formation is on the other side."
        choices = {
            "Have Borin throw a grappling hook": self.chapter_six_step_3 if "Borin the Warrior" in self.companions else self.chapter_six_fail_no_borin_hook,
            "Attempt a dangerous running jump": self.chapter_six_fail_jump,
            "Search for another way around": self.chapter_six_fail_dead_end,
            "Try to climb down and around the gap": self.chapter_six_fail_loose_rocks
        }
        self.show_scene("mountain_gap.png", story, choices)

    def chapter_six_step_3(self):
        story = "Borin's hook catches, and you all swing across. Higher up, the wind howls and it begins to snow heavily. You must find shelter."
        choices = {
            "Huddle together under a large rock overhang": self.chapter_six_step_4,
            "Enter a dark, narrow cave opening": self.chapter_six_fail_bear,
            "Keep pushing forward through the storm": self.chapter_six_fail_lost_in_snow,
            "Try to build a snow shelter": self.chapter_six_fail_collapse
        }
        self.show_scene("mountain_snow.png", story, choices)

    def chapter_six_step_4(self):
        story = "The storm passes. The path ahead is blocked by a territorial mountain goat with enormous horns. It paws the ground, ready to charge."
        choices = {
            "Offer it some of your rations as a distraction": self.chapter_six_step_5,
            "Try to scare it by shouting": self.chapter_six_fail_goat_charge,
            "Attempt to sneak past it": self.chapter_six_fail_goat_charge,
            "Have Borin fight it": self.chapter_six_fail_goat_fight
        }
        self.show_scene("mountain_goat.png", story, choices)

    def chapter_six_step_5(self):
        story = "The goat is distracted by the food, allowing you to pass safely. You've reached the upper slopes of the mountain! You have completed Chapter 6!"
        choices = {"Continue to Chapter 7": self.chapter_seven_start}
        self.show_scene("mountain_peak_view.png", story, choices)

    # --- Chapter 6 Fails ---
    def chapter_six_fail_fall(self):
        self.show_end_scene("mountain_fall.png", "The rock face is too sheer. You lose your grip and fall.", is_win=False)
    def chapter_six_fail_storm(self):
        self.show_end_scene("mountain_snow.png", "You wait too long. A sudden, fierce blizzard rolls in, trapping you at the base.", is_win=False)
    def chapter_six_fail_no_passage(self):
        self.show_end_scene("mountain_base.png", "'This isn't my home mountain!' Borin grumbles. 'No secret doors here.' You waste valuable time searching.", is_win=False)
    def chapter_six_fail_no_borin_hook(self):
        self.show_end_scene("mountain_gap.png", "You have no grappling hook or strong arm to throw it. The gap is impassable.", is_win=False)
    def chapter_six_fail_jump(self):
        self.show_end_scene("mountain_fall.png", "You take a running leap but don't quite make it to the other side.", is_win=False)
    def chapter_six_fail_dead_end(self):
        self.show_end_scene("mountain_ledge.png", "You search for hours but the path leads to a dead end, forcing you to turn back.", is_win=False)
    def chapter_six_fail_loose_rocks(self):
        self.show_end_scene("rockslide.png", "The rocks below are unstable. Your movement triggers a small rockslide.", is_win=False)
    def chapter_six_fail_bear(self):
        self.show_end_scene("bear_cave.png", "The cave was already occupied by a very angry bear.", is_win=False)
    def chapter_six_fail_lost_in_snow(self):
        self.show_end_scene("snow_blind.png", "You push on, but quickly become disoriented and lost in the whiteout.", is_win=False)
    def chapter_six_fail_collapse(self):
        self.show_end_scene("snow_collapse.png", "Your hastily built shelter collapses under the weight of the snow.", is_win=False)
    def chapter_six_fail_goat_charge(self):
        self.show_end_scene("goat_charge.png", "Your action provokes the goat, which charges and knocks you off the narrow path.", is_win=False)
    def chapter_six_fail_goat_fight(self):
        self.show_end_scene("goat_charge.png", "The goat is surprisingly strong and agile, easily knocking Borin aside before charging you.", is_win=False)

    # --- Chapter 7 Scenes ---
    # Goal: Find and navigate the entrance to the dragon's dungeon.
    def chapter_seven_start(self):
        self.current_chapter_start_method = self.chapter_seven_start
        story = "On the high slopes, you see several cave openings. One has large, unnatural scorch marks around it. Another is covered in ice. A third looks like a simple fissure."
        choices = {
            "Investigate the scorched cave": self.chapter_seven_step_2,
            "Enter the icy cave": self.chapter_seven_fail_frost_troll,
            "Explore the narrow fissure": self.chapter_seven_fail_dead_end_fissure,
            "Climb higher up the mountain": self.chapter_seven_fail_avalanche
        }
        self.show_scene("cave_entrances.png", story, choices)

    def chapter_seven_step_2(self):
        story = "The entrance leads to a massive, perfectly carved stone door, sealed shut. There are no visible handles or locks, only ancient dwarven runes."
        choices = {
            "Ask Borin to read the runes": self.chapter_seven_step_3 if "Borin the Warrior" in self.companions else self.chapter_seven_fail_no_dwarf,
            "Try to force the door open": self.chapter_seven_fail_door_too_strong,
            "Search for a hidden lever": self.chapter_seven_fail_no_lever,
            "Have Elara try a magic spell": self.chapter_seven_fail_magic_immune
        }
        self.show_scene("rune_door.png", story, choices)

    def chapter_seven_step_3(self):
        story = "'It's a riddle,' Borin grunts. 'Speak friend and enter... wait, no. It says 'Speak the mountain's true name'.' He tells you the name is 'Aethelgard'."
        choices = {
            "Speak 'Aethelgard' to the door": self.chapter_seven_step_4,
            "Try to trick the door by saying 'the mountain'": self.chapter_seven_fail_riddle,
            "Yell at the door in frustration": self.chapter_seven_fail_door_too_strong,
            "Write the name on the door": self.chapter_seven_fail_riddle
        }
        self.show_scene("rune_door_glowing.png", story, choices)

    def chapter_seven_step_4(self):
        story = "The great door rumbles open. Inside, a long, dark hallway is lined with pressure plates. A faint breeze carrying the smell of sulfur comes from the far end."
        choices = {
            "Follow the breeze, avoiding the plates": self.chapter_seven_step_5,
            "Walk straight down the middle": self.chapter_seven_fail_dart_trap,
            "Have Borin try to disarm the traps": self.chapter_seven_fail_trap_complex,
            "Throw a rock onto a plate to test it": self.chapter_seven_fail_dart_trap
        }
        self.show_scene("trap_hallway.png", story, choices)

    def chapter_seven_step_5(self):
        story = "You carefully navigate the hall and arrive at a huge gate. The air is hot, and you can hear the deep, rhythmic breathing of a massive creature. You have completed Chapter 7!"
        choices = {"Continue to Chapter 8": self.chapter_eight_start}
        self.show_scene("final_gate.png", story, choices)

    # --- Chapter 7 Fails ---
    def chapter_seven_fail_frost_troll(self):
        self.show_end_scene("frost_troll.png", "The icy cave is the lair of a vicious frost troll!", is_win=False)
    def chapter_seven_fail_dead_end_fissure(self):
        self.show_end_scene("narrow_cave.png", "The fissure becomes too narrow to pass through, forcing you to retreat.", is_win=False)
    def chapter_seven_fail_avalanche(self):
        self.show_end_scene("avalanche.png", "Climbing higher was a mistake. Your movement triggers a massive avalanche.", is_win=False)
    def chapter_seven_fail_no_dwarf(self):
        self.show_end_scene("rune_door.png", "No one in your party can read the ancient dwarven runes. The door remains sealed.", is_win=False)
    def chapter_seven_fail_door_too_strong(self):
        self.show_end_scene("rune_door.png", "The door is magically reinforced and doesn't budge, no matter how much force you use.", is_win=False)
    def chapter_seven_fail_no_lever(self):
        self.show_end_scene("rune_door.png", "You search for hours, but there is no hidden mechanism to be found.", is_win=False)
    def chapter_seven_fail_magic_immune(self):
        self.show_end_scene("rune_door.png", "Elara's spells have no effect on the ancient dwarven stonework.", is_win=False)
    def chapter_seven_fail_riddle(self):
        self.show_end_scene("rune_door_glowing.png", "An angry rumble echoes from the door. That was not the correct answer.", is_win=False)
    def chapter_seven_fail_dart_trap(self):
        self.show_end_scene("dart_trap.png", "You step on a pressure plate, and a volley of poison darts flies from the walls.", is_win=False)
    def chapter_seven_fail_trap_complex(self):
        self.show_end_scene("trap_hallway.png", "'These mechanisms are too intricate!' Borin says. 'I can't disarm them without setting them off.'", is_win=False)

    # --- Chapter 8 Scenes ---
    # Goal: Navigate the final dungeon corridors.
    def chapter_eight_start(self):
        self.current_chapter_start_method = self.chapter_eight_start
        story = "The great gate slams shut behind you. You are in a vast, hot cavern. The path splits around a massive central pillar."
        choices = {
            "Take the left path": self.chapter_eight_step_2,
            "Take the right path": self.chapter_eight_fail_patrol,
            "Try to climb the pillar": self.chapter_eight_fail_hot_pillar,
            "Wait and listen for sounds": self.chapter_eight_fail_patrol
        }
        self.show_scene("dungeon_entrance_hall.png", story, choices)

    def chapter_eight_step_2(self):
        story = "The path leads to a chasm filled with lava. A single, rickety chain bridge spans the gap. It looks unstable."
        choices = {
            "Cross one by one, carefully": self.chapter_eight_step_3,
            "Have everyone run across at once": self.chapter_eight_fail_bridge_collapse,
            "Try to jump the chasm": self.chapter_eight_fail_lava_jump,
            "Look for another way": self.chapter_eight_fail_lava_flow
        }
        self.show_scene("lava_bridge.png", story, choices)

    def chapter_eight_step_3(self):
        story = "Across the bridge, you enter a treasure room filled with piles of gold. The exit is on the far side, but something feels wrong."
        choices = {
            "Stick to the walls, avoiding the gold": self.chapter_eight_step_4,
            "Walk straight through the treasure": self.chapter_eight_fail_mimic,
            "Grab a handful of coins": self.chapter_eight_fail_mimic,
            "Send Borin first to test the ground": self.chapter_eight_fail_mimic
        }
        self.show_scene("treasure_room_trap.png", story, choices)

    def chapter_eight_step_4(self):
        story = "The next corridor is filled with a shimmering, magical haze. It makes you feel dizzy and confused."
        choices = {
            "Have Elara cast a cleansing prayer": self.chapter_eight_step_5 if "Elara the Healer" in self.companions else self.chapter_eight_fail_no_elara_haze,
            "Push through with sheer willpower": self.chapter_eight_fail_confusion,
            "Hold your breath and run": self.chapter_eight_fail_confusion,
            "Throw a rock into it": self.chapter_eight_fail_haze_intensifies
        }
        self.show_scene("magic_haze.png", story, choices)

    def chapter_eight_step_5(self):
        story = "Elara's prayer clears the haze. The corridor leads to a ledge overlooking a colossal cavern. The dragon is below. You have completed Chapter 8!"
        choices = {"Continue to Chapter 9": self.chapter_nine_start}
        self.show_scene("lair_overview.png", story, choices)

    # --- Chapter 8 Fails ---
    def chapter_eight_fail_patrol(self):
        self.show_end_scene("drake_patrol.png", "You run directly into a patrol of lesser drakes guarding the lair.", is_win=False)
    def chapter_eight_fail_hot_pillar(self):
        self.show_end_scene("dungeon_entrance_hall.png", "The pillar is searing hot to the touch, burning your hands.", is_win=False)
    def chapter_eight_fail_bridge_collapse(self):
        self.show_end_scene("broken_bridge.png", "The combined weight is too much! The bridge snaps, plunging you into the lava.", is_win=False)
    def chapter_eight_fail_lava_jump(self):
        self.show_end_scene("lava_chasm.png", "The chasm is far too wide. You fall short and are consumed by the lava.", is_win=False)
    def chapter_eight_fail_lava_flow(self):
        self.show_end_scene("lava_chasm.png", "You find another path, but it leads to a dead end as a fresh lava flow cuts you off.", is_win=False)
    def chapter_eight_fail_mimic(self):
        self.show_end_scene("treasure_mimic.png", "One of the treasure piles was a monstrous mimic! It attacks before you can react.", is_win=False)
    def chapter_eight_fail_no_elara_haze(self):
        self.show_end_scene("magic_haze.png", "Without a healer to dispel the magic, the confusing haze is impassable.", is_win=False)
    def chapter_eight_fail_confusion(self):
        self.show_end_scene("magic_haze.png", "You enter the haze and become hopelessly confused, wandering in circles until you collapse.", is_win=False)
    def chapter_eight_fail_haze_intensifies(self):
        self.show_end_scene("magic_haze.png", "The rock vanishes into the haze, which seems to glow brighter and become even more disorienting.", is_win=False)

    # --- Chapter 9 Scenes ---
    # Goal: Get from the high ledge to the dragon's side without waking it.
    def chapter_nine_start(self):
        self.current_chapter_start_method = self.chapter_nine_start
        story = "You're on the high ledge overlooking the dragon. To get down, you see a crumbling staircase, a thick chain hanging down, and a steep slide of loose gravel."
        choices = {
            "Take the crumbling staircase": self.chapter_nine_step_2,
            "Slide down the chain": self.chapter_nine_fail_chain_noise,
            "Use the gravel slide": self.chapter_nine_fail_rockslide,
            "Try to climb down the rock face": self.chapter_nine_fail_climb_fall
        }
        self.show_scene("lair_ledge.png", story, choices)

    def chapter_nine_step_2(self):
        story = "You reach the cavern floor. The air is hot and the ground is covered in gold coins. The slightest misstep could make a sound."
        choices = {
            "Walk on the shadowy edges of the room": self.chapter_nine_step_3,
            "Walk directly over the coins": self.chapter_nine_fail_coin_noise,
            "Try to 'swim' through the gold": self.chapter_nine_fail_coin_noise,
            "Have Borin clear a path": self.chapter_nine_fail_coin_noise
        }
        self.show_scene("treasure_floor.png", story, choices)

    def chapter_nine_step_3(self):
        story = "While sneaking, your foot bumps a stack of golden goblets. They teeter, about to crash to the floor!"
        choices = {
            "Lunge and catch them": self.chapter_nine_step_4,
            "Let them fall and brace for a fight": self.chapter_nine_fail_goblet_crash,
            "Freeze and hope they don't fall": self.chapter_nine_fail_goblet_crash,
            "Try to use magic to stop them": self.chapter_nine_fail_magic_noise
        }
        self.show_scene("goblet_fall.png", story, choices)

    def chapter_nine_step_4(self):
        story = "You catch them just in time. A small stream of molten gold blocks your path. It's too hot to cross."
        choices = {}
        # Add the shield option only if the player has it
        if "Sturdy Shield" in self.inventory:
            choices["Use your shield as a bridge"] = self.chapter_nine_step_5
        else:
            choices["Try to find something to bridge the gap"] = self.chapter_nine_fail_no_shield_bridge
        choices.update({
            "Attempt to jump over it": self.chapter_nine_fail_lava_jump,
            "Pour water on it to cool it": self.chapter_nine_fail_steam_hiss,
            "Look for another way around": self.chapter_nine_fail_dragon_stirs
        })
        self.show_scene("molten_gold_stream.png", story, choices)

    def chapter_nine_step_5(self):
        story = "You cross the stream and are now at the foot of the treasure pile. The dragon's breathing is like thunder. You are in position. You have completed Chapter 9!"
        choices = {"Continue to the Final Chapter": self.chapter_ten_start}
        self.show_scene("dragon_approach.png", story, choices)

    # --- Chapter 9 Fails ---
    def chapter_nine_fail_chain_noise(self):
        self.show_end_scene("dragon_waking.png", "The chain groans and clanks against the rock wall, causing the dragon's eye to twitch open.", is_win=False)
    def chapter_nine_fail_rockslide(self):
        self.show_end_scene("dragon_waking.png", "The gravel slide is too loud! The noise echoes through the cavern, waking the dragon.", is_win=False)
    def chapter_nine_fail_climb_fall(self):
        self.show_end_scene("chasm.png", "A handhold breaks loose and you tumble to the floor with a loud crash.", is_win=False)
    def chapter_nine_fail_coin_noise(self):
        self.show_end_scene("dragon_waking.png", "The clinking of coins is impossible to silence. The dragon stirs from its slumber.", is_win=False)
    def chapter_nine_fail_goblet_crash(self):
        self.show_end_scene("dragon_waking.png", "The goblets crash to the floor with a deafening clang. The dragon is awake and angry.", is_win=False)
    def chapter_nine_fail_magic_noise(self):
        self.show_end_scene("dragon_waking.png", "Elara's spell creates a soft 'whoosh' of air, but it's enough to alert the dragon.", is_win=False)
    def chapter_nine_fail_steam_hiss(self):
        self.show_end_scene("dragon_waking.png", "The water hits the molten gold and erupts in a loud hiss of steam. The dragon's head snaps toward the sound.", is_win=False)
    def chapter_nine_fail_dragon_stirs(self):
        self.show_end_scene("dragon_waking.png", "You take too long searching for another path. The dragon begins to stir on its own.", is_win=False)
    def chapter_nine_fail_lava_jump(self):
        self.show_end_scene("lava_chasm.png", "The stream of molten gold is wider than it looks. You fall short and are consumed.", is_win=False)

    # --- Chapter 10 Scenes (8 steps) ---
    def chapter_ten_start(self):
        self.current_chapter_start_method = self.chapter_ten_start
        story = "You venture down the sulfurous tunnel and enter a massive chamber. In the center, a great dragon sleeps atop a mountain of gold. This is it—the final confrontation."
        choices = {}
        if "Ancient Sword" in self.inventory:
            choices["Sneak closer for a surprise attack"] = self.chapter_ten_step_2
        else:
            choices["Charge with your normal weapon"] = self.chapter_ten_fail_no_sword
        choices["Try to steal some treasure"] = self.chapter_ten_fail_steal
        choices["Shout to wake it up"] = self.chapter_ten_fail_shout
        choices["Throw a rock at it"] = self.chapter_ten_fail_rock
        self.show_scene("sleeping_dragon.png", story, choices)

    def chapter_ten_step_2(self):
        story = "You sneak closer. The dragon stirs. Its massive eye begins to open. This is your only chance!"
        choices = {
            "Lunge for the weak spot on its neck": self.chapter_ten_step_3,
            "Aim for its eye": self.chapter_ten_fail_eye_poke,
            "Hesitate": self.chapter_ten_fail_hesitate,
            "Have Borin make a distraction": self.chapter_ten_step_3 if "Borin the Warrior" in self.companions else self.chapter_ten_fail_distraction
        }
        self.show_scene("dragon_waking.png", story, choices)

    def chapter_ten_step_3(self):
        story = "You strike true! The sword sinks deep, and the dragon roars in pain, thrashing wildly. It's wounded, but far from dead."
        choices = {
            "Dodge its retaliating claw swipe": self.chapter_ten_step_4,
            "Try to pull the sword out": self.chapter_ten_fail_stuck_sword,
            "Stand your ground with your shield": self.chapter_ten_fail_shield_break,
            "Run away": self.chapter_ten_fail_run_away
        }
        self.show_scene("dragon_wounded.png", story, choices)

    def chapter_ten_step_4(self):
        story = "You narrowly dodge the claw. The dragon prepares to unleash a torrent of fire!"
        choices = {
            "Hide behind a large pillar": self.chapter_ten_step_5,
            "Try to run under its belly": self.chapter_ten_fail_fire_belly,
            "Use your shield to deflect the fire": self.chapter_ten_fail_shield_melt,
            "Have Elara cast a water spell": self.chapter_ten_fail_no_water_spell if "Elara the Healer" not in self.companions else self.chapter_ten_step_5
        }
        self.show_scene("dragon_breathing_fire.png", story, choices)

    def chapter_ten_step_5(self):
        story = "The fire subsides. The dragon is momentarily winded. You see your chance to climb its back."
        choices = {
            "Scramble up its leg to its back": self.chapter_ten_step_6,
            "Attack its tail": self.chapter_ten_fail_tail_whip,
            "Throw a rock at its head": self.chapter_ten_fail_rock_annoy,
            "Ask Borin to throw you": self.chapter_ten_fail_dwarf_toss if "Borin the Warrior" not in self.companions else self.chapter_ten_step_6
        }
        self.show_scene("dragon_tired.png", story, choices)

    def chapter_ten_step_6(self):
        story = "You're on its back! The beast thrashes, trying to shake you off. You need to deliver another blow."
        choices = {
            "Stab downwards into its spine": self.chapter_ten_step_7,
            "Try to control it like a horse": self.chapter_ten_fail_rodeo,
            "Hold on for dear life": self.chapter_ten_fail_thrown,
            "Signal Elara to heal you": self.chapter_ten_fail_bad_timing_heal if "Elara the Healer" not in self.companions else self.chapter_ten_step_7
        }
        self.show_scene("dragon_back.png", story, choices)

    def chapter_ten_step_7(self):
        story = "Another successful strike! The dragon stumbles, crashing into a cavern wall, weakened."
        choices = {
            "Prepare for the final blow": self.chapter_ten_step_8,
            "Taunt the beast": self.chapter_ten_fail_taunt,
            "Try to reason with it": self.chapter_ten_fail_talk,
            "Let your companions finish it": self.chapter_ten_fail_lazy
        }
        self.show_scene("dragon_stumbling.png", story, choices)

    def chapter_ten_step_8(self):
        story = "You grip the ancient sword, which hums with power. With one final, mighty blow, you end the beast's reign. You have saved the village!"
        self.show_end_scene("dragon_slain.png", story, is_win=True)

    # --- Chapter 10 Fails ---
    def chapter_ten_fail_no_sword(self):
        story = "You bravely charge the dragon, but your common weapon shatters against its scales. It incinerates you instantly."
        self.show_end_scene("dragon_fire.png", story, is_win=False)
    def chapter_ten_fail_steal(self):
        story = "You try to sneak closer to snatch some gold, but the clinking of coins awakens the dragon. It is not pleased."
        self.show_end_scene("dragon_fire.png", story, is_win=False)
    def chapter_ten_fail_shout(self):
        self.show_end_scene("dragon_fire.png", "The dragon awakens with a roar and breathes fire before you can even move.", is_win=False)
    def chapter_ten_fail_rock(self):
        self.show_end_scene("dragon_fire.png", "The rock bounces harmlessly off its hide. The now-awake dragon is very angry.", is_win=False)
    def chapter_ten_fail_eye_poke(self):
        self.show_end_scene("dragon_fire.png", "You miss the neck and poke its eye. It roars in fury and eats you.", is_win=False)
    def chapter_ten_fail_hesitate(self):
        self.show_end_scene("dragon_fire.png", "You hesitate for a second too long. The dragon is fully awake and attacks.", is_win=False)
    def chapter_ten_fail_distraction(self):
        self.show_end_scene("dragon_fire.png", "Without Borin, there is no one to create a distraction.", is_win=False)
    def chapter_ten_fail_stuck_sword(self):
        self.show_end_scene("dragon_fire.png", "The sword is lodged deep. While you struggle, the dragon bites you in half.", is_win=False)
    def chapter_ten_fail_shield_break(self):
        self.show_end_scene("dragon_fire.png", "Your shield, even the sturdy one, shatters under the force of the blow.", is_win=False)
    def chapter_ten_fail_run_away(self):
        self.show_end_scene("dragon_fire.png", "You turn to run, but you are not fast enough to escape its fiery breath.", is_win=False)
    def chapter_ten_fail_fire_belly(self):
        self.show_end_scene("dragon_fire.png", "You run under its belly, but it simply adjusts its aim downwards.", is_win=False)
    def chapter_ten_fail_shield_melt(self):
        self.show_end_scene("dragon_fire.png", "The dragon's fire is too hot. Your shield melts, and so do you.", is_win=False)
    def chapter_ten_fail_no_water_spell(self):
        self.show_end_scene("dragon_fire.png", "Elara is a healer, not a wizard. She cannot conjure water from nothing.", is_win=False)
    def chapter_ten_fail_tail_whip(self):
        self.show_end_scene("dragon_fire.png", "You attack the tail, and it responds with a whip-like crack that sends you flying into a wall.", is_win=False)
    def chapter_ten_fail_rock_annoy(self):
        self.show_end_scene("dragon_fire.png", "The rock just annoys it. It turns and snaps you up in its jaws.", is_win=False)
    def chapter_ten_fail_dwarf_toss(self):
        self.show_end_scene("dragon_tired.png", "You look around for Borin, but he's not there to toss you.", is_win=False)
    def chapter_ten_fail_rodeo(self):
        self.show_end_scene("dragon_fire.png", "This is a dragon, not a horse. It easily throws you off and into its mouth.", is_win=False)
    def chapter_ten_fail_thrown(self):
        self.show_end_scene("chasm.png", "You are thrown from the dragon's back and fall into a deep chasm.", is_win=False)
    def chapter_ten_fail_bad_timing_heal(self):
        self.show_end_scene("dragon_back.png", "This is not the time for healing! While you are distracted, the dragon throws you off.", is_win=False)
    def chapter_ten_fail_taunt(self):
        self.show_end_scene("dragon_fire.png", "Your taunt gives it a second wind. It unleashes one last, desperate fireball.", is_win=False)
    def chapter_ten_fail_talk(self):
        self.show_end_scene("dragon_fire.png", "The dragon is not interested in conversation. It eats you.", is_win=False)
    def chapter_ten_fail_lazy(self):
        self.show_end_scene("dragon_fire.png", "This is your fight. Your companions are busy fending off its claws and cannot deliver the final blow.", is_win=False)

if __name__ == "__main__":
    # Define the path to the images folder on the desktop
    desktop_images_path = os.path.join(os.path.expanduser("~"), "Desktop", "images")
    # Create the folder on the desktop if it doesn't exist
    if not os.path.exists(desktop_images_path):
        os.makedirs(desktop_images_path)
        print(f"Created folder at: {desktop_images_path}\nPlease add your game pictures there.")

    # Define the path to the sounds folder on the desktop
    desktop_sounds_path = os.path.join(os.path.expanduser("~"), "Desktop", "sounds")
    # Create the folder on the desktop if it doesn't exist
    if not os.path.exists(desktop_sounds_path):
        os.makedirs(desktop_sounds_path)
        print(f"Created folder at: {desktop_sounds_path}\nPlease add your game sounds there (e.g., 'menu_music.mp3').")
    
    # Create saves folder
    desktop_saves_path = os.path.join(os.path.expanduser("~"), "Desktop", "adventure_saves")
    if not os.path.exists(desktop_saves_path):
        os.makedirs(desktop_saves_path)

    app = AdventureGame()
    app.mainloop()
