""" Clone of 2048 game.

Can enter the array size at bottom.

Rohan Lewis

November 2017 """

import poc_2048_gui
import random

# Directions, DO NOT MODIFY.
UP = 1
DOWN = 2
LEFT = 3
RIGHT = 4

# Offsets for computing tile indices in each direction.
# DO NOT MODIFY this dictionary.
OFFSETS = {UP: (1, 0),
           DOWN: (-1, 0),
           LEFT: (0, 1),
           RIGHT: (0, -1)}

def merge(line):
    """ Helper function that merges a single row or column in 2048."""
    merged = False
    new_list = []
    for item in line :
        if item != 0 :
            new_list.append(item)
            if merged == True :
                merged = False
            elif len(new_list) > 1 :
                if new_list[-1] == new_list[-2] :
                    merged = True
                    new_list.pop(-1)
                    new_list[-1] *= 2
    while len(new_list) < len(line) :
        new_list.append(0)
    return new_list    

class TwentyFortyEight :
    """ Class to run the game logic. """

    def __init__(self, grid_height, grid_width):
        self._grid = {}
        self._height = grid_height
        self._width = grid_width
        self._merge_happened = False
        self.reset()
     
    def reset(self) :
        """ Reset the game so the grid is empty except for two initial tiles. """
        for row in xrange(0, self._height) :
            for col in xrange(0, self._width) :
                self.set_tile(row, col, 0)
        self.new_tile()
        self.new_tile()
        
    def __str__(self):
        """
        Return a string representation of the grid for debugging.
        """
        str_array = ''
        for row in xrange(0,self._height):
            temp_list = []
            for col in xrange(0,self._width) :
                temp_list.append(self.get_tile(row,col))
            str_array += str(temp_list) +'\n'
        return str_array

    def get_grid_height(self):
        """ Get the height of the board. """
        return self._height

    def get_grid_width(self):
        """ Get the width of the board. """
        return self._width

    def move(self, direction):
        """ Move all tiles in the given direction and add a new tile if any tiles
        moved. """
        if (direction == UP) or (direction == DOWN) :
            list_of_columns = []
            for col in xrange(0,self._width) :
                a_column_list = []
                for row in xrange(0,self._height) :
                    a_column_list.append(self.get_tile(row,col))
                list_of_columns.append(a_column_list)
            if direction == UP :
                list_of_columns = self.merge_all_the_lists(list_of_columns)
            else :
                list_of_columns = self.reverse_merge_reverse(list_of_columns)
            self.update_all_the_tiles(UP, list_of_columns)
    
        else :
            list_of_rows = []
            for row in xrange(0,self._height) :
                a_row_list = []
                for col in xrange(0,self._width) :
                    a_row_list.append(self.get_tile(row,col))
                list_of_rows.append(a_row_list)
            if direction == LEFT :
                list_of_rows = self.merge_all_the_lists(list_of_rows)
            else :
                list_of_rows = self.reverse_merge_reverse(list_of_rows)
            self.update_all_the_tiles(LEFT, list_of_rows)
        
        if self._merge_happened == True :
            self.new_tile()
 
    def reverse_merge_reverse(self, list_of_lists) :       
        """ Helper function for down and right, as they require reversing before and
        after merge. """
        self.reverse_all_the_lists(list_of_lists)
        list_of_lists = self.merge_all_the_lists(list_of_lists)
        self.reverse_all_the_lists(list_of_lists)
        return list_of_lists
        
    def reverse_all_the_lists(self, list_of_lists) :
        """ Helper function for move to reverse all lists within a list. """
        for a_list in list_of_lists :
            a_list.reverse()
    
    def merge_all_the_lists(self, list_of_lists) :
        """ Helper function for move to merge all lists within a list. """
        self._merge_happened = False
        list_of_merged_lists = []
        for a_list in list_of_lists :
            if a_list !=  merge(a_list) :
                self._merge_happened = True
            a_list = merge(a_list)
            list_of_merged_lists.append(a_list)
        return list_of_merged_lists
    
    def update_all_the_tiles(self, direction, list_of_lists) :
        """ Helper function for move to update all values in the grid. """
        for row in xrange(0,self._height) :
            for col in xrange(0,self._width) :
                if direction == UP :
                    self.set_tile(row, col, list_of_lists[col][row])
                else :
                    self.set_tile(row, col, list_of_lists[row][col])
        print str(self)
    
    def new_tile(self):
        """ First checks that there are empty tiles.
        Then, creates a new tile in a randomly selected empty square.  The tile should
        be 2 90% of the time and 4 10% of the time. """
        
        if 0 in self._grid.values() :
            while True :
                row = random.randrange(0, self._height)
                col = random.randrange(0, self._width)
                if self.get_tile(row, col) == 0 :
                    spawned_value = 2
                    rand_int = random.randrange(0,10)
                    if rand_int == 4 :
                        spawned_value = 4
                    self.set_tile(row, col, spawned_value)
                    return
        else :
            print ("Game Over!")
               
    def set_tile(self, row, col, value):
        """ Set the tile at position row, col to have the given value. """
        self._grid[(row, col)] = value
        
    def get_tile(self, row, col):
        """ Return the value of the tile at position row, col. """
        return self._grid[(row, col)]
    
poc_2048_gui.run_gui(TwentyFortyEight(4, 4))

