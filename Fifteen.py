"""Loyd's Fifteen puzzle - solver and visualizer.  Note that solved configuration
has the blank (zero) tile in upper left.  Use the arrows key to swap this tile
with its neighbors.

Can enter the array size at bottom.

Rohan Lewis

March 2018 """

import poc_fifteen_gui

class Puzzle:
    """Class representation for the Fifteen puzzle."""

    def __init__(self, puzzle_height, puzzle_width, initial_grid=None) :
        """Initialize puzzle with default height and width.  Returns a Puzzle object"""
        self._height = puzzle_height
        self._width = puzzle_width
        self._grid = [[col + puzzle_width * row
                       for col in range(self._width)]
                      for row in range(self._height)]

        if initial_grid != None :
            for row in range(puzzle_height) :
                for col in range(puzzle_width) :
                    self._grid[row][col] = initial_grid[row][col]

    def __str__(self) :
        """Generate string representaion for puzzle.  Returns a string."""
        ans = ""
        for row in range(self._height) :
            ans += str(self._grid[row])
            ans += "\n"
        return ans

    #####################################
    # GUI methods

    def get_height(self) :
        """Getter for puzzle height.  Returns an integer."""
        return self._height

    def get_width(self) :
        """Getter for puzzle width.   Returns an integer."""
        return self._width

    def get_number(self, row, col) :
        """Getter for the number at tile position pos.  Returns an integer."""
        return self._grid[row][col]

    def set_number(self, row, col, value) :
        """Setter for the number at tile position pos."""
        self._grid[row][col] = value

    def clone(self) :
        """Make a copy of the puzzle to update during solving.  Returns a Puzzle object."""
        new_puzzle = Puzzle(self._height, self._width, self._grid)
        return new_puzzle

    ########################################################
    # Core puzzle methods

    def current_position(self, solved_row, solved_col) :
        """Locate the current position of the tile that will be at position (solved_row, solved_col) when the puzzle
        is solved.  Returns a tuple of two integers."""
        solved_value = (solved_col + self._width * solved_row)

        for row in range(self._height) :
            for col in range(self._width) :
                if self._grid[row][col] == solved_value:
                    return (row, col)
        assert False, "Value " + str(solved_value) + " not found"

    def update_puzzle(self, move_string) :
        """Updates the puzzle state based on the provided move string."""
        zero_row, zero_col = self.current_position(0, 0)
        for direction in move_string :
            if direction == "l":
                assert zero_col > 0, "move off grid: " + direction
                self._grid[zero_row][zero_col] = self._grid[zero_row][zero_col - 1]
                self._grid[zero_row][zero_col - 1] = 0
                zero_col -= 1
            elif direction == "r" :
                assert zero_col < self._width - 1, "move off grid: " + direction
                self._grid[zero_row][zero_col] = self._grid[zero_row][zero_col + 1]
                self._grid[zero_row][zero_col + 1] = 0
                zero_col += 1
            elif direction == "u" :
                assert zero_row > 0, "move off grid: " + direction
                self._grid[zero_row][zero_col] = self._grid[zero_row - 1][zero_col]
                self._grid[zero_row - 1][zero_col] = 0
                zero_row -= 1
            elif direction == "d" :
                assert zero_row < self._height - 1, "move off grid: " + direction
                self._grid[zero_row][zero_col] = self._grid[zero_row + 1][zero_col]
                self._grid[zero_row + 1][zero_col] = 0
                zero_row += 1
            else:
                assert False, "invalid direction: " + direction

    ##################################################################
    # Phase one methods
    
    def zero_corner_initialize(self) :
        """Move zero tile to bottom right corner."""
        ver_position = self.current_position(0,0)[0]
        ver_distance = self.get_height() - 1 - ver_position
        hor_position = self.current_position(0,0)[1]
        hor_distance = self.get_width() - 1 - hor_position
        move_string = "r" * hor_distance + "d" * ver_distance
        self.update_puzzle(move_string)
        return move_string

    def lower_row_invariant(self, target_row, target_col) :
        """Three part check."""
        #Check if tile zero is positioned at (i,j).
        if self.get_number(target_row, target_col) != 0 :
            return False
        
        #All tiles in rows i+1 or below are positioned at their solved location.
        dummy_row = self.get_height() - 1
        while target_row < dummy_row :
            for dummy_col in range(self.get_width()) :
                dummy_value = dummy_col + self.get_width() * dummy_row
                if self.get_number(dummy_row, dummy_col) != dummy_value :
                    return False
            dummy_row -= 1
            
        #All tiles in row i to the right of position (i,j) are positioned at their solved location.
        dummy_col = self.get_width() - 1
        while target_col < dummy_col :
            dummy_value = dummy_col + self.get_width() * target_row
            if self.get_number(target_row, dummy_col) != dummy_value :
                return False
            dummy_col -= 1

        #If all three above are true.
        return True

    def solve_interior_tile(self, target_row, target_col) :
        """Where is the correct tile?"""
        ver_position = self.current_position(target_row, target_col)[0]
        ver_distance = target_row - ver_position
        hor_position = self.current_position(target_row, target_col)[1]
        hor_distance = abs(target_col - hor_position)
        
        #If the correct tile is on the same row then it has to be to the left.  Move it right directly to
        #the target position.
        if ver_position == target_row :
            move_string = ("l" * hor_distance +
                           "urrdl" * (hor_distance - 1) )

        #If the correct tile is not on the same row, it has to be above, as rows below are solved.
        else :
            #Move zero tile up to the row below the correct tile.  If correct tile is in the same column as
            #the target, then zero tile will be directly under correct tile.    
            move_string = "u" * (ver_distance - 1)

            #Check if the correct tile is to the left of the target.  Move target to center.  Move zero tile 
            #directly under correct tile.
            if hor_position < target_col :
                #Check if in row zero.
                if ver_position == 0 :
                    move_string += ("u"+ "l" * hor_distance +
                                    "drrul" * (hor_distance - 1) +
                                    "dr")
                else :
                    move_string += ("u"+ "l" * hor_distance +
                                    "urrdl" * (hor_distance - 1) +
                                    "dr")

            #Check if the correct tile is to the right of the target.  Move target to center.  Move zero tile
            #directly under correct tile.
            elif hor_position > target_col :
                #Check if in row zero.
                if ver_position == 0 :
                    move_string += ("u" + "r" * hor_distance +
                                    "dllur" * (hor_distance - 1) +
                                    "dl")
                else :
                    move_string += ("u" + "r" * hor_distance +
                                    "ulldr" * (hor_distance - 1) +
                                    "ullddr")
            
            #Move correct tile down to target.  Loop zero tile counterclockwise around the left and
            #place it in the position left of correct tile and target.
            move_string += "ulddr" * (ver_distance - 1) + "uld"

        self.update_puzzle(move_string)
        return move_string

    def solve_col0_tile(self, target_row) :
        """Solve tile in column zero on specified row (> 1).  Updates puzzle and returns a move string."""
        ver_position = self.current_position(target_row, 0)[0] 
        ver_distance = target_row - ver_position 
        #hor_position 
        hor_distance = self.current_position(target_row, 0)[1]
                
        #Check if correct tile one above target (i-1, 0).
        if ver_distance == 1 :
            if hor_distance == 0 :
                move_string = "u"
            elif hor_distance == 1 :
                move_string = "urulddrulurddlu"
            else :
                move_string = ("ru" + "r" * (hor_distance - 1) +
                               "ulldr" * (hor_distance - 1) + 
                               "dlu")
        
        #Move tile in (target_row, 1) to (target_row, 0).  Move correct tile for (target_row, 0)
        #to (target_row - 1, 0).
        else :
            move_string = "r"
            
            #Correct tile is in column 0.  Move zero tile directly under correct tile.
            if hor_distance == 0:
                move_string += ("ul" + "u" * (ver_distance - 2))            
            
            #Correct tile is in column 1.  Move it to column 0 and move zero tile directly under
            #correct tile.
            elif hor_distance == 1 :
                move_string += ("u" * (ver_distance - 1) +
                                "lurdl")

            #Correct tile is to the right of target.  Move zero tile directly under correct tile.
            else :
                move_string += ("u" * ver_distance +
                                "r" * (hor_distance - 1) +
                                "dllur" * (hor_distance - 1)+
                                "dl")
                         
            #Move correct tile down to target.  Loop zero tile counterclockwise around the left and
            #place it in the position left of correct tile and target.
            move_string += ("u" + "rddlu" * (ver_distance - 1))

        #Move zero tile from column zero all the way to the right.
        move_string += "r" * (self.get_width() - 1)    
        self.update_puzzle(move_string)
        return move_string     
    

    #############################################################
    # Phase two methods

    def row0_invariant(self, target_col) :
        """Check whether the puzzle satisfies the row zero invariant at the given column (col > 1). Returns a boolean.
        Four part check."""
        
        #Check if tile zero is positioned at (0, j).
        if self.get_number(0, target_col) != 0 :
            return False
        
        #Check if correct tile is positioned at (1, j).
        dummy_value = target_col + self.get_width()
        if self.get_number(1, target_col) != dummy_value :
            return False        
        
        #All tiles in row 0 and row 1 to the right of position (0, j) are positioned at their solved location.
        dummy_row = 1 
        dummy_col = self.get_width() - 1
        while dummy_row >= 0 :
            while target_col < dummy_col :
                dummy_value = dummy_col + self.get_width() * dummy_row
                if self.get_number(dummy_row, dummy_col) != dummy_value :
                    return False
                dummy_col -= 1
            dummy_row -= 1
            dummy_col = self.get_width() - 1
            
        #All tiles in rows 2 or below are positioned at their solved location.
        dummy_row = self.get_height() - 1
        while dummy_row > 1 :
            for dummy_col in range(self.get_width()) :
                dummy_value = dummy_col + self.get_width() * dummy_row
                if self.get_number(dummy_row, dummy_col) != dummy_value :
                    return False
            dummy_row -= 1

        #If all three above are true.
        return True

    def row1_invariant(self, target_col) :
        """Check whether the puzzle satisfies the row one invariant at the given column (col > 1). Returns a boolean."""

        #All tiles in row 0 and row 1 to the right of position (1, j) are positioned at their solved location.
        dummy_row = 1 
        dummy_col = self.get_width() - 1
        while dummy_row >= 0 :
            while target_col < dummy_col :
                dummy_value = dummy_col + self.get_width() * dummy_row
                if self.get_number(dummy_row, dummy_col) != dummy_value :
                    return False
                dummy_col -= 1
            dummy_row -= 1
            dummy_col = self.get_width() - 1

        #Zero tile is at (1, j).
        #All tiles in row 1 to the right of (1, j) are positioned at their solved location.
        #All tiles in rows 2 or below are positioned at their solved location.
        return self.lower_row_invariant(1, target_col)    
        
    def solve_row0_tile(self, target_col) :
        """Solve the tile in row zero at the specified column.  Updates puzzle and returns a move string."""
        #ver_position  
        ver_distance = self.current_position(0, target_col)[0]
        hor_position = self.current_position(0, target_col)[1]
        hor_distance = target_col - hor_position
        
        #Check if correct tile is 1 tile left of target.
        if hor_distance == 1 :
            if ver_distance == 0 :
                move_string = ""
            elif hor_distance == 1 :
                move_string = "ldlurrdluldrru"
        
        #Zero tile is several left of target.
        else :
            #Move tile in (1, target_col) to (0, target_col).  Move correct tile for (0, target_col)
            #to (0, target_col - 1).  
            move_string = "d"
            
            #Correct tile is in row 0.  Move zero tile directly to the right of correct tile.
            if ver_distance == 0:
                move_string += ("lu" + "l" * (hor_distance - 2))            
            
            #Correct tile is in row 1.  Move it to row 0 and move zero tile directly to the right
            #of correct tile.
            elif ver_distance == 1 :
                move_string += ("l" * (hor_distance - 1) + "uldru")
                  
            #Move correct tile right to target.  Loop zero tile counterclockwise around the left and
            #place correct tile for (1, target_col).
            move_string += ("ldrru" * (hor_distance - 1))
        
        #Move correct tile to target.  Move zero tile to (1, target_col - 1).
        move_string += "ld"
        self.update_puzzle(move_string)
        return move_string     
   
    def solve_row1_tile(self, target_col) :
        """Solve the tile in row one at the specified column.  Updates puzzle and returns a move string."""
        ver_position = self.current_position(1, target_col)[0] 
        ver_distance = 1 - ver_position 
        hor_position = self.current_position(1, target_col)[1]
        hor_distance = target_col - hor_position
        
        #Correct tile is in cell (0, j).
        if hor_distance == 0 :
            move_string = "u"

        #Correct tile is in row 0 to the left of (0, j).
        elif ver_distance == 1 :
            move_string = ("lurdl" * hor_distance +
                           "urrdl" * (hor_distance - 1)
                           + "ur")
                           
        #Correct tile is in row 1 to the left of (1, j).
        else :
            move_string = ("l" * hor_distance +
                           "urrdl" * (hor_distance - 1)
                           + "ur")

        self.update_puzzle(move_string)
        return move_string  

    ###########################################################
    # Phase 3 methods

    def solve_2x2(self) :
        """Solve the upper left 2x2 part of the puzzle.  Updates the puzzle and returns a move string."""
        zero_location = self.current_position(0,0)
        one_location = self.current_position(0,1)
                   
        if zero_location == (0,0) :
            if one_location == (0,1) :
                move_string = ""
            elif one_location == (1,0) :
                move_string = "drul"
            elif one_location == (1,1) :
                move_string = "rdlu"
        
        elif zero_location == (0,1) :
            if one_location == (0,0) :
                move_string = "l"
            elif one_location == (1,0) :
                move_string = "ldrul"
            elif one_location == (1,1) :
                move_string = "dlu"

        elif zero_location == (1,0) :
            if one_location == (0,0) :
                move_string = "rul"
            elif one_location == (0,1) :
                move_string = "u"
            elif one_location == (1,1) :
                move_string = "urdlu"

        elif zero_location == (1,1) :
            if one_location == (0,0) :
                move_string = "ul"
            elif one_location == (0,1) :
                move_string = "lu"
            elif one_location == (1,0) :
                move_string = "uldrul"
        
        self.update_puzzle(move_string)
        return move_string  

    def solve_puzzle(self) :
        """Generate a solution string for a puzzle.  Updates the puzzle and returns a move string."""
        my_puzzle = self.clone()
        
        target_row = my_puzzle.get_height() - 1
        target_col = my_puzzle.get_width() - 1
        move_string = ""
    
        #Phase 1.
        move_string += my_puzzle.zero_corner_initialize()
        while target_row > 1 :
            while target_col > 0 :
                assert my_puzzle.lower_row_invariant(target_row, target_col), "Problem with invariant (" + str(target_col) + ", " + str(target_col) + ")."
                move_string += my_puzzle.solve_interior_tile(target_row, target_col)
                target_col -= 1
            
            if target_col == 0 :
                assert my_puzzle.lower_row_invariant(target_row, target_col), "Problem with invariant (" + str(target_col) + ", " + str(target_col) + ")."
                move_string += my_puzzle.solve_col0_tile(target_row)
                target_col = my_puzzle.get_width() - 1

            target_row -= 1

        #Phase 2.
        assert target_row == 1, "Phase 1 not complete."
        assert target_col == my_puzzle.get_width() - 1, "Phase 1 not complete."
        while target_col > 1:
            assert my_puzzle.row1_invariant(target_col), "Problem with invariant (1, " + str(target_col) + ")."
            move_string += my_puzzle.solve_row1_tile(target_col)
            assert my_puzzle.row0_invariant(target_col), "Problem with invariant (0, " + str(target_col) + ")."
            move_string += my_puzzle.solve_row0_tile(target_col)
            target_col -=1
            
        #Phase 3.
        move_string += my_puzzle.solve_2x2()
        self.update_puzzle(move_string)
        return move_string

# Start interactive simulation
poc_fifteen_gui.FifteenGUI(Puzzle(4, 4))
