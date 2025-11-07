from flask import Flask, render_template, request, jsonify
import os
import numpy as np
from solver import SudokuSolver
from recognizer import SudokuRecognizer
from generator import SudokuGenerator

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize components
solver = SudokuSolver()
generator = SudokuGenerator()
recognizer = SudokuRecognizer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/solve', methods=['POST'])
def solve_sudoku():
    try:
        data = request.get_json()
        grid = data.get('grid')
        
        if not grid or len(grid) != 9 or any(len(row) != 9 for row in grid):
            return jsonify({'error': 'Invalid grid format'}), 400
        
        # Convert to numpy array and solve
        sudoku_grid = np.array(grid, dtype=int)
        solution = solver.solve(sudoku_grid.copy())
        
        if solution is not None:
            return jsonify({'solution': solution.tolist()})
        else:
            return jsonify({'error': 'No solution exists'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# @app.route('/upload', methods=['POST'])
# def upload_image():
#     # Instead of processing, just return a "coming soon" message
#     return jsonify({'message': '🟢 Feature will be available soon!'}), 200

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        # Save uploaded file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # Recognize sudoku from image
        grid = recognizer.recognize_sudoku(filepath)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        if grid is not None:
            return jsonify({'grid': grid.tolist()})
        else:
            return jsonify({'error': 'Could not recognize Sudoku grid from image'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate_puzzle():
    try:
        data = request.get_json()
        difficulty = data.get('difficulty', 'medium')
        
        puzzle = generator.generate(difficulty)
        return jsonify({'puzzle': puzzle.tolist()})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render provides PORT env variable
    app.run(host="0.0.0.0", port=port)




