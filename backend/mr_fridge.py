import cv2
import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import base64
from openai import OpenAI

# .env dosyasındaki gizli anahtarı sisteme yükle
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI istemcisini güvenli anahtar ile başlat
client = OpenAI(api_key=API_KEY)


class MrFridgeApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        # Kamerayı başlat
        self.vid = cv2.VideoCapture(0)

        # Arayüz elemanları
        self.canvas = tk.Canvas(
            window,
            width=self.vid.get(cv2.CAP_PROP_FRAME_WIDTH),
            height=self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT),
        )
        self.canvas.pack()

        self.sonuc_label = tk.Label(
            window,
            text="Kameraya bir eşya gösterin ve 'Tara'ya basın.",
            font=("Arial", 14),
            fg="blue",
        )
        self.sonuc_label.pack(pady=10)

        self.btn_tara = tk.Button(
            window,
            text="TARA",
            width=20,
            height=2,
            command=self.tara,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
        )
        self.btn_tara.pack(pady=10)

        self.delay = 15
        self.update_kamera()

        self.window.mainloop()

    def update_kamera(self):
        ret, frame = self.vid.read()
        if ret:
            cv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv_img))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.window.after(self.delay, self.update_kamera)

    def tara(self):
        ret, frame = self.vid.read()
        if ret:
            self.sonuc_label.config(
                text="Mr.Fridge inceliyor, lütfen bekleyin...", fg="orange"
            )
            self.window.update()

            # Görüntüyü JPG formatında belleğe al
            success, encoded_image = cv2.imencode(".jpg", frame)

            if success:
                # Base64 formatına çevir
                base64_image = base64.b64encode(encoded_image).decode("utf-8")

                try:
                    # OpenAI API'ye (GPT-4o) Base64 görüntüyü ve promptu gönder
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Bu resimde elimde tuttuğum veya odaklanılan eşya nedir? Sadece tek bir kelime veya çok kısa bir isimle (örneğin: Süt, Yarım Elma, Ketçap Şişesi) Türkçe olarak cevap ver.",
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
                        max_tokens=50,  # Sadece kısa bir cevap istediğimiz için token sınırını düşük tutuyoruz
                    )

                    # Gelen cevabı al ve ekrana yaz
                    sonuc_metni = response.choices[0].message.content.strip()
                    self.sonuc_label.config(
                        text=f"Tespit Edildi: {sonuc_metni}", fg="green"
                    )

                except Exception as e:
                    self.sonuc_label.config(text="API Bağlantı Hatası!", fg="red")
                    messagebox.showerror(
                        "Hata Detayı",
                        f"OpenAI API Hatası:\n{str(e)}\n\nLütfen API anahtarınızı ve bakiyenizi kontrol edin.",
                    )

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()


if __name__ == "__main__":
    root = tk.Tk()
    app = MrFridgeApp(root, "Mr.Fridge - Akıllı Nesne Tanıma")
