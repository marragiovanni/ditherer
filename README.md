# Ditherer

Simple and intuitive python software for applying dithering algorithms on images

## 📌 Features
✅ Open and save images in PNG, JPG, JPEG, GIF, BMP  
✅ Three dithering algorithms: Floyd-Steinberg, Random, Bayer  
✅ Adjustable parameters for custom dithering intensity  
✅ Undo/Redo support for easy editing  
✅ User-friendly GUI with a toolbar  

## 🛠️ Installation
Requires **Python 3.8+.**  
```bash
git clone https://github.com/marragiovanni/ditherer.git
cd ditherer
pip install -r requirements.txt
python main.py
```

## ⚙️ How to Use
- Open an image with Open button
- Select a dithering algorithm & adjust parameters  
- Click Apply to process the image  
- Use Undo/Redo if needed or Default to restore the original image 
- Save the image with Save button

## 🧪 Supported Algorithms
🎛️ **Floyd-Steinberg – Realistic error diffusion**  
  
*Floyd-Steinberg with dithering intensity of 10*
![fs](https://github.com/user-attachments/assets/6392b823-fc8b-4ed6-97ed-35748a0f640d)

🎲 **Random Dithering – Adds artistic noise**  
  
*Random with dithering intensity of 5*
![random5](https://github.com/user-attachments/assets/0d1f5228-c5c6-4993-9ea7-5f4deaeff852)

📊 **Bayer Dithering – Pattern-based dithering**  
  
*4x4 Bayer dithering, quantization threshold of 255*
![bayer4x4](https://github.com/user-attachments/assets/1029a5a7-f342-4f28-9808-1696bf8bae46)


## License
This project is released under the MIT License.
