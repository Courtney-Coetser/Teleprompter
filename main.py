import tkinter as tk
from tkinter import scrolledtext

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

        self.colors = {"Mona": "red", "Chrissy": "blue"}
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
            self.update_text("End of Script", "")
            self.after(10000, self.destroy)  # Show "End of Script" for 10 seconds
    
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
            self.update_text("End of Script", "")
            self.after(10000, self.destroy)  # Show "End of Script" for 10 seconds

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

        self.label = tk.Label(self, text="Enter the dialogue for the teleprompter\n(Speaker: Dialogue)", font=("Helvetica", 16), bg="#f0f0f0")
        self.label.pack(pady=20)

        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=70, height=15, font=("Helvetica", 12))
        self.text_area.pack(pady=20)
        self.text_area.insert("1.0", previous_input)  # Insert the previous input

        self.duration_label = tk.Label(self, text="Enter total duration of the video in minutes:", font=("Helvetica", 12), bg="#f0f0f0")
        self.duration_label.pack(pady=5)
        
        self.duration_entry = tk.Entry(self, font=("Helvetica", 12))
        self.duration_entry.pack(pady=5)

        self.text_area.bind("<Control-Return>", self.ctrl_enter_submit)  # Bind Ctrl+Enter to submit

        self.submit_button = tk.Button(self, text="Submit", command=self.start_teleprompter, bg="#f0f0f0", font=("Helvetica", 12))
        self.submit_button.pack(pady=20)

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
                self.label.config(text="Invalid dialogue format or duration. Please ensure each line is 'Speaker: Dialogue' and duration is correct.")
        except ValueError:
            self.label.config(text="Invalid duration. Please enter a numeric value for the duration.")

    def ctrl_enter_submit(self, event):
        self.start_teleprompter()
        return "break"  # Prevent default behavior

    def update_geometry(self):
        self.update_idletasks()
        self.geometry(f"{self.winfo_width()}x{self.winfo_height() + 30}")
        self.after(100, self.update_geometry)  # Continuously update the size of the window

# Function to run the start page
def start_page(previous_input=""):
    page = StartPage(previous_input=previous_input)
    page.mainloop()

# Run the start page
if __name__ == "__main__":
    start_page()