from ursina import *
import random
import time

app = Ursina()

# B3313 Inspired Settings: low-poly, vibrant, slightly distorted, aliased
window.fullscreen = True
window.color = color.black  # Dark, potentially glitchy background
application.development_mode = False  # Hide FPS counter

# Player tracking data
player_data = {
    "moves": 0,
    "jumps": 0,
    "stars_collected": {"yellow": 0, "red": 0, "green": 0},
    "time_spent": 0,
    "glitches_encountered": 0
}

# Player with B3313-inspired movement (crisp, slightly off, with potential for glitches)
class B3313Player(Entity):
    def __init__(self):
        super().__init__()
        self.speed = 11  # Slightly faster, maybe with occasional speedups
        self.jump_height = 2.7  # Higher, potentially floatier jumps
        self.jump_duration = 0.35  # Even shorter, snappier jumps
        self.jumping = False
        self.gravity = 1.3  # Slightly heavier, but maybe with inconsistent pull
        self.velocity_y = 0
        self.grounded = False
        self.triple_jump_counter = 0
        self.triple_jump_cooldown = 0.7

        self.model = 'cube'  # Keep the low-poly look
        self.scale = (0.7, 1.7, 0.7)  # Slightly different proportions
        self.color = color.rgb(255, 215, 0)  # A more golden-yellow, perhaps hinting at stars
        self.collider = BoxCollider(self, center=(0, 0.85, 0), size=(0.7, 1.7, 0.7))
        camera.parent = self
        camera.position = (0, 1.3, -1) # Closer camera, slightly behind
        camera.fov = 75  # Slightly wider FOV for a different perspective

    def update(self):
        player_data["time_spent"] += time.dt
        direction = Vec3(held_keys['d'] - held_keys['a'], 0, held_keys['w'] - held_keys['s']).normalized()
        if direction.length() > 0:
            player_data["moves"] += 1
            self.position += direction * self.speed * time.dt
            self.rotation_y = lerp(self.rotation_y, -direction.x * 35 + random.uniform(-5, 5), 0.15)  # Snappy turn with a hint of instability

        self.velocity_y -= self.gravity * time.dt
        if held_keys['space'] and self.grounded and not self.jumping and self.triple_jump_cooldown <= 0:
            self.jumping = True
            player_data["jumps"] += 1
            self.triple_jump_counter += 1
            self.velocity_y = self.jump_height * (1 + 0.25 * min(self.triple_jump_counter - 1, 2)) + random.uniform(-0.3, 0.3) # Inconsistent jump height
            if self.triple_jump_counter >= 3:
                self.triple_jump_counter = 0
                self.triple_jump_cooldown = 0.7
            invoke(self.reset_jump, delay=self.jump_duration)

        self.y += self.velocity_y * time.dt
        hit_info = raycast(self.position + Vec3(0, 0.1, 0), Vec3(0, -1, 0), distance=0.55)
        if hit_info.hit:
            self.grounded = True
            self.y = hit_info.world_point.y
            self.velocity_y = max(self.velocity_y, 0)
        else:
            self.grounded = False
            if not self.jumping and self.velocity_y < -5 and random.random() < 0.01: # Small chance of a sudden drop
                self.y -= 0.5
                player_data["glitches_encountered"] += 1

        if self.triple_jump_cooldown > 0:
            self.triple_jump_cooldown -= time.dt

    def reset_jump(self):
        self.jumping = False

# B3313-style star (faceted, vibrant, possibly with a slight visual anomaly)
class Star(Entity):
    def __init__(self, position, star_type):
        super().__init__(
            model='sphere',  # Faceted look is key
            scale=0.5, # Slightly smaller
            position=position,
            color={'yellow': color.rgb(255, 255, 100), 'red': color.rgb(255, 50, 50), 'green': color.rgb(50, 255, 50)}[star_type], # Adjusted colors
            collider='sphere'
        )
        self.star_type = star_type
        self.y_offset = random.random()
        self.rotation_speed = random.uniform(45, 75) # Variable spin speed
        self.scale_factor = 1
        self.scale_direction = 0.01

        self.model = Mesh(vertices=self.model.vertices[::3], mode='triangle')  # More aggressive decimation for more aliasing

    def update(self):
        self.rotation_y += self.rotation_speed * time.dt
        self.y = self.position.y + math.sin(time.time() * 4 + self.y_offset) * 0.25 # Slightly faster bobbing

        self.scale_factor += self.scale_direction
        if self.scale_factor > 1.1 or self.scale_factor < 0.9:
            self.scale_direction *= -1
        self.scale = 0.5 * self.scale_factor

        if distance(player.position, self.position) < 1.5: # Slightly smaller pickup radius
            player_data["stars_collected"][self.star_type] += 1
            destroy(self)

# B3313 block (sharp edges, possibly misaligned textures or flickering colors)
class Block(Entity):
    def __init__(self, position):
        hue = (player_data["moves"] + player_data["jumps"]) % 360
        super().__init__(
            model='cube',
            position=position,
            color=color.hsv(hue, 0.9, 0.7 + random.uniform(-0.1, 0.1)),  # High saturation, slightly darker with color variations
            collider='box',
            scale=(1.05, 1.05, 1.05) # Slightly smaller blocks
        )
        if random.random() < 0.05: # Small chance of a block being slightly offset or scaled differently
            self.position += Vec3(random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1))
            self.scale += random.uniform(-0.05, 0.05)

# Level generation with B3313-inspired unpredictability
def create_level():
    random.seed(time.time() + player_data["moves"] + player_data["jumps"] + player_data["glitches_encountered"]) # Incorporate glitches into seed
    for z in range(-18, 18): # Slightly larger area
        for x in range(-18, 18):
            Block(position=(x, 0, z))

    platforms = int(player_data["time_spent"] * 2.5) % 12 + 4  # More frequent, varied platforms
    for _ in range(platforms):
        x, z = random.randint(-15, 15), random.randint(-15, 15)
        height = random.randint(1, 7 + int(player_data["jumps"] / 20))
        for y in range(1, height + 1):
            Block(position=(x + random.uniform(-0.2, 0.2), y + random.uniform(-0.1, 0.1), z + random.uniform(-0.2, 0.2))) # Slightly jumbled platforms

    stars = [(450, 'yellow'), (14, 'red'), (14, 'green')] # Slightly more stars
    for count, star_type in stars:
        for _ in range(count):
            x, z = random.randint(-15, 15), random.randint(-15, 15)
            y = random.randint(1, 15 + int(player_data["stars_collected"]["yellow"] / 120))
            Star(position=(x + random.uniform(-0.3, 0.3), y + random.uniform(-0.3, 0.3), z + random.uniform(-0.3, 0.3)), star_type=star_type) # Slightly more spread out

# B3313 skybox (simple, bold color that might shift abruptly)
class Sky(Entity):
    def __init__(self):
        super().__init__(
            model='sphere',
            scale=280, # Slightly smaller
            color=color.hsv((player_data["time_spent"] * 2) % 360, 0.8, 0.8 + random.uniform(-0.2, 0.2)), # Faster hue shift with brightness variation
            double_sided=True,
            segments=6  # Even lower resolution
        )

    def update(self):
        self.color = color.hsv((player_data["time_spent"] * 2) % 360 + random.uniform(-10, 10), 0.8, 0.8 + random.uniform(-0.2, 0.2)) # Subtle random hue shift

# HUD with potentially glitched or stylized text
class StarCounter(Text):
    def __init__(self):
        super().__init__(
            text="Y:0 | R:0 | G:0",
            position=(-0.85, 0.45), # Adjusted position
            scale=1.6, # Slightly larger
            font='VeraMono', # A more retro font
            color=color.rgb(100, 255, 200) # Another SGI-esque color
        )

    def update(self):
        s = player_data["stars_collected"]
        self.text = f"Y:{s['yellow']} | R:{s['red']} | G:{s['green']}"
        if sum(s.values()) >= 200:
            self.text += "\nB0NUS!" # Slightly glitched text

# Setup
player = B3313Player()
create_level()
Sky()
StarCounter()
Text(text="WASD MOVE | SPACE JUMP | COLLECT STARS", position=(-0.5, -0.4), scale=1.3, font='VeraMono', color=color.rgb(100, 255, 200))

# Consider adding sound effects and music that are reminiscent of the B3313 rom hack for a more authentic experience.

app.run()
