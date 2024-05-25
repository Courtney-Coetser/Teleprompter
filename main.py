import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, simpledialog
import os

# Function to calculate intervals based on provided dialogue and total video duration
def calculate_intervals(dialogue, total_time):
    num_prompts = len(dialogue)
    min_visible_time = 5
    extra_time_per_prompt = (total_time * 60 - (min_visible_time * num_prompts)) / num_prompts
    return min_visible_time, extra_time_per_prompt

# Tkinter Teleprompter Class
class Teleprompter(tk.Tk):
    def __init__(self, dialogue, total_time, previous_input):
        super().__init__()
        self.title("Teleprompter")
        self.dialogue = dialogue
        self.total_time_seconds = total_time * 60  # Convert minutes to seconds
        self.previous_input = previous_input
        self.current_index = 0
        self.paused = False
        self.bind("<Escape>", self.exit_to_start)  # Bind Escape to exit to start page

        self.colors = {"Speaker 1": "red", "Speaker 2": "blue"}
        self.bg_color = "#f0f0f0"  # Background color

        self.configure(bg=self.bg_color)  # Set the background color of the window

        self.label = tk.Label(self, text="", font=("Helvetica", 24), wraplength=800, justify="center", bg=self.bg_color)
        self.label.pack(pady=50)

        self.pause_button = tk.Button(self, text="Pause", command=self.toggle_pause, bg=self.bg_color)
        self.pause_button.pack()

        self.time_left_label = tk.Label(self, text="", font=("Helvetica", 12), bg=self.bg_color)
        self.time_left_label.pack(pady=20)

        self.bind("<space>", lambda event: self.toggle_pause())  # Bind spacebar to pause/resume

        global min_visible_time, extra_time_per_prompt
        min_visible_time, extra_time_per_prompt = calculate_intervals(dialogue, total_time)

        self.remaining_time = self.total_time_seconds  # Initialize remaining time
        self.update_time_left()
        self.after(1, self.run_script)  # Start the script after 1 millisecond
        self.after(1000, self.update_timer)  # Start the timer

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_button.config(text="Resume" if self.paused else "Pause")
        if not self.paused:  # if resuming, call run_script to process the next line
            self.run_script()

    def update_text(self, speaker, line):
        self.label.config(text=f"{speaker}: {line}", fg=self.colors.get(speaker, 'black'))  # Default color is black
        self.update()

    def run_script(self):
        if not self.paused and self.current_index < len(self.dialogue):
            speaker, line = self.dialogue[self.current_index]
            self.update_text(speaker, line)
            self.current_index += 1
            interval = min_visible_time + extra_time_per_prompt
            self.after(int(interval * 1000), self.run_script)
        elif self.current_index >= len(self.dialogue):
            self.end_script()

    def update_time_left(self):
        minutes_left = int(self.remaining_time // 60)
        seconds_left = int(self.remaining_time % 60)
        self.time_left_label.config(text=f"Time left: {minutes_left}m {seconds_left}s")

    def update_timer(self):
        if not self.paused:
            self.remaining_time -= 1
            self.update_time_left()
        if self.remaining_time > 0:
            self.after(1000, self.update_timer)
        else:
            self.end_script()

    def end_script(self):
        self.destroy()
        show_end_page()

    def exit_to_start(self, event=None):
        self.destroy()
        start_page(previous_input=self.previous_input)

# Function to get the dialogue from the user
def get_dialogue_from_text(dialogue_str):
    dialogue = []
    lines = dialogue_str.strip().split('\n')
    for line in lines:
        parts = line.split(':', 1)
        if len(parts) == 2:
            speaker, text = parts
            dialogue.append([speaker.strip(), text.strip()])
    return dialogue

# Setup Tkinter start page
class StartPage(tk.Tk):
    def __init__(self, previous_input=""):
        super().__init__()
        self.title("Start Page")
        self.configure(bg="#f0f0f0")

        self.label = tk.Label(self, text="Choose an option to get started", font=("Helvetica", 16), bg="#f0f0f0")
        self.label.pack(pady=20)

        self.create_script_button = tk.Button(self, text="Create Script", command=self.create_script, bg="#f0f0f0", font=("Helvetica", 12))
        self.create_script_button.pack(pady=10)

        self.load_script_button = tk.Button(self, text="Load Script", command=self.load_script, bg="#f0f0f0", font=("Helvetica", 12))
        self.load_script_button.pack(pady=10)

    def create_script(self):
        self.destroy()
        create_script_page(previous_input="")

    def load_script(self):
        self.destroy()
        LoadScriptPage()

# Create Script Page
class CreateScriptPage(tk.Tk):
    def __init__(self, previous_input=""):
        super().__init__()
        self.title("Create Script")
        self.configure(bg="#f0f0f0")

        self.label = tk.Label(self, text="Enter the dialogue for the teleprompter\n(Speaker: Dialogue)", font=("Helvetica", 16), bg="#f0f0f0")
        self.label.pack(pady=20)

        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=70, height=15, font=("Helvetica", 12))
        self.text_area.pack(pady=20)

        # Placeholder dialogue for easier testing
        placeholder_dialogue = """Speaker 1: Hello, welcome to the teleprompter app.
Speaker 2: Thank you! I'm excited to test this out.
Speaker 1: It's easy to use. Just enter your dialogue and the total time for your video.
Speaker 2: Sounds great! How do I start?
Speaker 1: Once you enter the details, just hit Start and the script will begin.
Speaker 2: Perfect. Let's get started!"""
        self.text_area.insert("1.0", previous_input or placeholder_dialogue)

        self.duration_label = tk.Label(self, text="Enter total duration of the video in minutes:", font=("Helvetica", 12), bg="#f0f0f0")
        self.duration_label.pack(pady=5)

        self.duration_entry = tk.Entry(self, font=("Helvetica", 12))
        self.duration_entry.pack(pady=5)

        self.text_area.bind("<Control-Return>", self.ctrl_enter_submit)  # Bind Ctrl+Enter to start

        self.button_frame = tk.Frame(self, bg="#f0f0f0")
        self.button_frame.pack(pady=10)

        self.submit_button = tk.Button(self.button_frame, text="Start", command=self.start_teleprompter, bg="#f0f0f0", font=("Helvetica", 12))
        self.submit_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(self.button_frame, text="Save Dialogue", command=self.save_dialogue, bg="#f0f0f0", font=("Helvetica", 12))
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.update_geometry()

    def start_teleprompter(self):
        dialogue_str = self.text_area.get("1.0", tk.END)
        dialogue = get_dialogue_from_text(dialogue_str)
        try:
            total_time = float(self.duration_entry.get())
            if dialogue and total_time > 0:
                self.destroy()
                app = Teleprompter(dialogue, total_time, previous_input=dialogue_str.strip())
                app.mainloop()
            else:
                self.label.config(
                    text="Invalid dialogue format or duration. Please ensure each line is 'Speaker: Dialogue' and duration is correct."
                )
        except ValueError:
            self.label.config(text="Invalid duration. Please enter a numeric value for the duration.")

    def ctrl_enter_submit(self, event):
        self.start_teleprompter()
        return "break"  # Prevent default behavior

    def update_geometry(self):
        self.update_idletasks()
        self.geometry(f"{self.winfo_width()}x{self.winfo_height() + 30}")
        self.after(100, self.update_geometry)  # Continuously update the size of the window

    def save_dialogue(self):
        dialogue_str = self.text_area.get("1.0", tk.END).strip()
        if not dialogue_str:
            messagebox.showwarning("Warning", "Dialogue is empty. Nothing to save.")
            return

        title = simpledialog.askstring("Input", "Please enter a title for your script")
        if title:
            file_path = f"{title}.txt"
            with open(file_path, 'w') as file:
                file.write(dialogue_str)
            messagebox.showinfo("Success", "Dialogue saved successfully.")

# Load Script Page
class LoadScriptPage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Load Script")
        self.configure(bg="#f0f0f0")

        self.label = tk.Label(self, text="Select a script to load", font=("Helvetica", 16), bg="#f0f0f0")
        self.label.pack(pady=20)

        self.script_listbox = tk.Listbox(self, font=("Helvetica", 12), width=50)
        self.script_listbox.pack(pady=20)

        self.load_button = tk.Button(self, text="Load", command=self.load_selected_script, bg="#f0f0f0", font=("Helvetica", 12))
        self.load_button.pack(pady=10)

        self.update_script_list()

    def update_script_list(self):
        self.script_listbox.delete(0, tk.END)
        script_directory = os.getcwd()
        scripts = [f for f in os.listdir(script_directory) if f.endswith('.txt')]
        for script in scripts:
            self.script_listbox.insert(tk.END, script)

    def load_selected_script(self):
        selected_script = self.script_listbox.get(tk.ACTIVE)
        if selected_script:
            file_path = os.path.join(os.getcwd(), selected_script)
            with open(file_path, 'r') as file:
                dialogue_str = file.read()
            self.destroy()
            create_script_page(previous_input=dialogue_str)

# End Page to show when the script ends
class EndPage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("End of Script")
        self.configure(bg="#f0f0f0")

        self.label = tk.Label(self, text="End", font=("Helvetica", 24), bg="#f0f0f0")
        self.label.pack(pady=50)

        self.bind("<Escape>", self.exit_to_start)  # Bind Escape to exit to start page

    def exit_to_start(self, event=None):
        self.destroy()
        start_page()

# Function to show the EndPage
def show_end_page():
    end_page = EndPage()
    end_page.mainloop()

# Function to run the start page
def start_page(previous_input=""):
    page = StartPage(previous_input=previous_input)
    page.mainloop()

def create_script_page(previous_input=""):
    page = CreateScriptPage(previous_input=previous_input)
    page.mainloop()

# Run the start page
if __name__ == "__main__":
    start_page()