# 🧠 Sudoku Solver Web App

A web-based application to **recognize**, **generate**, and **solve Sudoku puzzles** using image processing (OCR), Backtracking algorithms, and Flask for the backend API. Users can upload an image of a Sudoku puzzle, generate new puzzles of varying difficulty, or solve manually entered ones.

---

## 🚀 Features

- ✅ Upload a Sudoku image and auto-recognize the grid using OpenCV and Tesseract OCR  
- ✅ Generate valid Sudoku puzzles (`easy`, `medium`, `hard`)  
- ✅ Solve any valid Sudoku grid using a backtracking algorithm  
- ✅ Clean and modular backend using Flask

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask  
- **Image Processing:** OpenCV, Pytesseract, PIL (Pillow)  
- **Sudoku Logic:** Numpy-based grid manipulation, AI solver & generator  
- **Frontend:** HTML/CSS/JavaScript

---

## 📁 Project Structure

```
├── app.py                 # Flask main application
├── recognizer.py          # Handles OCR and Sudoku grid recognition from images
├── solver.py              # Sudoku solver using backtracking
├── generator.py           # Sudoku puzzle generator with difficulty levels
├── templates/             # HTML templates (e.g., index.html)
├── static/
│   ├── styles/            # CSS files
│   └── scripts/           # JavaScript files
├── uploads/               # Temporary upload folder (auto-created)
├── requirements.txt       # Python dependencies
└── README.md              # You're here
```

---

## 🧩 Setup Instructions

### 1. 🔧 Install System Dependencies

Ensure you have **Python 3.7+** installed.

You also need **Tesseract-OCR** installed on your system:

#### Windows:
- Download from: https://github.com/tesseract-ocr/tesseract
- After installation, optionally configure the path in `recognizer.py`:
```python
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

#### Linux (Ubuntu):
```bash
sudo apt update
sudo apt install tesseract-ocr
```

---

### 2. 🐍 Create Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

---

### 3. 📦 Install Python Dependencies
```bash
pip install -r requirements.txt
```

---

### 4. ▶️ Run the App
```bash
python app.py
```

Then visit: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---


## ✅ Dependencies (`requirements.txt`)

```
Flask
numpy
opencv-python
pytesseract
Pillow
```

---

## 💡 Future Improvements

- Add support for mobile camera capture  
- Improve OCR digit recognition with CNN  
- Track solving steps visually

---

## 📄 License

This project is open-source and available under the [MIT License](https://opensource.org/licenses/MIT).

---

Made with 🧠, 🐍, and ❤️ for Sudoku enthusiasts!
