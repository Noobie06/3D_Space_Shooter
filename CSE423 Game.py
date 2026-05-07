from OpenGL.GL import * 
from OpenGL.GLUT import * 
from OpenGL.GLU import * 
import math 
import random 

WINDOW_WIDTH = 1200 
WINDOW_HEIGHT = 900 
FPS = 60

fovY = 80.0 
camera_angle = 0.0 
camera_height = 200.0 
camera_radius = 1200.0
first_person = False 
fp_look_angle = 0.0 

player_x = 0.0 
player_y = 0.0 
player_z = 250.0
player_angle = 0.0 
player_pitch = 0.0
player_roll = 0.0
MOVE_SPEED = 12.0
ROTATE_SPEED = 4.5
VERTICAL_SPEED = 9.0

player_life = 5 
game_score = 0 
game_over = False 
game_paused = False
enemy_hit_cooldown = 0 
HIT_COOLDOWN_MAX = 40 

bullets = [] 
BULLET_SPEED = 22.0
BULLET_SIZE = 8 

enemies = [] 
NUM_ENEMIES = 8 
ENEMY_SPEED = 1.0
ENEMY_BASE_R = 30.0 
ENEMY_MIN_SCALE = 0.8 
ENEMY_MAX_SCALE = 1.2 
ENEMY_PULSE_STEP = 0.002 

cheat_mode = False 
cheat_vision = False 
CHEAT_ROTATE_STEP = 4.0
CHEAT_AIM_TOL = 3.0
cheat_locked = False 
cheat_fire_cooldown = 0
CHEAT_FIRE_COOLDOWN_MAX = 15

keys_pressed = {}
shift_pressed = False

space_storm_active = False
storm_turbulence_offset = 0.0

explosions = []
weapon_heat = 0.0
MAX_HEAT = 100.0
HEAT_PER_SHOT = 10.0
HEAT_DECAY = 0.8
overheated = False

screen_shake_time = 0
SHAKE_INTENSITY = 12.0

combo_count = 0
total_kills = 0

missiles = []
MISSILE_SPEED = 45.0
missiles_available = 0

boss_active = False
boss_hp = 1500
boss_max_hp = 1500
boss_x, boss_y, boss_z = 0, 3000, 0
boss_bullets = []
boss_shoot_timer = 0
boss_fire_timer = 0
BOSS_BULLET_SPEED = 10.0
boss_hit_flash = 0
boss_hits = 0
game_victory = False

# Boost System
boost_amount = 100.0
MAX_BOOST = 100.0
BOOST_MULTIPLIER = 3.0
BOOST_CONSUMPTION_RATE = 2.0
BOOST_REGEN_RATE = 0.15
BOOST_REGEN_DELAY = 60
boost_regen_timer = 0
is_boosting = False

# Planet System
NUM_PLANETS = 8
planets = []
planet_rotation = 0.0

STARS_COUNT = 300
STARS_RANGE = 2000
stars = [[random.uniform(-STARS_RANGE, STARS_RANGE), 
          random.uniform(-STARS_RANGE, STARS_RANGE), 
          random.uniform(-STARS_RANGE, STARS_RANGE)] for _ in range(STARS_COUNT)]

def _rad(deg): 
    return math.radians(deg) 

def _dist3d(ax, ay, az, bx, by, bz): 
    return math.sqrt((ax - bx) ** 2 + (ay - by) ** 2 + (az - bz) ** 2) 

def _angle_diff(current, target): 
    d = (target - current + 360) % 360 
    if d > 180: 
        d -= 360 
    return d 

def _fwd(angle): 
    r = _rad(angle) 
    return -math.sin(r), math.cos(r) 

def _spawn_enemy(): 
    dist = random.uniform(1000, 2000)
    ang = random.uniform(0, 2 * math.pi)
    phi = random.uniform(-math.pi/2, math.pi/2)
    
    ex = player_x + dist * math.cos(phi) * math.sin(ang)
    ey = player_y + dist * math.cos(phi) * math.cos(ang)
    ez = player_z + dist * math.sin(phi)
    
    return [ex, ey, ez, random.uniform(0.9, 1.1), ENEMY_PULSE_STEP]

def _spawn_explosion(x, y, z):
    for _ in range(20):
        vx = random.uniform(-5, 5)
        vy = random.uniform(-5, 5)
        vz = random.uniform(-5, 5)
        life = random.uniform(20, 40)
        explosions.append([x, y, z, vx, vy, vz, life])

def init_planets():
    global planets
    planets = []
    
    planet_configs = [
        {"radius": 200, "color": (0.2, 0.5, 1.0), "ring_color": None, "has_rings": False, "moon_count": 1},
        {"radius": 180, "color": (0.8, 0.2, 0.1), "ring_color": (0.9, 0.7, 0.4), "has_rings": True, "moon_count": 0},
        {"radius": 350, "color": (0.9, 0.7, 0.2), "ring_color": (0.7, 0.6, 0.5), "has_rings": True, "moon_count": 3},
        {"radius": 150, "color": (0.6, 0.9, 1.0), "ring_color": None, "has_rings": False, "moon_count": 0},
        {"radius": 300, "color": (0.6, 0.2, 0.8), "ring_color": (0.8, 0.5, 0.9), "has_rings": True, "moon_count": 2},
        {"radius": 120, "color": (0.5, 0.4, 0.3), "ring_color": None, "has_rings": False, "moon_count": 0},
        {"radius": 280, "color": (0.2, 0.8, 0.3), "ring_color": (0.4, 0.9, 0.5), "has_rings": True, "moon_count": 1},
        {"radius": 160, "color": (0.9, 0.6, 0.2), "ring_color": None, "has_rings": False, "moon_count": 0},
    ]
    
    for config in planet_configs:
        distance = random.uniform(2000, 5000)
        angle_h = random.uniform(0, 2 * math.pi)
        angle_v = random.uniform(-math.pi/3, math.pi/3)
        
        px = player_x + distance * math.cos(angle_v) * math.cos(angle_h)
        py = player_y + distance * math.cos(angle_v) * math.sin(angle_h)
        pz = player_z + distance * math.sin(angle_v)
        
        rotation_speed = random.uniform(0.1, 0.5)
        
        planets.append([
            px, py, pz,
            config["radius"],
            config["color"][0], config["color"][1], config["color"][2],
            config["ring_color"][0] if config["ring_color"] else 0,
            config["ring_color"][1] if config["ring_color"] else 0,
            config["ring_color"][2] if config["ring_color"] else 0,
            config["has_rings"],
            rotation_speed,
            config["moon_count"]
        ])

def init_game(): 
    global player_x, player_y, player_z, player_angle, player_pitch, player_roll, fp_look_angle 
    global player_life, game_score, game_over, game_paused, enemy_hit_cooldown 
    global bullets, enemies, explosions, cheat_mode, cheat_vision, cheat_locked 
    global camera_angle, camera_height, first_person 
    global weapon_heat, overheated, combo_count
    global space_storm_active, keys_pressed, shift_pressed
    global missiles, missiles_available
    global total_kills, boss_active, boss_hp, boss_max_hp, boss_bullets, game_victory, boss_hit_flash, boss_hits
    global planet_rotation, cheat_fire_cooldown
    global boost_amount, is_boosting, boost_regen_timer
    
    player_x = player_y = 0.0 
    player_z = 250.0
    player_angle = fp_look_angle = 0.0 
    player_pitch = 0.0
    player_roll = 0.0
    player_life = 5 
    game_score = 0 
    total_kills = 0
    game_over = False 
    game_victory = False
    game_paused = False
    enemy_hit_cooldown = 0 
    bullets = [] 
    enemies = [_spawn_enemy() for _ in range(NUM_ENEMIES)] 
    explosions = []
    missiles = []
    missiles_available = 0
    boss_active = False
    boss_max_hp = 1500
    boss_hp = boss_max_hp
    boss_bullets = []
    boss_hit_flash = 0
    boss_hits = 0
    cheat_mode = cheat_vision = cheat_locked = False 
    cheat_fire_cooldown = 0
    space_storm_active = False
    camera_angle = 0.0 
    camera_height = 200.0 
    first_person = False 
    weapon_heat = 0.0
    overheated = False
    combo_count = 0
    keys_pressed = {}
    shift_pressed = False
    planet_rotation = 0.0
    boost_amount = MAX_BOOST
    is_boosting = False
    boost_regen_timer = 0
    init_planets()

def setupCamera(): 
    global screen_shake_time
    glMatrixMode(GL_PROJECTION) 
    glLoadIdentity() 
    current_fov = fovY + 10.0 if (first_person or cheat_mode) else fovY
    gluPerspective(current_fov, WINDOW_WIDTH / WINDOW_HEIGHT, 1.0, 10000.0) 
    glMatrixMode(GL_MODELVIEW) 
    glLoadIdentity() 
    
    shake_x, shake_y, shake_z = 0, 0, 0
    if screen_shake_time > 0:
        shake_x = random.uniform(-SHAKE_INTENSITY, SHAKE_INTENSITY)
        shake_y = random.uniform(-SHAKE_INTENSITY, SHAKE_INTENSITY)
        shake_z = random.uniform(-SHAKE_INTENSITY, SHAKE_INTENSITY)
        screen_shake_time -= 1

    if first_person: 
        fdx, fdy = _fwd(player_angle) 
        eye_x = player_x - fdx * 60 + shake_x
        eye_y = player_y - fdy * 60 + shake_y
        eye_z = player_z + 80.0 + shake_z
        
        look_angle = player_angle if cheat_mode else fp_look_angle
        lfx, lfy = _fwd(look_angle) 
        
        lx = player_x + lfx * 1000 
        ly = player_y + lfy * 1000 
        lz = player_z 
        gluLookAt(eye_x, eye_y, eye_z, lx, ly, lz, 0, 0, 1) 
    else: 
        rad = _rad(camera_angle + player_angle) 
        cam_x = player_x + camera_radius * math.sin(rad) + shake_x
        cam_y = player_y - camera_radius * math.cos(rad) + shake_y
        cam_z = player_z + camera_height + shake_z
        gluLookAt(cam_x, cam_y, cam_z, player_x, player_y, player_z, 0, 0, 1) 

def draw_planet(px, py, pz, radius, cr, cg, cb, ring_cr, ring_cg, ring_cb, has_rings, rotation_angle, moon_count):
    glPushMatrix()
    glTranslatef(px, py, pz)
    glRotatef(rotation_angle, 0, 0, 1)
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(cr * 0.3, cg * 0.3, cb * 0.3, 0.3)
    quad = gluNewQuadric()
    gluQuadricNormals(quad, GLU_SMOOTH)
    gluSphere(quad, radius * 1.2, 32, 32)
    gluDeleteQuadric(quad)
    glDisable(GL_BLEND)
    
    glColor3f(cr, cg, cb)
    quad = gluNewQuadric()
    gluQuadricNormals(quad, GLU_SMOOTH)
    gluSphere(quad, radius, 32, 32)
    gluDeleteQuadric(quad)
    
    if radius > 250:
        for i in range(-3, 4):
            glPushMatrix()
            band_height = i * (radius / 4)
            glTranslatef(0, band_height, 0)
            glColor3f(cr * (0.7 + 0.1 * i), cg * (0.7 + 0.1 * i), cb * (0.7 + 0.1 * i))
            glScalef(1, 0.1, 1)
            quad = gluNewQuadric()
            gluQuadricNormals(quad, GLU_SMOOTH)
            gluSphere(quad, radius * 0.95, 32, 32)
            gluDeleteQuadric(quad)
            glPopMatrix()
    
    if radius <= 250:
        glColor3f(cr * 0.7, cg * 0.7, cb * 0.7)
        for i in range(6):
            spot_angle = i * (2 * math.pi / 6) + rotation_angle * 0.1
            spot_offset = random.uniform(0.3, 0.8) * radius
            spot_x = spot_offset * math.cos(spot_angle)
            spot_y = spot_offset * math.sin(spot_angle)
            
            glPushMatrix()
            glTranslatef(spot_x, spot_y, 0)
            spot_quad = gluNewQuadric()
            gluQuadricNormals(spot_quad, GLU_SMOOTH)
            gluSphere(spot_quad, radius * 0.12, 12, 12)
            gluDeleteQuadric(spot_quad)
            glPopMatrix()
    
    if has_rings:
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(ring_cr, ring_cg, ring_cb, 0.4)
        
        ring_quad = gluNewQuadric()
        
        glPushMatrix()
        glRotatef(25, 1, 0, 0)
        gluDisk(ring_quad, radius * 1.3, radius * 1.5, 64, 8)
        glPopMatrix()
        
        glColor4f(ring_cr * 1.2, ring_cg * 1.2, ring_cb * 1.2, 0.5)
        glPushMatrix()
        glRotatef(25, 1, 0, 0)
        gluDisk(ring_quad, radius * 1.6, radius * 1.8, 64, 8)
        glPopMatrix()
        
        glColor4f(ring_cr * 0.8, ring_cg * 0.8, ring_cb * 0.8, 0.3)
        glPushMatrix()
        glRotatef(25, 1, 0, 0)
        gluDisk(ring_quad, radius * 1.9, radius * 2.2, 64, 8)
        glPopMatrix()
        
        gluDeleteQuadric(ring_quad)
        glDisable(GL_BLEND)
    
    if moon_count > 0:
        for i in range(moon_count):
            moon_angle = rotation_angle * 2 + (i * 360 / moon_count)
            moon_orbit_radius = radius * (1.8 + i * 0.3)
            moon_x = moon_orbit_radius * math.cos(math.radians(moon_angle))
            moon_y = moon_orbit_radius * math.sin(math.radians(moon_angle))
            
            glPushMatrix()
            glTranslatef(moon_x, moon_y, 0)
            glColor3f(0.8, 0.8, 0.8)
            moon_quad = gluNewQuadric()
            gluQuadricNormals(moon_quad, GLU_SMOOTH)
            gluSphere(moon_quad, radius * 0.15, 16, 16)
            gluDeleteQuadric(moon_quad)
            glPopMatrix()
    
    glPopMatrix()

def draw_environment(): 
    glPointSize(1.5)
    glColor3f(0.8, 0.9, 1.0)
    glBegin(GL_POINTS)
    for s in stars:
        glVertex3f(s[0], s[1], s[2])
    glEnd()
    
    global planet_rotation
    for planet in planets:
        draw_planet(
            planet[0], planet[1], planet[2],
            planet[3],
            planet[4], planet[5], planet[6],
            planet[7], planet[8], planet[9],
            planet[10],
            planet_rotation * planet[11],
            planet[12]
        )

def draw_player(): 
    glPushMatrix() 
    glTranslatef(player_x, player_y, player_z) 
    glRotatef(player_angle, 0, 0, 1) 
    glRotatef(player_pitch, 1, 0, 0)
    glRotatef(player_roll, 0, 1, 0)
    
    glScalef(2.5, 2.5, 2.5)
    
    if game_over: 
        glRotatef(90, 1, 0, 0)
    
    if is_boosting:
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        
        for sx in [-1, 1]:
            glPushMatrix()
            glTranslatef(sx * 10, -55, 0)
            glColor4f(0.0, 0.5, 1.0, 0.3)
            glutSolidSphere(15, 16, 16)
            glColor4f(1.0, 1.0, 1.0, 0.8)
            glutSolidSphere(8, 16, 16)
            glPopMatrix()
        
        glColor4f(0.0, 0.8, 1.0, 0.3)
        for i in range(5):
            glPushMatrix()
            glTranslatef(random.uniform(-20, 20), random.uniform(-60, -30), random.uniform(-10, 10))
            glScalef(2, 30, 2)
            glutSolidCube(1)
            glPopMatrix()
        
        glDisable(GL_BLEND)
    
    glColor3f(0.4, 0.4, 0.45)
    glPushMatrix()
    glScalef(25, 100, 18)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(0.5, 0.5, 0.55)
    glPushMatrix()
    glTranslatef(0, 20, 5)
    glScalef(20, 40, 15)
    glutSolidCube(1)
    glPopMatrix()

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.0, 0.6, 1.0, 0.5)
    glPushMatrix()
    glTranslatef(0, 30, 15)
    glScalef(15, 35, 12)
    glutSolidSphere(1, 16, 16)
    glPopMatrix()
    glDisable(GL_BLEND)

    glColor3f(0.3, 0.3, 0.35)
    glPushMatrix()
    glTranslatef(0, 50, 0)
    glScalef(1, 1.5, 1)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 60, 0)
    for i in range(9):
        ang = i * (math.pi / 4)
        glVertex3f(12 * math.cos(ang), 0, 10 * math.sin(ang))
    glEnd()
    glPopMatrix()

    glColor3f(0.8, 0.8, 0.8)
    glPushMatrix()
    glTranslatef(0, 110, 0)
    glScalef(1, 40, 1)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(0.35, 0.35, 0.4)
    glBegin(GL_QUADS)
    glVertex3f(12.5, 40, -2)
    glVertex3f(110, -50, -2)
    glVertex3f(110, -75, -2)
    glVertex3f(12.5, -30, -2)
    glVertex3f(-12.5, 40, -2)
    glVertex3f(-110, -50, -2)
    glVertex3f(-110, -75, -2)
    glVertex3f(-12.5, -30, -2)
    glEnd()

    glColor3f(0.2, 0.2, 0.2)
    for sx in [-110, 110]:
        glPushMatrix()
        glTranslatef(sx, -62.5, -2)
        glScalef(8, 40, 8)
        glutSolidCube(1)
        glPopMatrix()

    glColor3f(0.4, 0.4, 0.45)
    for sx in [-1, 1]:
        glPushMatrix()
        glTranslatef(sx * 18, -40, 8)
        glRotatef(sx * 10, 0, 1, 0)
        glBegin(GL_QUADS)
        glVertex3f(0, 0, 0)
        glVertex3f(0, -50, 0)
        glVertex3f(0, -60, 45)
        glVertex3f(0, -15, 45)
        glEnd()
        glPopMatrix()

    for sx in [-1, 1]:
        glPushMatrix()
        glTranslatef(sx * 10, -55, 0)
        glColor3f(0.1, 0.1, 0.1)
        glutSolidTorus(2, 8, 8, 16)
        glColor3f(1.0, 0.3, 0.0)
        glPushMatrix()
        glTranslatef(0, -5, 0)
        glRotatef(180, 1, 0, 0)
        glutSolidCone(7, 30, 12, 6)
        glPopMatrix()
        glPopMatrix()

    glPopMatrix() 

def draw_enemy(ex, ey, ez, scale): 
    r = ENEMY_BASE_R * scale 
    glPushMatrix() 
    glTranslatef(ex, ey, ez) 
    
    glColor3f(0.7, 0.7, 0.8)
    glPushMatrix()
    glScalef(1, 1, 0.3)
    glutSolidSphere(r, 16, 16)
    glPopMatrix()

    glColor3f(0.0, 1.0, 0.4)
    glPushMatrix()
    glTranslatef(0, 0, r * 0.1)
    glutSolidSphere(r * 0.5, 12, 12)
    glPopMatrix()

    glPointSize(4.0)
    glBegin(GL_POINTS)
    for i in range(8):
        ang = i * (math.pi / 4)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(r * 0.9 * math.cos(ang), r * 0.9 * math.sin(ang), 0)
    glEnd()
    glPopMatrix() 

def draw_bullet(bx, by, bz): 
    glPushMatrix() 
    glTranslatef(bx, by, bz) 
    glColor3f(1.0, 0.2, 0.2)
    glutSolidSphere(BULLET_SIZE / 2, 8, 8) 
    glPopMatrix() 

def draw_missile(mx, my, mz):
    glPushMatrix()
    glTranslatef(mx, my, mz)
    glScalef(2.0, 2.0, 2.0)
    
    glColor3f(1.0, 0.5, 0.0)
    glPushMatrix()
    glScalef(8, 30, 8)
    glutSolidCube(1)
    glPopMatrix()
    
    glColor3f(1.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(0, 15, 0)
    glRotatef(-90, 1, 0, 0)
    glutSolidCone(5, 12, 8, 4)
    glPopMatrix()
    
    glColor3f(0.3, 0.3, 0.3)
    for r in [0, 90, 180, 270]:
        glPushMatrix()
        glRotatef(r, 0, 1, 0)
        glTranslatef(4, -10, 0)
        glBegin(GL_TRIANGLES)
        glVertex3f(0, 0, 0)
        glVertex3f(8, -5, 0)
        glVertex3f(0, -10, 0)
        glEnd()
        glPopMatrix()
        
    glColor3f(0.0, 1.0, 1.0)
    glPushMatrix()
    glTranslatef(0, -15, 0)
    glRotatef(90, 1, 0, 0)
    glutSolidCone(6, 40, 12, 6)
    glPopMatrix()
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(1.0, 0.8, 0.0, 0.4)
    glutSolidSphere(12, 12, 12)
    glDisable(GL_BLEND)
    glPopMatrix()

def draw_boss():
    glPushMatrix()
    glTranslatef(boss_x, boss_y, boss_z)
    
    dx = player_x - boss_x
    dy = player_y - boss_y
    angle = math.degrees(math.atan2(-dx, dy))
    glRotatef(angle, 0, 0, 1)
    glScalef(60.0, 60.0, 60.0)
    
    if boss_hit_flash > 0:
        glColor3f(1.0, 1.0, 1.0)
    else:
        glColor3f(0.0, 0.4, 1.0)
    
    glutSolidIcosahedron()
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    glColor4f(1.0, 0.0, 0.0, 0.6)
    glPushMatrix()
    glScalef(0.5, 0.5, 0.5)
    glutSolidSphere(1, 20, 20)
    glPopMatrix()
    
    glColor4f(0.0, 1.0, 1.0, 0.2)
    glutSolidSphere(1.2, 20, 20)
    glDisable(GL_BLEND)
    
    glColor3f(1.0, 0.8, 0.0)
    for i in range(8):
        glPushMatrix()
        glRotatef(i * 45, 0, 0, 1)
        glTranslatef(1.8, 0, 0)
        glScalef(2.5, 0.3, 0.3)
        glutSolidCube(1)
        glPopMatrix()
        
    glPopMatrix()

def draw_boss_bullet(bx, by, bz, is_fire):
    glPushMatrix()
    glTranslatef(bx, by, bz)
    
    if is_fire:
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glColor4f(1.0, 0.3, 0.0, 0.4)
        glutSolidSphere(60, 16, 16)
        glColor4f(1.0, 0.8, 0.0, 0.8)
        glutSolidSphere(30, 12, 12)
        glDisable(GL_BLEND)
    else:
        glColor3f(0.5, 0.0, 1.0)
        glutSolidSphere(15, 8, 8)
        
    glPopMatrix()

def draw_explosions():
    glPointSize(3.0)
    glBegin(GL_POINTS)
    for p in explosions:
        alpha = p[6] / 40.0
        glColor3f(1.0, 0.5 * alpha, 0.0)
        glVertex3f(p[0], p[1], p[2])
    glEnd()

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18): 
    glColor3f(1, 1, 1) 
    glMatrixMode(GL_PROJECTION) 
    glPushMatrix() 
    glLoadIdentity() 
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT) 
    glMatrixMode(GL_MODELVIEW) 
    glPushMatrix() 
    glLoadIdentity() 
    glRasterPos2f(x, y) 
    for ch in text: 
        glutBitmapCharacter(font, ord(ch)) 
    glPopMatrix() 
    glMatrixMode(GL_PROJECTION) 
    glPopMatrix() 
    glMatrixMode(GL_MODELVIEW) 

def draw_hud():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)

    # Boost Bar
    boost_bar_x = 30
    boost_bar_y = WINDOW_HEIGHT // 2 - 200
    boost_bar_width = 30
    boost_bar_height = 400
    
    glColor4f(0.1, 0.1, 0.1, 0.7)
    glBegin(GL_QUADS)
    glVertex2f(boost_bar_x - 5, boost_bar_y - 5)
    glVertex2f(boost_bar_x + boost_bar_width + 5, boost_bar_y - 5)
    glVertex2f(boost_bar_x + boost_bar_width + 5, boost_bar_y + boost_bar_height + 5)
    glVertex2f(boost_bar_x - 5, boost_bar_y + boost_bar_height + 5)
    glEnd()
    
    glColor3f(0.5, 0.5, 0.5)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(boost_bar_x, boost_bar_y)
    glVertex2f(boost_bar_x + boost_bar_width, boost_bar_y)
    glVertex2f(boost_bar_x + boost_bar_width, boost_bar_y + boost_bar_height)
    glVertex2f(boost_bar_x, boost_bar_y + boost_bar_height)
    glEnd()
    
    boost_ratio = boost_amount / MAX_BOOST
    boost_height = boost_bar_height * boost_ratio
    
    if boost_ratio > 0.6:
        glColor3f(0.0, 0.8, 1.0)
    elif boost_ratio > 0.3:
        glColor3f(0.0, 0.5, 1.0)
    else:
        glColor3f(0.0, 0.2, 0.8)
    
    if is_boosting:
        glColor3f(1.0, 0.5, 0.0)
    
    glBegin(GL_QUADS)
    glVertex2f(boost_bar_x + 2, boost_bar_y + 2)
    glVertex2f(boost_bar_x + boost_bar_width - 2, boost_bar_y + 2)
    glVertex2f(boost_bar_x + boost_bar_width - 2, boost_bar_y + boost_height - 2)
    glVertex2f(boost_bar_x + 2, boost_bar_y + boost_height - 2)
    glEnd()
    
    glColor4f(0.3, 0.3, 0.3, 0.5)
    glLineWidth(1.0)
    for i in range(1, 10):
        y_pos = boost_bar_y + (boost_bar_height * i / 10)
        glBegin(GL_LINES)
        glVertex2f(boost_bar_x, y_pos)
        glVertex2f(boost_bar_x + boost_bar_width, y_pos)
        glEnd()
    
    glColor3f(1.0, 1.0, 1.0)
    draw_text(boost_bar_x - 5, boost_bar_y + boost_bar_height + 15, "BOOST", GLUT_BITMAP_HELVETICA_12)
    boost_percent = int(boost_ratio * 100)
    draw_text(boost_bar_x, boost_bar_y - 25, f"{boost_percent}%", GLUT_BITMAP_HELVETICA_12)
    
    if is_boosting:
        glColor3f(1.0, 0.5, 0.0)
        draw_text(boost_bar_x - 10, boost_bar_y - 45, "ACTIVE", GLUT_BITMAP_HELVETICA_12)
    elif boost_regen_timer > 0:
        glColor3f(0.5, 0.5, 0.5)
        draw_text(boost_bar_x - 10, boost_bar_y - 45, f"REGEN:{boost_regen_timer//60 + 1}s", GLUT_BITMAP_HELVETICA_10)
    else:
        glColor3f(0.0, 1.0, 0.0)
        draw_text(boost_bar_x - 10, boost_bar_y - 45, "REGEN", GLUT_BITMAP_HELVETICA_12)

    # Crosshair
    if first_person:
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        glColor3f(0.0, 1.0, 0.0)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glVertex2f(cx - 20, cy)
        glVertex2f(cx + 20, cy)
        glVertex2f(cx, cy - 20)
        glVertex2f(cx, cy + 20)
        glEnd()
        glBegin(GL_LINE_LOOP)
        glVertex2f(cx - 5, cy - 5)
        glVertex2f(cx + 5, cy - 5)
        glVertex2f(cx + 5, cy + 5)
        glVertex2f(cx - 5, cy + 5)
        glEnd()

    # Radar
    radar_x, radar_y = WINDOW_WIDTH - 120, 120
    radar_size = 100
    glColor4f(0.0, 0.2, 0.0, 0.5)
    glBegin(GL_POLYGON)
    for i in range(32):
        ang = i * (2 * math.pi / 32)
        glVertex2f(radar_x + radar_size * math.cos(ang), radar_y + radar_size * math.sin(ang))
    glEnd()
    glColor3f(0.0, 1.0, 0.0)
    glBegin(GL_LINE_LOOP)
    for i in range(32):
        ang = i * (2 * math.pi / 32)
        glVertex2f(radar_x + radar_size * math.cos(ang), radar_y + radar_size * math.sin(ang))
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(radar_x - radar_size, radar_y)
    glVertex2f(radar_x + radar_size, radar_y)
    glVertex2f(radar_x, radar_y - radar_size)
    glVertex2f(radar_x, radar_y + radar_size)
    glEnd()

    glPointSize(5.0)
    glBegin(GL_POINTS)
    radar_range = 3000.0
    for e in enemies:
        dx = e[0] - player_x
        dy = e[1] - player_y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < radar_range:
            rad = _rad(player_angle)
            rx = (dx * math.cos(rad) + dy * math.sin(rad)) / radar_range * radar_size
            ry = (-dx * math.sin(rad) + dy * math.cos(rad)) / radar_range * radar_size
            
            d_radar = math.sqrt(rx*rx + ry*ry)
            if d_radar > radar_size:
                rx *= (radar_size / d_radar)
                ry *= (radar_size / d_radar)
            
            glColor3f(1.0, 0.0, 0.0)
            glVertex2f(radar_x + rx, radar_y + ry)
    glEnd()
    
    if boss_active:
        dx = boss_x - player_x
        dy = boss_y - player_y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < radar_range:
            rad = _rad(player_angle)
            rx = (dx * math.cos(rad) + dy * math.sin(rad)) / radar_range * radar_size
            ry = (-dx * math.sin(rad) + dy * math.cos(rad)) / radar_range * radar_size
            
            d_radar = math.sqrt(rx*rx + ry*ry)
            if d_radar > radar_size:
                rx *= (radar_size / d_radar)
                ry *= (radar_size / d_radar)
            
            glPointSize(10.0)
            glBegin(GL_POINTS)
            glColor3f(1.0, 0.0, 1.0)
            glVertex2f(radar_x + rx, radar_y + ry)
            glEnd()
            glPointSize(5.0)

    glBegin(GL_POINTS)
    glColor3f(0.0, 1.0, 1.0)
    glVertex2f(radar_x, radar_y)
    glEnd()

    # Boss Health Bar 
    if boss_active:
        bar_width = 800
        bar_height = 25
        start_x = (WINDOW_WIDTH - bar_width) // 2
        start_y = WINDOW_HEIGHT - 60
        
        # Background shadow
        glColor4f(0.0, 0.0, 0.0, 0.8)
        glBegin(GL_QUADS)
        glVertex2f(start_x - 3, start_y - 3)
        glVertex2f(start_x + bar_width + 3, start_y - 3)
        glVertex2f(start_x + bar_width + 3, start_y + bar_height + 3)
        glVertex2f(start_x - 3, start_y + bar_height + 3)
        glEnd()
        
        # Dark background
        glColor3f(0.2, 0.2, 0.2)
        glBegin(GL_QUADS)
        glVertex2f(start_x, start_y)
        glVertex2f(start_x + bar_width, start_y)
        glVertex2f(start_x + bar_width, start_y + bar_height)
        glVertex2f(start_x, start_y + bar_height)
        glEnd()
        
        # Health bar fill
        hp_ratio = max(0, boss_hp / boss_max_hp)
        if hp_ratio < 0.3:
            # Flashing red when low
            glColor3f(1.0, 0.1 + 0.2 * abs(math.sin(storm_turbulence_offset * 5)), 0.0)
        elif hp_ratio < 0.6:
            # Yellow for medium
            glColor3f(1.0, 0.8, 0.0)
        else:
            # Green for high
            glColor3f(0.0, 1.0, 0.0)
        
        glBegin(GL_QUADS)
        glVertex2f(start_x + 2, start_y + 2)
        glVertex2f(start_x + bar_width * hp_ratio - 2, start_y + 2)
        glVertex2f(start_x + bar_width * hp_ratio - 2, start_y + bar_height - 2)
        glVertex2f(start_x + 2, start_y + bar_height - 2)
        glEnd()
        
        # Border
        glColor3f(1.0, 1.0, 1.0)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(start_x, start_y)
        glVertex2f(start_x + bar_width, start_y)
        glVertex2f(start_x + bar_width, start_y + bar_height)
        glVertex2f(start_x, start_y + bar_height)
        glEnd()
        glLineWidth(1.0)
        
        # Boss label above bar
        glColor3f(1.0, 0.0, 0.0)
        draw_text(WINDOW_WIDTH // 2 - 50, start_y + bar_height + 5, "BOSS", GLUT_BITMAP_HELVETICA_18)
        
        # HP text on bar
        glColor3f(1.0, 1.0, 1.0)
        hp_text = f"HP: {int(boss_hp)} / {boss_max_hp}"
        draw_text(WINDOW_WIDTH // 2 - 40, start_y + 5, hp_text, GLUT_BITMAP_HELVETICA_12)

    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def fire_bullet(ignore_heat=False): 
    global weapon_heat, overheated
    if overheated and not ignore_heat:
        return

    fdx, fdy = _fwd(player_angle) 
    mx = player_x + fdx * 130 
    my = player_y + fdy * 130 
    mz = player_z
    fdz = math.sin(_rad(player_pitch))
    bullets.append([mx, my, mz, fdx * BULLET_SPEED, fdy * BULLET_SPEED, fdz * BULLET_SPEED]) 
    
    if not ignore_heat:
        actual_heat = HEAT_PER_SHOT * 0.3 if boss_active else HEAT_PER_SHOT
        weapon_heat += actual_heat
        if weapon_heat >= MAX_HEAT:
            overheated = True

def fire_missiles():
    global missiles_available
    if missiles_available > 0:
        fdx, fdy = _fwd(player_angle)
        right_x, right_y = fdy, -fdx
        
        for i in range(3):
            offset_mag = 0
            if i == 1: offset_mag = -80
            elif i == 2: offset_mag = 80
            
            mx = player_x + right_x * offset_mag
            my = player_y + right_y * offset_mag
            mz = player_z
            
            if boss_active:
                target = [boss_x, boss_y, boss_z, 1.0, 0]
            else:
                if not enemies:
                    continue
                sorted_enemies = sorted(enemies, key=lambda e: _dist3d(player_x, player_y, player_z, e[0], e[1], e[2]))
                target = sorted_enemies[i % len(sorted_enemies)]
                
            missiles.append([mx, my, mz, target, False])
            
        missiles_available -= 1

def update_bullets(): 
    global game_score, cheat_locked, combo_count, missiles_available, total_kills, boss_hp, boss_active, boss_x, boss_y, boss_z, boss_hit_flash, game_victory, boss_hits
    alive = [] 
    for b in bullets: 
        b[0] += b[3] 
        b[1] += b[4] 
        b[2] += b[5] 
        if _dist3d(b[0], b[1], b[2], player_x, player_y, player_z) > 2000: 
            cheat_locked = False 
            continue 
        hit = False 

        if boss_active:
            dist_to_boss = _dist3d(b[0], b[1], b[2], boss_x, boss_y, boss_z)
            if dist_to_boss < 60:
                damage = 40 if cheat_mode else 25
                boss_hp -= damage
                boss_hit_flash = 5
                
                boss_hits += 1
                if boss_hits == 10 or boss_hits == 25 or boss_hits == 45:
                    missiles_available += 2

                if boss_hp <= 0:
                    boss_hp = 0
                    boss_active = False
                    game_victory = True
                    total_kills = 0 
                _spawn_explosion(b[0], b[1], b[2])
                hit = True

        if not hit:
            for i, e in enumerate(enemies): 
                hit_multiplier = 3.0 if cheat_mode else 1.5
                threshold = ENEMY_BASE_R * e[3] * hit_multiplier 
                if _dist3d(b[0], b[1], b[2], e[0], e[1], e[2]) < threshold: 
                    combo_count += 1
                    game_score += 1 
                    total_kills += 1
                    
                    if combo_count >= 5:
                        missiles_available += 1
                        combo_count = 0
                    _spawn_explosion(e[0], e[1], e[2])
                    enemies[i] = _spawn_enemy() 
                    cheat_locked = False 
                    hit = True 
                    break 
        if not hit: 
            alive.append(b) 
    bullets.clear() 
    bullets.extend(alive) 

def update_missiles():
    global game_score, total_kills, boss_hp, boss_active, boss_x, boss_y, boss_z, boss_hit_flash, game_victory, boss_hits, missiles_available
    alive = []
    
    for m in missiles:
        if len(m) < 5:
            m.append(False)
            
        if boss_active:
            m[3] = [boss_x, boss_y, boss_z, 1.0, 0]

        if not boss_active and m[3] not in enemies:
            if enemies:
                best_d = float('inf')
                new_target = enemies[0]
                for e in enemies:
                    d = _dist3d(m[0], m[1], m[2], e[0], e[1], e[2])
                    if d < best_d:
                        best_d = d
                        new_target = e
                m[3] = new_target
            else:
                _spawn_explosion(m[0], m[1], m[2])
                continue

        tx, ty, tz, _, _ = m[3]
        dx = tx - m[0]
        dy = ty - m[1]
        dz = tz - m[2]
        d = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        if d < 300 and not m[4]: 
            if boss_active:
                boss_dist = _dist3d(m[0], m[1], m[2], boss_x, boss_y, boss_z)
                if boss_dist < 100:
                    m[4] = True
                    _spawn_explosion(boss_x, boss_y, boss_z)
                    boss_hp -= 200
                    boss_hit_flash = 10
                    
                    boss_hits += 1
                    if boss_hits == 10 or boss_hits == 25 or boss_hits == 45:
                        missiles_available += 2

                    if boss_hp <= 0:
                        boss_hp = 0
                        boss_active = False
                        game_victory = True
                        total_kills = 0
                else:
                    _spawn_explosion(m[0], m[1], m[2])
                    continue
            else:
                m[4] = True
                _spawn_explosion(tx, ty, tz)
                game_score += 1
                total_kills += 1
                if m[3] in enemies:
                    enemies[enemies.index(m[3])] = _spawn_enemy()
            continue
        elif d < 300 and m[4]:
            continue
        else:
            m[0] += (dx/d) * MISSILE_SPEED
            m[1] += (dy/d) * MISSILE_SPEED
            m[2] += (dz/d) * MISSILE_SPEED
            alive.append(m)
            
    missiles.clear()
    missiles.extend(alive)

def update_explosions():
    global explosions
    alive = []
    for p in explosions:
        p[0] += p[3]
        p[1] += p[4]
        p[2] += p[5]
        p[6] -= 1
        if p[6] > 0:
            alive.append(p)
    explosions = alive

def check_planet_collisions():
    global player_life, enemy_hit_cooldown, screen_shake_time, player_x, player_y, player_z
    
    for planet in planets:
        dist = _dist3d(player_x, player_y, player_z, planet[0], planet[1], planet[2])
        if dist < planet[3] + 50:
            if enemy_hit_cooldown == 0:
                player_life -= 1
                enemy_hit_cooldown = HIT_COOLDOWN_MAX
                screen_shake_time = 30
                dx = player_x - planet[0]
                dy = player_y - planet[1]
                dz = player_z - planet[2]
                dist_norm = math.sqrt(dx*dx + dy*dy + dz*dz)
                if dist_norm > 0:
                    push_dist = planet[3] + 100
                    player_x = planet[0] + (dx/dist_norm) * push_dist
                    player_y = planet[1] + (dy/dist_norm) * push_dist
                    player_z = planet[2] + (dz/dist_norm) * push_dist
            break

def update_enemies(): 
    global player_life, enemy_hit_cooldown, screen_shake_time, combo_count
    global total_kills, boss_active, boss_hp, boss_x, boss_y, boss_z, boss_shoot_timer, boss_fire_timer, boss_bullets
    
    if enemy_hit_cooldown > 0: 
        enemy_hit_cooldown -= 1 

    if not boss_active and total_kills >= 20:
        boss_active = True
        player_life += 10
        boss_hp = boss_max_hp
        boss_x, boss_y, boss_z = player_x, player_y + 2500, player_z
        enemies.clear()
        boss_bullets = []
        boss_shoot_timer = 0
        boss_fire_timer = 0

    if boss_active:
        dx = player_x - boss_x
        dy = player_y - boss_y
        dz = player_z - boss_z
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        if dist > 1500:
            speed = (ENEMY_SPEED * 1.5)
            boss_x += (dx/dist) * speed
            boss_y += (dy/dist) * speed
            boss_z += (dz/dist) * speed
        elif dist < 800:
            speed = (ENEMY_SPEED * 2.0)
            boss_x -= (dx/dist) * speed
            boss_y -= (dy/dist) * speed
            boss_z -= (dz/dist) * speed
        
        shoot_delay = 150 if cheat_mode else 90
        boss_shoot_timer += 1
        boss_fire_timer += 1 
        
        if boss_shoot_timer >= shoot_delay:
            boss_shoot_timer = 0
            is_fire = False
            if boss_fire_timer >= 600:
                is_fire = True
                boss_fire_timer = 0
            
            bx_dir = (player_x - boss_x) / dist
            by_dir = (player_y - boss_y) / dist
            bz_dir = (player_z - boss_z) / dist
            
            boss_bullets.append([boss_x, boss_y, boss_z, 
                                 bx_dir * BOSS_BULLET_SPEED, 
                                 by_dir * BOSS_BULLET_SPEED, 
                                 bz_dir * BOSS_BULLET_SPEED, 
                                 is_fire])

        alive_bb = []
        for bb in boss_bullets:
            bb[0] += bb[3]
            bb[1] += bb[4]
            bb[2] += bb[5]
            
            hit_r = 80 if bb[6] else 35
            if _dist3d(bb[0], bb[1], bb[2], player_x, player_y, player_z) < hit_r:
                if enemy_hit_cooldown == 0:
                    player_life -= 1
                    enemy_hit_cooldown = HIT_COOLDOWN_MAX
                    screen_shake_time = 25 if bb[6] else 10
                continue
            
            if _dist3d(bb[0], bb[1], bb[2], boss_x, boss_y, boss_z) < 4000:
                alive_bb.append(bb)
        boss_bullets = alive_bb

        if dist < 500:
            if enemy_hit_cooldown == 0:
                player_life -= 1
                enemy_hit_cooldown = HIT_COOLDOWN_MAX
                screen_shake_time = 30
        
        return

    fdx, fdy = _fwd(player_angle)
    predict_x = player_x + fdx * MOVE_SPEED * 8
    predict_y = player_y + fdy * MOVE_SPEED * 8
    predict_z = player_z

    for e in enemies: 
        dx = predict_x - e[0] 
        dy = predict_y - e[1] 
        dz = predict_z - e[2]
        d = math.sqrt(dx * dx + dy * dy + dz * dz) 
        if d > 1: 
            speed = (ENEMY_SPEED * 0.5) + (game_score * 0.01)
            e[0] += (dx / d) * speed 
            e[1] += (dy / d) * speed 
            e[2] += (dz / d) * speed 
        e[3] += e[4] 
        if e[3] >= ENEMY_MAX_SCALE or e[3] <= ENEMY_MIN_SCALE: 
            e[4] *= -1 
        
        if _dist3d(e[0], e[1], e[2], player_x, player_y, player_z) < ENEMY_BASE_R * e[3] + 80:
            if enemy_hit_cooldown == 0:
                player_life -= 1 
                enemy_hit_cooldown = HIT_COOLDOWN_MAX 
                screen_shake_time = 20 
                combo_count = 0 
                enemies[enemies.index(e)] = _spawn_enemy()

def _nearest_enemy_bearing(): 
    global boss_active, boss_x, boss_y, boss_z
    best_d = float('inf') 
    best_deg = 0.0 
    best_dz = 0.0
    
    targets = enemies if not boss_active else [[boss_x, boss_y, boss_z, 1.0, 0]]
    
    for e in targets: 
        dist = _dist3d(player_x, player_y, player_z, e[0], e[1], e[2])
        
        if boss_active:
            future_x, future_y, future_z = e[0], e[1], e[2]
        else:
            travel_time = dist / BULLET_SPEED
            speed = (ENEMY_SPEED * 0.5) + (game_score * 0.01)
            dx_to_p = player_x - e[0]
            dy_to_p = player_y - e[1]
            dz_to_p = player_z - e[2]
            d_to_p = math.sqrt(dx_to_p**2 + dy_to_p**2 + dz_to_p**2 + 0.1)
            
            future_x = e[0] + (dx_to_p / d_to_p) * speed * travel_time * 0.5
            future_y = e[1] + (dy_to_p / d_to_p) * speed * travel_time * 0.5
            future_z = e[2] + (dz_to_p / d_to_p) * speed * travel_time * 0.5

        if dist < best_d: 
            best_d = dist 
            best_deg = math.degrees(math.atan2(-(future_x - player_x), future_y - player_y)) % 360 
            best_dz = future_z - player_z
    return best_d, best_deg, best_dz

def keyboardListener(key, x, y): 
    global cheat_mode, cheat_vision, cheat_locked, game_over, game_paused, space_storm_active, first_person, fp_look_angle
    global shift_pressed
    
    modifiers = glutGetModifiers()
    shift_pressed = (modifiers & GLUT_ACTIVE_SHIFT) != 0
    
    if key == b'r': 
        init_game() 
        glutPostRedisplay() 
        return 
    
    if key == b'p' or key == b'P':
        if not game_over:
            game_paused = not game_paused
        glutPostRedisplay()
        return

    if key == b'x' or key == b'X':
        fire_missiles()
        glutPostRedisplay()
        return

    if game_over or game_paused: 
        return 
    
    keys_pressed[key] = True

    if key == b'c': 
        cheat_mode = not cheat_mode 
        if not cheat_mode: 
            cheat_vision = False 
            cheat_locked = False 
    elif key == b'v': 
        if cheat_mode: 
            cheat_vision = not cheat_vision 
    elif key == b'm' or key == b'M':
        space_storm_active = not space_storm_active
    glutPostRedisplay() 

def keyboardUpListener(key, x, y):
    global shift_pressed
    keys_pressed[key] = False
    modifiers = glutGetModifiers()
    shift_pressed = (modifiers & GLUT_ACTIVE_SHIFT) != 0
    glutPostRedisplay()

def specialKeyListener(key, x, y): 
    global camera_angle, camera_height, shift_pressed
    
    modifiers = glutGetModifiers()
    shift_pressed = (modifiers & GLUT_ACTIVE_SHIFT) != 0
    
    if key == GLUT_KEY_UP: 
        camera_height += 20 
    elif key == GLUT_KEY_DOWN: 
        camera_height = max(-200, camera_height - 20) 
    elif key == GLUT_KEY_LEFT: 
        camera_angle = (camera_angle - 5) % 360 
    elif key == GLUT_KEY_RIGHT: 
        camera_angle = (camera_angle + 5) % 360 
    glutPostRedisplay()

def specialKeyUpListener(key, x, y):
    global shift_pressed
    modifiers = glutGetModifiers()
    shift_pressed = (modifiers & GLUT_ACTIVE_SHIFT) != 0
    glutPostRedisplay()

def mouseListener(button, state, x, y): 
    global first_person, fp_look_angle 
    if game_over or game_paused: 
        return 
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN: 
        fire_bullet() 
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN: 
        first_person = not first_person 
        fp_look_angle = player_angle 
    glutPostRedisplay() 

def idle(): 
    global game_over, game_paused, player_angle, player_pitch, player_roll, player_z, player_x, player_y, fp_look_angle, cheat_locked
    global weapon_heat, overheated, combo_count
    global space_storm_active, storm_turbulence_offset
    global boss_active, boss_bullets, boss_x, boss_y, boss_z, boss_hit_flash, game_victory
    global planet_rotation, cheat_fire_cooldown
    global boost_amount, is_boosting, boost_regen_timer, shift_pressed
    global player_life
    
    if game_over or game_paused or game_victory: 
        glutPostRedisplay() 
        return 
    
    if boss_hit_flash > 0:
        boss_hit_flash -= 1
    
    if cheat_mode and player_life < 10:
        player_life = 10

    fdx, fdy = _fwd(player_angle)
    
    movement_keys_pressed = (keys_pressed.get(b'w') or keys_pressed.get(b'W') or
                            keys_pressed.get(b's') or keys_pressed.get(b'S') or
                            keys_pressed.get(b'a') or keys_pressed.get(b'A') or
                            keys_pressed.get(b'd') or keys_pressed.get(b'D') or
                            keys_pressed.get(b'q') or keys_pressed.get(b'Q') or
                            keys_pressed.get(b'e') or keys_pressed.get(b'E'))
    
    is_boosting = shift_pressed and movement_keys_pressed and boost_amount > 0
    
    if is_boosting and boost_amount > 0:
        current_move_speed = MOVE_SPEED * BOOST_MULTIPLIER
        current_vertical_speed = VERTICAL_SPEED * BOOST_MULTIPLIER
        boost_amount = max(0, boost_amount - BOOST_CONSUMPTION_RATE)
        boost_regen_timer = BOOST_REGEN_DELAY
    else:
        current_move_speed = MOVE_SPEED * 2.0 if cheat_mode else MOVE_SPEED
        current_vertical_speed = VERTICAL_SPEED * 1.5 if cheat_mode else VERTICAL_SPEED
        
        if boost_amount < MAX_BOOST:
            if boost_regen_timer > 0:
                boost_regen_timer -= 1
            else:
                boost_amount = min(MAX_BOOST, boost_amount + BOOST_REGEN_RATE)
    
    current_rotate_speed = ROTATE_SPEED if not cheat_mode else CHEAT_ROTATE_STEP

    if keys_pressed.get(b'w') or keys_pressed.get(b'W'):
        player_x += fdx * current_move_speed
        player_y += fdy * current_move_speed
    if keys_pressed.get(b's') or keys_pressed.get(b'S'):
        player_x -= fdx * current_move_speed
        player_y -= fdy * current_move_speed
    if (keys_pressed.get(b'a') or keys_pressed.get(b'A')) and not cheat_mode:
        player_angle = (player_angle + current_rotate_speed) % 360
        fp_look_angle = player_angle
        player_roll = min(player_roll + 2.5, 30.0)
    if (keys_pressed.get(b'd') or keys_pressed.get(b'D')) and not cheat_mode:
        player_angle = (player_angle - current_rotate_speed) % 360
        fp_look_angle = player_angle
        player_roll = max(player_roll - 2.5, -30.0)
    if keys_pressed.get(b'q') or keys_pressed.get(b'Q'):
        player_z += current_vertical_speed
        player_pitch = min(player_pitch + 2.0, 25.0)
    if keys_pressed.get(b'e') or keys_pressed.get(b'E'):
        player_z -= current_vertical_speed
        player_pitch = max(player_pitch - 2.0, -25.0)

    if player_pitch > 0:
        player_pitch = max(0, player_pitch - 0.5)
    elif player_pitch < 0:
        player_pitch = min(0, player_pitch + 0.5)
    
    if player_roll > 0:
        player_roll = max(0, player_roll - 1.0)
    elif player_roll < 0:
        player_roll = min(0, player_roll + 1.0)
    
    if space_storm_active:
        storm_turbulence_offset += 0.2
        turbulence_x = math.sin(storm_turbulence_offset) * 3.0
        turbulence_z = math.cos(storm_turbulence_offset * 0.7) * 2.0
        player_x += turbulence_x
        player_z += turbulence_z

    for s in stars:
        for i in range(3):
            pos = [player_x, player_y, player_z][i]
            if s[i] < pos - STARS_RANGE: 
                s[i] += 2 * STARS_RANGE
            if s[i] > pos + STARS_RANGE: 
                s[i] -= 2 * STARS_RANGE

    for planet in planets:
        for i in range(3):
            pos = [player_x, player_y, player_z][i]
            if planet[i] < pos - STARS_RANGE * 2: 
                planet[i] += 4 * STARS_RANGE
            if planet[i] > pos + STARS_RANGE * 2: 
                planet[i] -= 4 * STARS_RANGE
    
    planet_rotation += 0.1
    
    decay_mult = 3.0 if boss_active else 1.0
    if weapon_heat > 0:
        weapon_heat -= HEAT_DECAY * decay_mult
    else:
        weapon_heat = 0
        overheated = False
    
    update_bullets() 
    update_missiles()
    update_enemies() 
    update_explosions()
    
    check_planet_collisions()

    if player_life <= 0: 
        game_over = True 
        first_person = False 
        glutPostRedisplay() 
        return 

    if cheat_mode: 
        if cheat_fire_cooldown > 0:
            cheat_fire_cooldown -= 1
            
        dist, target_deg, dz = _nearest_enemy_bearing() 
        diff = _angle_diff(player_angle, target_deg) 
        
        rotate_speed_cheat = CHEAT_ROTATE_STEP * 1.5
        step = min(rotate_speed_cheat, abs(diff)) * (1 if diff >= 0 else -1) 
        player_angle = (player_angle + step) % 360 
        fdx, fdy = _fwd(player_angle)

        approach_dist = 800 if boss_active else 400
        safe_dist = 600 if boss_active else 300

        if dist > approach_dist:
            player_x += fdx * current_move_speed
            player_y += fdy * current_move_speed
        elif dist < safe_dist:
            player_x -= fdx * current_move_speed * 0.5
            player_y -= fdy * current_move_speed * 0.5

        if boss_active:
            for bb in boss_bullets:
                d_to_b = _dist3d(player_x, player_y, player_z, bb[0], bb[1], bb[2])
                if d_to_b < 600:
                    side_x, side_y = fdy, -fdx
                    strafe_dir = 1.0 if (int(storm_turbulence_offset * 10) % 40 < 20) else -1.0
                    dodge_speed = current_move_speed * 2.0
                    
                    player_x += side_x * dodge_speed * strafe_dir
                    player_y += side_y * dodge_speed * strafe_dir
                    player_z += current_vertical_speed * strafe_dir
                    player_roll = 30.0 * strafe_dir
                    break

        if abs(dz) > 10:
            v_speed_boost = VERTICAL_SPEED * 1.5
            v_step = min(v_speed_boost, abs(dz)) * (1 if dz > 0 else -1)
            player_z += v_step
            target_pitch = max(-25.0, min(25.0, dz / 15.0))
            player_pitch = player_pitch * 0.8 + target_pitch * 0.2

        aim_tol = CHEAT_AIM_TOL * 3.0 if boss_active else CHEAT_AIM_TOL
        dz_tol = 200 if boss_active else 40

        fire_cooldown = CHEAT_FIRE_COOLDOWN_MAX if boss_active else CHEAT_FIRE_COOLDOWN_MAX
        
        if abs(diff) <= aim_tol and abs(dz) < dz_tol and cheat_fire_cooldown <= 0: 
            fire_bullet(ignore_heat=True)
            cheat_fire_cooldown = fire_cooldown
            cheat_locked = True 
        else: 
            if abs(diff) > aim_tol or abs(dz) >= dz_tol:
                cheat_locked = False 
    glutPostRedisplay() 

def showScreen(): 
    if space_storm_active:
        glClearColor(0.1, 0.05, 0.15, 1.0)
    else:
        glClearColor(0.0, 0.0, 0.0, 1.0)
        
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 
    glEnable(GL_DEPTH_TEST) 
    
    if space_storm_active:
        glEnable(GL_FOG)
        glFogfv(GL_FOG_COLOR, (0.4, 0.2, 0.6, 1.0))
        glFogi(GL_FOG_MODE, GL_EXP2)
        glFogf(GL_FOG_DENSITY, 0.001)
    else:
        glDisable(GL_FOG)

    glLoadIdentity() 
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT) 
    setupCamera() 
    draw_environment() 
    draw_player() 
    for e in enemies: 
        draw_enemy(e[0], e[1], e[2], e[3]) 
    for b in bullets: 
        draw_bullet(b[0], b[1], b[2]) 
    for m in missiles:
        draw_missile(m[0], m[1], m[2])
    
    if boss_active:
        draw_boss()
        for bb in boss_bullets:
            draw_boss_bullet(bb[0], bb[1], bb[2], bb[6])

    draw_explosions()
    draw_hud()
    
    glColor3f(1.0, 1.0, 1.0)
    draw_text(10, WINDOW_HEIGHT - 30, f"Life: {player_life}   Score: {game_score}   Kills: {total_kills}")
    
    if missiles_available > 0:
        glColor3f(1.0, 1.0, 0.0)
        draw_text(10, WINDOW_HEIGHT - 58, f"Missiles: {missiles_available}")
    glColor3f(1.0, 1.0, 1.0)
    
    draw_text(10, WINDOW_HEIGHT - 86, f"Heat: {int(weapon_heat)}% {'[OVERHEATED]' if overheated else ''}")
    
    if combo_count > 1:
        draw_text(WINDOW_WIDTH - 150, WINDOW_HEIGHT - 30, f"COMBO x{combo_count}!", GLUT_BITMAP_HELVETICA_18)
    
    cam_lbl = "FPV" if first_person else "Orbit" 
    cheat_lbl = "Auto-Pilot: ON" if cheat_mode else "Manual" 
    draw_text(10, WINDOW_HEIGHT - 120, f"Camera: {cam_lbl}   Mode: {cheat_lbl}   Storm (M): {'ON' if space_storm_active else 'OFF'}") 
    draw_text(10, WINDOW_HEIGHT - 145, "Controls: W/S/A/D/Q/E (Move), SHIFT+Move (Boost), Left Click (Fire), Right Click (View)")
    draw_text(10, WINDOW_HEIGHT - 170, "P (Pause), R (Restart), X (Missile), C (Cheat Mode), M (Space Storm)")

    if space_storm_active:
        draw_text(WINDOW_WIDTH // 2 - 80, WINDOW_HEIGHT - 30, "SPACE STORM ACTIVE", GLUT_BITMAP_HELVETICA_18)

    if game_paused:
        draw_text(WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT // 2 + 10, "PAUSED", GLUT_BITMAP_TIMES_ROMAN_24)

    if game_victory:
        glColor3f(0.0, 1.0, 0.0)
        draw_text(WINDOW_WIDTH // 2 - 200, WINDOW_HEIGHT // 2 + 10, 
                   "BOSS DEFEATED - SYSTEM SECURED!", 
                   GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(WINDOW_WIDTH // 2 - 130, WINDOW_HEIGHT // 2 - 30, 
                   "Press R to play again", 
                   GLUT_BITMAP_HELVETICA_18)

    if game_over: 
        glColor3f(1.0, 0.0, 0.0)
        draw_text(WINDOW_WIDTH // 2 - 210, WINDOW_HEIGHT // 2 + 10, 
                   "MISSION FAILED  -  Press R to retry", 
                   GLUT_BITMAP_TIMES_ROMAN_24) 
    glutSwapBuffers() 

def timer(v):
    idle()
    glutTimerFunc(1000 // FPS, timer, 0)

def reshape(w, h):
    global WINDOW_WIDTH, WINDOW_HEIGHT
    WINDOW_WIDTH = w
    WINDOW_HEIGHT = h
    glViewport(0, 0, w, h)
    setupCamera()

def main(): 
    init_game() 
    glutInit() 
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH) 
    
    glutInitWindowSize(1920, 1080) 
    glutInitWindowPosition(0, 0) 
    glutCreateWindow(b"Space Shooter - Complete Edition") 
    glutFullScreen()
    
    glutDisplayFunc(showScreen) 
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboardListener) 
    glutKeyboardUpFunc(keyboardUpListener)
    glutSpecialFunc(specialKeyListener) 
    glutSpecialUpFunc(specialKeyUpListener)
    glutMouseFunc(mouseListener) 
    glutTimerFunc(0, timer, 0) 
    glutMainLoop() 

if __name__ == "__main__": 
    main()