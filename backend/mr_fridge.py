import cv2
import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import base64
from openai import OpenAI

# Load the secret key from the .env file into the environment
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client with the secure key
client = OpenAI(api_key=API_KEY)


class MrFridgeApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        # Start the camera
        self.vid = cv2.VideoCapture(0)

        # UI elements
        self.canvas = tk.Canvas(
            window,
            width=self.vid.get(cv2.CAP_PROP_FRAME_WIDTH),
            height=self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT),
        )
        self.canvas.pack()

        self.result_label = tk.Label(
            window,
            text="Show an item to the camera and press 'SCAN'.",
            font=("Arial", 14),
            fg="blue",
        )
        self.result_label.pack(pady=10)

        self.btn_scan = tk.Button(
            window,
            text="SCAN",
            width=20,
            height=2,
            command=self.scan,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
        )
        self.btn_scan.pack(pady=10)

        self.delay = 15
        self.update_camera()

        self.window.mainloop()

    def update_camera(self):
        ret, frame = self.vid.read()
        if ret:
            cv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv_img))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.window.after(self.delay, self.update_camera)

    def scan(self):
        ret, frame = self.vid.read()
        if ret:
            self.result_label.config(
                text="Mr.Fridge is analyzing, please wait...", fg="orange"
            )
            self.window.update()

            # Encode the image in JPG format in memory
            success, encoded_image = cv2.imencode(".jpg", frame)

            if success:
                # Convert to base64 format
                base64_image = base64.b64encode(encoded_image).decode("utf-8")

                try:
                    # Send the base64 image and prompt to the OpenAI API (GPT-4o)
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "What is the item I am holding or focusing on in this image? Answer with only a single word or a very short name (e.g.: Milk, Half Apple, Ketchup Bottle) in English.",
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{base64_image}"
                                        },
                                    },
                                ],
                            }
                        ],
                        max_tokens=50,  # Low token limit since we only need a short answer
                    )

                    # Retrieve the response and display it
                    result_text = response.choices[0].message.content.strip()
                    self.result_label.config(
                        text=f"Detected: {result_text}", fg="green"
                    )

                except Exception as e:
                    self.result_label.config(text="API Connection Error!", fg="red")
                    messagebox.showerror(
                        "Error Details",
                        f"OpenAI API Error:\n{str(e)}\n\nPlease check your API key and account balance.",
                    )

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()


if __name__ == "__main__":
    root = tk.Tk()
    app = MrFridgeApp(root, "Mr.Fridge - Smart Item Recognition")
