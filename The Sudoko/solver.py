import numpy as np

class SudokuSolver:
    """Sudoku solver using backtracking algorithm."""
    
    def __init__(self):
        self.size = 9
        
    def is_valid(self, grid, row, col, num):
        """Check if placing num at (row, col) is valid."""
        
        # Check row
        if num in grid[row]:
            return False
        
        # Check column
        if num in grid[:, col]:
            return False
        
        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        if num in grid[box_row:box_row+3, box_col:box_col+3]:
            return False
        
        return True
    
    def find_empty_cell(self, grid):
        """Find the next empty cell (0) in the grid."""
        for i in range(self.size):
            for j in range(self.size):
                if grid[i][j] == 0:
                    return i, j
        return None
    
    def solve(self, grid):
        """Solve the Sudoku puzzle using backtracking."""
        grid = grid.copy()  # Don't modify original
        
        empty = self.find_empty_cell(grid)
        if not empty:
            return grid  # Puzzle solved
        
        row, col = empty
        
        for num in range(1, 10):
            if self.is_valid(grid, row, col, num):
                grid[row][col] = num
                
                result = self.solve(grid)
                if result is not None:
                    return result
                
                grid[row][col] = 0  # Backtrack
        
        return None  # No solution found
    
    def is_valid_puzzle(self, grid):
        """Check if the puzzle is valid (has unique solution)."""
        # Check for duplicate numbers in rows, columns, boxes
        for i in range(self.size):
            # Check row
            row = [x for x in grid[i] if x != 0]
            if len(row) != len(set(row)):
                return False
            
            # Check column
            col = [grid[j][i] for j in range(self.size) if grid[j][i] != 0]
            if len(col) != len(set(col)):
                return False
        
        # Check 3x3 boxes
        for box_row in range(0, self.size, 3):
            for box_col in range(0, self.size, 3):
                box = []
                for i in range(box_row, box_row + 3):
                    for j in range(box_col, box_col + 3):
                        if grid[i][j] != 0:
                            box.append(grid[i][j])
                if len(box) != len(set(box)):
                    return False
        
        return True
