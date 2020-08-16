""" Spaceship

Rohan Lewis

November 2017 """

import simplegui
import math
import random

# Globals for user interface.
WIDTH = 800
HEIGHT = 600
DIM = [WIDTH, HEIGHT]
score = 0
lives = 3
time = 0
shots_fired = 0
asteroids = set([])
missiles = set([])
explosions = set([])
started = False

class ImageInfo :
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False) :
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated
    
# Art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# Debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# Nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.f2014.png")

# Splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# Ship image
ship_info = ImageInfo([45, 45], [90, 90], 35, None, False)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# Missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([10,10], [20, 20], 8, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot3.png")

# Asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)

# Animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# Alternative upbeat soundtrack by composer and former IIPP student Emiel Stopler
# Please do not redistribute without permission from Emiel at http://www.filmcomposer.nl
# Soundtrack = simplegui.load_sound("https://storage.googleapis.com/codeskulptor-assets/ricerocks_theme.mp3")

# Helper functions to handle transformations.
def angle_to_vector(ang) :
    return [math.cos(ang), math.sin(ang)]

def dist(p,q) :
    return math.sqrt((p[0] - q[0])**2 +(p[1] - q[1])**2)

def midp(p,q) :
    return [(p[0] + q[0])/2, (p[1] + q[1])/2]

# Draw asteroids and missiles from their sets.  Eliminate them if necessary.
def process_sprite_group(canvas, set) :
    for element in list(set) :
        element.draw(canvas)
        if element.animated == True :
            element.age += 1
            if element.age == element.lifespan :
                set.remove(element)
        if element.update() == True :
            set.remove(element)

# Collisions between a group and an object.
def group_collision(group, other_object) :
    occurence = False
    for element in list(group) :
        midpoint = midp(element.pos, other_object.pos)
        if element.collision(other_object) == True :
            group.remove(element)
            explosion_spawner(midpoint[0],midpoint[1])
            occurence = True
    return occurence

# Collisions between two groups.
def group_group_collision(group1, group2) :
    occurence = False
    for element in list(group2) :
        if group_collision(group1, element) == True :
            group2.remove(element)
            occurence = True
    return occurence

# Ship class.
class Ship :
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.death = False
        self.explosion_timer = 0
        
    def draw(self,canvas) :
        # Temporarily changes the ship to an explosion.
        if self.death == True :
            if self.explosion_timer < 24 :
                self.explosion_timer +=1
            else :
                self.death = False
                self.explosion_timer = 0
                self.pos = [WIDTH / 2, HEIGHT / 2]
                self.vel = [0, 0]
                self.angle = (3 * math.pi / 2)
        # Updates ship image if accelerating.
        else:
            if self.thrust == True :
                self.image_center = [135, 45]
            else :
                self.image_center = [45, 45]
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)

    def update(self) :
        for n in xrange(2) :
            self.pos[n] = (self.pos[n] + self.vel[n]) % DIM[n]
            self.vel[n] *= 0.97
        self.angle += self.angle_vel
        self.thrust_on(self.thrust)

    def thrust_on(self, thrust) :
        if self.thrust == True :
            for n in xrange(2) :
                self.vel[n] += angle_to_vector(self.angle)[n]
            ship_thrust_sound.play()
        else :
            ship_thrust_sound.pause()
            
# Sprite class.
class Sprite :
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
   
    def draw(self, canvas) :
        if self.animated == True :
            canvas.draw_image(self.image, [self.image_center[0] + self.age*128, self.image_center[1]], 
                              self.image_size, self.pos, self.image_size, self.angle)
        else :
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
    
    def update(self) :
        if self.lifespan == 50 :
            self.age += 1
            if self.age == self.lifespan :
                return True
        for n in xrange(2) :
            self.pos[n] = (self.pos[n] + self.vel[n]) % DIM[n]
        self.angle += self.angle_vel
        return False
    
    def collision(self, other_object) :
        if dist(self.pos, other_object.pos) <= (self.radius + other_object.radius) :
            return True
        else :
            return False

def click(pos):
    global lives, score, started
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True
        lives = 3
        score = 0
        soundtrack.play()
        
def draw(canvas) :
    global asteroids, lives, missiles, score, started, time
    
    # Animated background.
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    # Draw and update asteroids.
    process_sprite_group(canvas, asteroids)
    
    # Animate explosions.
    process_sprite_group(canvas, explosions)    

    # Draw and update missiles.
    process_sprite_group(canvas, missiles)
    
    # Draw and update ship.
    Rocinante.draw(canvas)
    Rocinante.update()
    
    # Draw the lives and score.
    canvas.draw_text("Lives: " + str(lives), (10, 25), 25, "White")
    canvas.draw_text("Score: " + str(score), (705, 25), 25, 'White')
    
    # Draw splash screen if not started.
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], 
                          splash_info.get_size())
    
    # Collisions.
    if group_collision(asteroids, Rocinante) == True :
        lives -= 1
        Rocinante.death = True
        explosion_spawner(Rocinante.pos[0], Rocinante.pos[1])
        asteroids = set([])
        missiles = set([])
    
    if group_group_collision(asteroids, missiles) == True :
        score += 1

    # Restart.    
    if lives == 0 :
            started = False
            soundtrack.pause()
            soundtrack.rewind()
            if shots_fired == 0:
                pass
            else:
                accuracy = 100 * score / shots_fired
                canvas.draw_text("Accuracy: " + str(accuracy) + "%", (330, 500), 25, "White")    

# Timer handler that spawns an asteroid and adds it to asteroids.    
def asteroid_spawner() :
    if started == True :
        asteroid_types = ["asteroid_blue.png", "asteroid_brown.png", "asteroid_blend.png"]
        asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/" + (asteroid_types[random.randrange(0,3,1)]))
        if len(asteroids) < 12 :
            asteroid = Sprite([(random.randrange(0, WIDTH, 1)), (random.randrange(0, HEIGHT, 1))], 
                              [(random.randrange(-25, 25, 1) / 10.0), (random.randrange(-25, 25, 1) / 10.0)],
                              0, (random.randrange(-5, 5, 1) / 25.0),
                              asteroid_image, asteroid_info)
            if dist(asteroid.pos, Rocinante.pos) <= 150 :
                pass
            else :
                asteroids.add(asteroid)

# Handler that spawns a missile and adds it to missiles.                
def missile_spawner() :
    global shots_fired
    if started == True :
        missiles.add(Sprite([(Rocinante.pos[0] + Rocinante.radius * angle_to_vector(Rocinante.angle)[0]), (Rocinante.pos[1] + Rocinante.radius * angle_to_vector(Rocinante.angle)[1])],
                            [(Rocinante.vel[0] + 7*angle_to_vector(Rocinante.angle)[0]), (Rocinante.vel[1] + 7*angle_to_vector(Rocinante.angle)[1])],
                            Rocinante.angle, 0,
                            missile_image, missile_info, missile_sound))
        shots_fired += 1

# Handler that spawns a temporary animated explosion and adds it to explosions.         
def explosion_spawner(x,y) :
    explosions.add(Sprite([x, y], [0, 0], 0, 0, explosion_image, explosion_info, explosion_sound))
    
# Rotate and accelerate ship, as well as shoot missile.  
def keydown(key) :
    #Rotation.
    if key == simplegui.KEY_MAP["left"] :
        Rocinante.angle_vel = -0.1
    elif key == simplegui.KEY_MAP["right"] :
        Rocinante.angle_vel = 0.1
    #Acceleration.
    if key == simplegui.KEY_MAP["up"] :
        Rocinante.thrust = True
    #Missile
    if key == simplegui.KEY_MAP["space"] :
        missile_spawner()
    
# Stop ship movement.        
def keyup(key) :
    if key == simplegui.KEY_MAP["left"] or key == simplegui.KEY_MAP["right"] :
        Rocinante.angle_vel = 0
    if key == simplegui.KEY_MAP["up"] :
        Rocinante.thrust = False 

# Initialize ship and asteroid
Rocinante = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], (3 * math.pi / 2), ship_image, ship_info)
asteroid_spawner()

# Initialize frame and register handlers.
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)
frame.set_draw_handler(draw)
timer = simplegui.create_timer(1000.0, asteroid_spawner)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.set_mouseclick_handler(click)

#!
timer.start()
frame.start()
soundtrack.set_volume(0.4)