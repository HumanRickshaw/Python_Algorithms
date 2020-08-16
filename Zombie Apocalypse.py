"""Student portion of Zombie Apocalypse mini-project

Can enter the array size at bottom.

Rohan Lewis

March 2018 """

import random
import poc_grid
import poc_queue
import poc_zombie_gui

# global constants
EMPTY = 0 
FULL = 1
FOUR_WAY = 0
EIGHT_WAY = 1
OBSTACLE = 5
HUMAN = 6
ZOMBIE = 7

class Apocalypse(poc_grid.Grid):
    """Class for simulating zombie pursuit of human on grid with obstacles."""
    
    def __init__(self, grid_height, grid_width,
                 obstacle_list = None,
                 zombie_list = None,
                 human_list = None) :
        """Create a simulation of given size with given obstacles, humans, and zombies."""
        
        poc_grid.Grid.__init__(self, grid_height, grid_width)
        if obstacle_list != None :
            for cell in obstacle_list :
                self.set_full(cell[0], cell[1])
        
        if zombie_list != None:
            self._zombie_list = list(zombie_list)
        else:
            self._zombie_list = []
        
        if human_list != None:
            self._human_list = list(human_list)  
        else:
            self._human_list = []
        
    def clear(self):
        """Set cells in obstacle grid to be empty.  Reset zombie and human lists to be empty."""
        poc_grid.Grid.clear(self)
        self._zombie_list = []
        self._human_list = []
        
    def add_zombie(self, row, col):
        """Add zombie to the zombie list."""
        self._zombie_list.append((row,col))
                
    def num_zombies(self):
        """Return number of zombies."""
        return len(self._zombie_list)      
          
    def zombies(self):
        """Generator that yields the zombies in the order they were added."""
        for zombie in self._zombie_list :
            yield zombie

    def add_human(self, row, col) :
        """Add human to the human list."""
        self._human_list.append((row,col))
        
    def num_humans(self):
        """Return number of humans."""
        return len(self._human_list)  
    
    def humans(self):
        """Generator that yields the humans in the order they were added."""
        for human in self._human_list :
            yield human
        
    def compute_distance_field(self, entity_type) :
        """Function computes and returns a 2D distance field.  Distance at member of
        entity_list is zero.  Shortest paths avoid obstacles and use four-way distances."""
        visited = poc_grid.Grid(self._grid_height, self._grid_width)
        
        distance_field = []
        for dummy_row in range(self._grid_height) :
            distance_field.append([])
            for dummy_col in range(self._grid_width) :
                distance_field[dummy_row].append(self._grid_height*self._grid_width)
        
        boundary = []
        if entity_type == 6 :
            for dummy_human in self.humans() :
                boundary.append(dummy_human)
        if entity_type == 7 :
            for dummy_zombie in self.zombies() :
                boundary.append(dummy_zombie)
                
        for cell in boundary :
            visited.set_full(cell[0],cell[1])
            distance_field[cell[0]][cell[1]] = 0
            
        while len(boundary) > 0 :
            current_cell = boundary.pop(0)
            for neighbor_cell in self.four_neighbors(current_cell[0], current_cell[1]) :
                if visited.is_empty(neighbor_cell[0], neighbor_cell[1]) and self.is_empty(neighbor_cell[0], neighbor_cell[1]):
                    visited.set_full(neighbor_cell[0], neighbor_cell[1])
                    boundary.append(neighbor_cell)
                    distance_field[neighbor_cell[0]][neighbor_cell[1]] = distance_field[current_cell[0]][current_cell[1]] + 1
        
        return distance_field
       
    def move_humans(self, zombie_distance_field) :
        """Function that moves humans away from zombies, diagonal moves are allowed."""
        moved_human_list = []    
        for human in self.humans() :
            max_distance = zombie_distance_field[human[0]][human[1]]
            move_human = human
            for neighbor_cell in self.eight_neighbors(human[0], human[1]) :
                if self.is_empty(neighbor_cell[0], neighbor_cell[1]) :
                    if zombie_distance_field[neighbor_cell[0]][neighbor_cell[1]] > max_distance :
                        max_distance = zombie_distance_field[neighbor_cell[0]][neighbor_cell[1]]
                        move_human = neighbor_cell
            moved_human_list.append(move_human)
        
        self._human_list = []
        for moved_human in moved_human_list :
            self.add_human(moved_human[0], moved_human[1])
               
    def move_zombies(self, human_distance_field) :
        """Function that moves zombies towards humans, no diagonal moves are allowed."""
        moved_zombie_list = []
        for zombie in self.zombies() :
            min_distance = human_distance_field[zombie[0]][zombie[1]]
            move_zombie = zombie
            for neighbor_cell in self.four_neighbors(zombie[0], zombie[1]) :
                if self.is_empty(neighbor_cell[0], neighbor_cell[1]) :
                    if human_distance_field[neighbor_cell[0]][neighbor_cell[1]] < min_distance :
                        min_distance = human_distance_field[neighbor_cell[0]][neighbor_cell[1]]
                        move_zombie = neighbor_cell
            moved_zombie_list.append(move_zombie)

        self._zombie_list = []
        for moved_zombie in moved_zombie_list :
            self.add_zombie(moved_zombie[0], moved_zombie[1])
            
poc_zombie_gui.run_gui(Apocalypse(30, 40))