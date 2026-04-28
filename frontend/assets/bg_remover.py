from rembg import remove
from PIL import Image
import os

files = ["YemekTercihleri.jpg","HesapAyarlari.jpg"]

for file in files:
    input_path = f"frontend/assets/{file}"
    output_path = f"frontend/assets/{file.replace('.jpg', '.png')}"
    
    if os.path.exists(input_path):
        input_img = Image.open(input_path).convert("RGBA") # RGBA'ya çevirerek aç
        output_img = remove(input_img)
        output_img.save(output_path, "PNG") # Kaydederken formatı zorla
        print(f"✅ Başarılı: {output_path}")
    else:
        print(f"❌ Dosya bulunamadı: {os.path.abspath(input_path)}") # Tam yolu yazdır ki hata neredeyse gör