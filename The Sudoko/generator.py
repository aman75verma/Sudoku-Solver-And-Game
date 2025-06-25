import numpy as np
import random
from solver import SudokuSolver

class SudokuGenerator:
    """Generate Sudoku puzzles of varying difficulty."""

    def __init__(self):
        self.solver = SudokuSolver()
        
    def generate_full_grid(self):
        """Generate a complete valid Sudoku grid."""
        grid = np.zeros((9, 9), dtype=int)
        
        # Fill diagonal 3x3 boxes first (they don't interfere with each other)
        for i in range(0, 9, 3):
            self.fill_box(grid, i, i)
        
        # Fill remaining cells
        if not self.fill_remaining(grid, 0, 3):
            raise RuntimeError("Failed to generate complete Sudoku grid")
        
        return grid
    
    def fill_box(self, grid, row, col):
        """Fill a 3x3 box with random valid numbers."""
        numbers = list(range(1, 10))
        random.shuffle(numbers)
        
        for i in range(3):
            for j in range(3):
                grid[row + i][col + j] = numbers[i * 3 + j]
    
    def fill_remaining(self, grid, i, j):
        """Fill remaining cells using backtracking."""
        if j >= 9 and i < 8:
            i += 1
            j = 0
        if i >= 9 and j >= 9:
            return True
        
        if i < 3:
            if j < 3:
                j = 3
        elif i < 6:
            if j == int(i / 3) * 3:
                j += 3
        else:
            if j == 6:
                i += 1
                j = 0
                if i >= 9:
                    return True
        
        numbers = list(range(1, 10))
        random.shuffle(numbers)
        
        for num in numbers:
            if self.solver.is_valid(grid, i, j, num):
                grid[i][j] = num
                if self.fill_remaining(grid, i, j + 1):
                    return True
                grid[i][j] = 0
        
        return False
    
    def remove_numbers(self, grid, difficulty):
        """Remove numbers based on filled cells (difficulty).
           Easy:   ~50-55 filled (26-31 removed)
           Medium: ~36-49 filled (32-45 removed)
           Hard:   ~17-35 filled (46-64 removed)
        """
        fill_counts = {  # Ranges for filled cells (not removed)
            'easy': (50, 55),   
            'medium': (36, 49),
            'hard': (17, 35)
        }
        
        # Calculate the desired number of filled cells
        min_fill, max_fill = fill_counts.get(difficulty, (40, 45))
        target_fill = random.randint(min_fill, max_fill)
        
        puzzle = grid.copy()
        total_cells = 81
        removed = 0
        max_attempts = 200
        attempts = 0
        
        # Generate all possible cell positions in a random order
        positions = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(positions)
        
        for i, j in positions:
            if removed >= (total_cells - target_fill) or attempts >= max_attempts:
                break  # Stop if target is reached or max attempts
            
            if puzzle[i][j] == 0:
                continue  # Skip already removed cells
            
            # Temporarily remove the number and check solvability
            backup = puzzle[i][j]
            puzzle[i][j] = 0
            
            solutions = []
            self.count_solutions(puzzle.copy(), solutions, max_solutions=2)
            
            if len(solutions) == 1:
                removed += 1  # Keep removal if only 1 solution exists
            else:
                puzzle[i][j] = backup  # Revert if multiple solutions
            
            attempts += 1
        
        return puzzle

    
    def has_unique_solution(self, puzzle):
        """Check if puzzle has exactly one solution."""
        solutions = []
        self.count_solutions(puzzle.copy(), solutions, 2)
        return len(solutions) == 1
    
    def count_solutions(self, grid, solutions, max_solutions):
        """Count number of solutions (up to max_solutions)."""
        if len(solutions) >= max_solutions:
            return
        
        empty = self.solver.find_empty_cell(grid)
        if not empty:
            solutions.append(grid.copy())
            return
        
        row, col = empty
        for num in range(1, 10):
            if self.solver.is_valid(grid, row, col, num):
                grid[row][col] = num
                self.count_solutions(grid, solutions, max_solutions)
                grid[row][col] = 0
                if len(solutions) >= max_solutions:
                    return
    
    def generate(self, difficulty='medium'):
        """Generate a Sudoku puzzle of specified difficulty."""
        full_grid = self.generate_full_grid()
        puzzle = self.remove_numbers(full_grid, difficulty)
        return puzzle
