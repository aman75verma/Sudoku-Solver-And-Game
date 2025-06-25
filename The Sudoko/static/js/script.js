let currentGrid = Array(9).fill().map(() => Array(9).fill(0));
let originalGrid = Array(9).fill().map(() => Array(9).fill(0));
let startTime = null;
let timerInterval = null;
let errorCount = 0;
let hintCount = 0;

// Initialize grid
function initializeGrid() {
    const grid = document.getElementById('sudokuGrid');
    grid.innerHTML = '';
    
    for (let i = 0; i < 81; i++) {
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'sudoku-cell';
        input.maxLength = 1;
        
        input.oninput = function(e) {
            const value = e.target.value;
            if (!/^[1-9]$/.test(value)) {
                e.target.value = '';
            }
            updateGrid();
            updateStats();
        };
        
        input.onkeydown = function(e) {
            if (e.key === 'Backspace' || e.key === 'Delete') {
                e.target.value = '';
                updateGrid();
                updateStats();
            }
            if (e.key >= '1' && e.key <= '9') {
                e.target.value = e.key;
                updateGrid();
                updateStats();
                e.preventDefault();
            }
        }
        input.onfocus = function() {
            if (!startTime) {
                startTimer();
            }
        };
        
        grid.appendChild(input);
    }
    updateStats();
}

function updateGrid() {
    const inputs = document.querySelectorAll('.sudoku-cell');
    for (let i = 0; i < 81; i++) {
        const row = Math.floor(i / 9);
        const col = i % 9;
        const value = inputs[i].value;
        currentGrid[row][col] = value ? parseInt(value) : 0;
    }
}

function displayGrid(grid, markSolved = false) {
    const inputs = document.querySelectorAll('.sudoku-cell');
    for (let i = 0; i < 81; i++) {
        const row = Math.floor(i / 9);
        const col = i % 9;
        const value = grid[row][col];
        
        inputs[i].value = value || '';
        inputs[i].className = 'sudoku-cell';
        
        if (value && originalGrid[row][col] === 0 && markSolved) {
            inputs[i].className += ' solved';
            inputs[i].readOnly = true;
        } else if (value && originalGrid[row][col] !== 0) {
            inputs[i].className += ' given';
            inputs[i].readOnly = true;
        } else {
            inputs[i].readOnly = false;
        }
    }
    currentGrid = grid.map(row => [...row]);
    updateStats();
}

function showMessage(text, type = 'success', icon = '') {
    const messageDiv = document.getElementById('message');
    const iconHtml = icon ? `<i class="${icon}"></i>` : '';
    messageDiv.innerHTML = `<div class="message ${type}">${iconHtml}${text}</div>`;
    setTimeout(() => messageDiv.innerHTML = '', 5000);
}

function showLoading(show, progress = 0) {
    document.getElementById('loading').style.display = show ? 'block' : 'none';
    if (show) {
        document.getElementById('progressFill').style.width = progress + '%';
    }
}

function updateStats() {
    const filledCells = currentGrid.flat().filter(cell => cell !== 0).length;
    const completion = Math.round((filledCells / 81) * 100);
    
    document.getElementById('filledCells').textContent = `${filledCells}/81`;
    document.getElementById('completion').textContent = `${completion}%`;
    document.getElementById('errors').textContent = errorCount;
    document.getElementById('hints').textContent = hintCount;
}

function startTimer() {
    startTime = Date.now();
    timerInterval = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const minutes = Math.floor(elapsed / 60000);
        const seconds = Math.floor((elapsed % 60000) / 1000);
        document.getElementById('timeElapsed').textContent = 
            `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }, 1000);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

async function solvePuzzle() {
    updateGrid();
    
    if (currentGrid.every(row => row.every(cell => cell === 0))) {
        showMessage('Please enter some numbers first!', 'error', 'fas fa-exclamation-circle');
        return;
    }
    
    showLoading(true, 0);
    
    // Simulate progress
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        showLoading(true, progress);
    }, 100);
    
    try {
        const response = await fetch('/solve', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ grid: currentGrid })
        });
        
        const data = await response.json();
        clearInterval(progressInterval);
        
        if (response.ok) {
            showLoading(true, 100);
            setTimeout(() => {
                displayGrid(data.solution, true);
                showMessage('🎉 Puzzle solved successfully!', 'success', 'fas fa-trophy');
                stopTimer();
                showLoading(false);
            }, 500);
        } else {
            showMessage(data.error || 'Failed to solve puzzle', 'error', 'fas fa-times-circle');
            showLoading(false);
        }
    } catch (error) {
        clearInterval(progressInterval);
        showMessage('Error solving puzzle: ' + error.message, 'error', 'fas fa-exclamation-triangle');
        showLoading(false);
    }
}

function validatePuzzle() {
    updateGrid();
    let hasConflicts = false;

    // Check rows and columns
    for (let i = 0; i < 9; i++) {
        let rowSet = new Set();
        let colSet = new Set();
        for (let j = 0; j < 9; j++) {
            // Check row
            let rowVal = currentGrid[i][j];
            if (rowVal !== 0) {
                if (rowSet.has(rowVal)) hasConflicts = true;
                rowSet.add(rowVal);
            }
            // Check column
            let colVal = currentGrid[j][i];
            if (colVal !== 0) {
                if (colSet.has(colVal)) hasConflicts = true;
                colSet.add(colVal);
            }
        }
    }

    // Check 3x3 boxes
    for (let boxRow = 0; boxRow < 3; boxRow++) {
        for (let boxCol = 0; boxCol < 3; boxCol++) {
            let boxSet = new Set();
            for (let i = 0; i < 3; i++) {
                for (let j = 0; j < 3; j++) {
                    let val = currentGrid[boxRow * 3 + i][boxCol * 3 + j];
                    if (val !== 0) {
                        if (boxSet.has(val)) hasConflicts = true;
                        boxSet.add(val);
                    }
                }
            }
        }
    }

    if (hasConflicts) {
        errorCount++;
        showMessage('Conflicts detected in current grid!', 'error', 'fas fa-exclamation-triangle');
    } else {
        showMessage('Grid looks valid so far!', 'success', 'fas fa-check-circle');
    }
    updateStats();
}

function clearGrid() {
    currentGrid = Array(9).fill().map(() => Array(9).fill(0));
    originalGrid = Array(9).fill().map(() => Array(9).fill(0));
    displayGrid(currentGrid);
    document.getElementById('message').innerHTML = '';
    stopTimer();
    startTime = null;
    errorCount = 0;
    hintCount = 0;
    document.getElementById('timeElapsed').textContent = '00:00';
    updateStats();
    showMessage('Grid cleared successfully!', 'info', 'fas fa-info-circle');
}

async function generatePuzzle() {
    const difficulty = document.getElementById('difficulty').value;
    showLoading(true, 0);
    
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 20;
        if (progress > 85) progress = 85;
        showLoading(true, progress);
    }, 150);
    
    
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ difficulty: difficulty })
        });
        
        const data = await response.json();
        clearInterval(progressInterval);
        
        if (response.ok) {
            showLoading(true, 100);
            setTimeout(() => {
                originalGrid = data.puzzle.map(row => [...row]);
                displayGrid(data.puzzle);
                showMessage(`🎲 ${difficulty.charAt(0).toUpperCase() + difficulty.slice(1)} puzzle generated!`, 'success', 'fas fa-dice');
                stopTimer(); 
                startTime = null;
                errorCount = 0;
                hintCount = 0;
                document.getElementById('timeElapsed').textContent = '00:00';
                updateStats();

                showLoading(false);
            }, 500);
        } else {
            showMessage(data.error || 'Failed to generate puzzle', 'error', 'fas fa-times-circle');
            showLoading(false);
        }
    } catch (error) {
        clearInterval(progressInterval);
        showMessage('Error generating puzzle: ' + error.message, 'error', 'fas fa-exclamation-triangle');
        showLoading(false);
    }
}

async function uploadImage() {
    const fileInput = document.getElementById('imageUpload');
    const file = fileInput.files[0];
    
    if (!file) return;
    
    showLoading(true, 0);
    showMessage('📸 Analyzing image with AI...', 'info', 'fas fa-camera');
    
    const formData = new FormData();
    formData.append('image', file);
    
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 10;
        if (progress > 80) progress = 80;
        showLoading(true, progress);
    }, 200);
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        clearInterval(progressInterval);
        
        if (response.ok) {
            showLoading(true, 100);
            setTimeout(() => {
                originalGrid = data.grid.map(row => [...row]);
                displayGrid(data.grid);
                showMessage('✨ Sudoku recognized from image!', 'success', 'fas fa-magic');
                startTime = null;
                errorCount = 0;
                hintCount = 0;
                document.getElementById('timeElapsed').textContent = '00:00';
                showLoading(false);
            }, 500);
        } else {
            showMessage(data.error || 'Failed to recognize Sudoku from image', 'error', 'fas fa-times-circle');
            showLoading(false);
        }
    } catch (error) {
        clearInterval(progressInterval);
        showMessage('Error processing image: ' + error.message, 'error', 'fas fa-exclamation-triangle');
        showLoading(false);
    } finally {
        fileInput.value = '';
    }
}

// Drag and drop functionality
const uploadArea = document.querySelector('.upload-area');

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', (e) => {
    if (!uploadArea.contains(e.relatedTarget)) {
        uploadArea.classList.remove('dragover');
    }
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].type.startsWith('image/')) {
        document.getElementById('imageUpload').files = files;
        uploadImage();
    } else {
        showMessage('Please drop a valid image file', 'error', 'fas fa-exclamation-triangle');
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey || e.metaKey) {
        switch(e.key) {
            case 's':
                e.preventDefault();
                solvePuzzle();
                break;
            case 'r':
                e.preventDefault();
                clearGrid();
                break;
            case 'g':
                e.preventDefault();
                generatePuzzle();
                break;
            case 'v':
                e.preventDefault();
                validatePuzzle();
                break;
        }
    }
});

// Add hint functionality
function getHint() {
    updateGrid();
    
    // Find empty cells
    const emptyCells = [];
    for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
            if (currentGrid[i][j] === 0) {
                emptyCells.push([i, j]);
            }
        }
    }
    
    if (emptyCells.length === 0) {
        showMessage('Puzzle is already complete!', 'info', 'fas fa-check-circle');
        return;
    }
    
    // For demo purposes, just highlight a random empty cell
    const randomCell = emptyCells[Math.floor(Math.random() * emptyCells.length)];
    const cellIndex = randomCell[0] * 9 + randomCell[1];
    const inputs = document.querySelectorAll('.sudoku-cell');
    
    inputs[cellIndex].focus();
    inputs[cellIndex].style.background = '#fef3c7';
    setTimeout(() => {
        inputs[cellIndex].style.background = '';
    }, 2000);
    
    hintCount++;
    updateStats();
    showMessage('💡 Try focusing on this cell!', 'info', 'fas fa-lightbulb');
}

// Add hint button to controls
function addHintButton() {
    const btnGroup = document.querySelector('.btn-group');
    const hintBtn = document.createElement('button');
    hintBtn.className = 'btn btn-outline';
    hintBtn.onclick = getHint;
    hintBtn.innerHTML = '<i class="fas fa-lightbulb"></i> Get Hint';
    btnGroup.appendChild(hintBtn);
}

// Auto-save functionality (using memory since localStorage is not available)
let autoSaveData = null;

function autoSave() {
    updateGrid();
    autoSaveData = {
        grid: currentGrid.map(row => [...row]),
        originalGrid: originalGrid.map(row => [...row]),
        startTime: startTime,
        errorCount: errorCount,
        hintCount: hintCount
    };
}

function loadAutoSave() {
    if (autoSaveData) {
        currentGrid = autoSaveData.grid.map(row => [...row]);
        originalGrid = autoSaveData.originalGrid.map(row => [...row]);
        startTime = autoSaveData.startTime;
        errorCount = autoSaveData.errorCount;
        hintCount = autoSaveData.hintCount;
        
        displayGrid(currentGrid);
        updateStats();
        
        if (startTime) {
            startTimer();
        }
        
        showMessage('Previous session restored!', 'info', 'fas fa-history');
    }
}

// Auto-save every 30 seconds
setInterval(autoSave, 30000);

// Initialize the application
function initializeApp() {
    initializeGrid();
    addHintButton();
    
    // Add keyboard shortcut info
    const shortcutInfo = document.createElement('div');
    shortcutInfo.innerHTML = `
        <div style="margin-top: 1rem; padding: 1rem; background: rgba(99, 102, 241, 0.1); border-radius: 0.5rem; font-size: 0.75rem; color: var(--gray-600);">
            <strong>Keyboard Shortcuts:</strong><br>
            Ctrl+S: Solve | Ctrl+R: Clear | Ctrl+G: Generate | Ctrl+V: Validate
        </div>
    `;
    document.querySelector('.sidebar').appendChild(shortcutInfo);
    
    // Check for auto-save data
    setTimeout(loadAutoSave, 1000);
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', initializeApp);

// Handle page visibility change for auto-save
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        autoSave();
    }
});

// Handle before unload for auto-save
window.addEventListener('beforeunload', autoSave);