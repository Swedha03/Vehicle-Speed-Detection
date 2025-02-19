
### **Vehicle Speed Detection Using Computer Vision**  

🚗 A computer vision-based system for estimating vehicle speed from recorded video footage using **Haar Cascade** for vehicle detection and **Lucas-Kanade Optical Flow** for speed estimation.  

---

## **🔹 Features**  
✅ Upload recorded video footage for analysis  
✅ Detect vehicles using Haar Cascade  
✅ Track vehicle motion using Lucas-Kanade Optical Flow  
✅ Estimate vehicle speed based on pixel displacement  
✅ Output processed video with speed annotations  

---

## **🔹 Technologies Used**  
- **Python**  
- **OpenCV**  
- **NumPy**  
- **FFmpeg** (for video conversion)  
- **Haar Cascade** (vehicle detection)  
- **Lucas-Kanade Optical Flow** (speed estimation)  
- **Flask / Django (if applicable)**  

---

## **🔹 Installation**  

1️⃣ **Clone the repository**  
```bash
git clone https://github.com/Swedha03/Vehicle-Speed-Detection.git
cd Vehicle-Speed-Detection
```

2️⃣ **Create a virtual environment (optional but recommended)**  
```bash
python -m venv venv
source venv/bin/activate  # For Mac/Linux
venv\Scripts\activate      # For Windows
```

3️⃣ **Install dependencies**  
```bash
pip install -r requirements.txt
```

---

## **🔹 Usage**  

1️⃣ **Run the program**  
```bash
python manage.py --video path/to/video.mp4
```

2️⃣ **Optional Parameters**  
- `--output path/to/output.mp4` → Save processed video  
- `--debug` → Enable debug mode for additional logs  

3️⃣ **View Results**  
- Processed video with **speed annotations** is saved in the output folder.  

--



