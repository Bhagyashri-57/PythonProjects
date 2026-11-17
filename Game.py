
import tkinter as tk
from enum import Enum


# Only one FSM state
class TrafficState(Enum):
    GREEN = 1


class TrafficLightFSM:

    def __init__(self, root):
        self.root = root
        self.root.title("Traffic Light FSM")
        self.root.geometry("450x550")
        self.root.configure(bg="white")

        self.state = TrafficState.GREEN
        self.running = False
        self.count = 0

        # Title
        self.title = tk.Label(
            root,
            text="TRAFFIC LIGHT FSM",
            font=("Arial", 20, "bold"),
            bg="white"
        )
        self.title.pack(pady=10)

        # Traffic light canvas
        self.canvas = tk.Canvas(
            root,
            width=180,
            height=300,
            bg="white",
            highlightthickness=0
        )
        self.canvas.pack(pady=10)

        # Traffic light box
        self.canvas.create_rectangle(
            40, 10, 140, 290,
            fill="black"
        )

        # Traffic light circles
        self.red_light = self.canvas.create_oval(
            65, 30, 115, 80,
            fill="gray"
        )

        self.yellow_light = self.canvas.create_oval(
            65, 115, 115, 165,
            fill="gray"
        )

        self.green_light = self.canvas.create_oval(
            65, 200, 115, 250,
            fill="green"
        )

        # Status message
        self.status_label = tk.Label(
            root,
            text="Vehicles allowed to move",
            font=("Arial", 13, "bold"),
            fg="green",
            bg="white"
        )
        self.status_label.pack(pady=10)

        # Action counter
        self.count_label = tk.Label(
            root,
            text="Action Count: 0",
            font=("Arial", 12),
            bg="white"
        )
        self.count_label.pack(pady=5)

        # Buttons
        self.start_button = tk.Button(
            root,
            text="START FSM",
            font=("Arial", 12, "bold"),
            bg="green",
            fg="white",
            command=self.start
        )
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(
            root,
            text="STOP FSM",
            font=("Arial", 12, "bold"),
            bg="red",
            fg="white",
            command=self.stop
        )
        self.stop_button.pack(pady=5)

        self.red_button = tk.Button(
            root,
            text="RED - STOP",
            font=("Arial", 12, "bold"),
            bg="darkred",
            fg="white",
            command=self.red_instruction
        )
        self.red_button.pack(pady=5)

    # Perform only one action
    def perform_action(self):
        if self.state == TrafficState.GREEN:
            self.count += 1

            self.status_label.config(
                text="Vehicles allowed to move",
                fg="green"
            )

            self.count_label.config(
                text=f"Action Count: {self.count}"
            )

            print("Vehicles allowed to move")

    # Repeat the action every 2 seconds
    def run(self):
        if self.running:
            self.perform_action()
            self.root.after(2000, self.run)

    # Start FSM
    def start(self):
        if not self.running:
            self.running = True

            self.canvas.itemconfig(
                self.red_light, fill="gray"
            )
            self.canvas.itemconfig(
                self.yellow_light, fill="gray"
            )
            self.canvas.itemconfig(
                self.green_light, fill="green"
            )

            self.status_label.config(
                text="Vehicles allowed to move",
                fg="green"
            )

            print("FSM Started")
            self.run()

    # Stop FSM and display stop instruction
    def stop(self):
        self.running = False

        self.canvas.itemconfig(
            self.red_light, fill="red"
        )
        self.canvas.itemconfig(
            self.yellow_light, fill="gray"
        )
        self.canvas.itemconfig(
            self.green_light, fill="gray"
        )

        self.status_label.config(
            text="STOP THE VEHICLE!",
            fg="red"
        )

        print("STOP THE VEHICLE!")

    # Red button action
    def red_instruction(self):
        self.stop()


# Main program
root = tk.Tk()
app = TrafficLightFSM(root)
root.mainloop()
