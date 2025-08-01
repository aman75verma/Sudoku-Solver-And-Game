# 🧠 Sudoku Solver Web App

A web-based application to **generate**, **manually input**, and **solve Sudoku puzzles** using a backtracking algorithm and a Flask-based backend. Currently, **image upload and OCR-based grid recognition features are under development**.

## 🚀 Features

- ✅ Generate valid Sudoku puzzles (`easy`, `medium`, `hard`)  
- ✅ Solve any valid Sudoku grid using a backtracking algorithm  
- ✅ Clean and modular backend using Flask  
- 🚧 Image upload and auto-recognition (OCR) are **currently in development**

## 🛠️ Tech Stack

- **Backend:** Python, Flask  
- **Sudoku Logic:** Numpy-based grid manipulation, AI solver & generator  
- **Frontend:** HTML/CSS/JavaScript

## 📁 Project Structure

```
├── app.py                 # Flask main application
├── solver.py              # Sudoku solver using backtracking
├── generator.py           # Sudoku puzzle generator with difficulty levels
├── templates/             # HTML templates (e.g., index.html)
├── static/
│   ├── styles/            # CSS files
│   └── scripts/           # JavaScript files
├── uploads/               # Temporary upload folder (for future use)
├── requirements.txt       # Python dependencies
└── README.md              # You're here
```

## 🧩 Setup Instructions

### 1. 🔧 Install System Dependencies

Ensure you have **Python 3.7+** installed.

### 2. 🐍 Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. 📦 Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. ▶️ Run the App

```bash
python app.py
```

Then visit: [http://127.0.0.1:5000](http://127.0.0.1:5000)


## 💡 Future Improvements

- Add support for mobile camera capture  
- Integrate OCR for digit recognition using deep learning or Tesseract (in progress)  
- Track solving steps visually  

## 📄 License

This project is open-source and available under the [MIT License](https://opensource.org/licenses/MIT).

---

Made with 🧠, 🐍, and ❤️ for Sudoku enthusiasts!
