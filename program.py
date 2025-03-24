from ursina import *        # Import Ursina engine classes and definitions
import random               # Import random for randomness in glitch effects

# Configure window (title, etc.) to avoid warnings and set vibe
app = Ursina()  # Initialize the Ursina app first to define 'base'
window.title = "B3313-Inspired Surreal Game"
window.borderless = False   # Ensure window is created normally (not borderless fullscreen)
Texture.default_filtering = None  # Disable texture filtering for an aliased (pixelated) look
window.color = color.black  # Black background to contrast colorful objects

# Define a Player entity with basic movement and jump mechanics
class Player(Entity):
    def __init__(self):
        super().__init__(
            model='cube',
            color=color.white,
            texture=None,
            position=(0, 1, 0),   # start slightly above ground
            scale=(0.5, 1, 0.5),  # a rectangular player shape (width, height, depth)
            collider='box'
        )
        self.speed = 5          # movement speed
        self.jump_power = 5     # jump strength (fixed for consistency)
        self.velocity_y = 0     # vertical velocity (for gravity/jumping)
        self.grounded = False   # whether player is on the ground

    def update(self):
        # Horizontal movement (WASD keys)
        direction = Vec3(
            held_keys['d'] - held_keys['a'],
            0,
            held_keys['w'] - held_keys['s']
        )
        if direction.length() > 0: 
            direction = direction.normalized()  # move at consistent speed in any direction
        self.position += direction * self.speed * time.dt

        # Apply gravity
        self.velocity_y -= 9.8 * time.dt  # gravity acceleration
        self.y += self.velocity_y * time.dt

        # Ground collision check (simple ground at y=0)
        if self.y <= 0.5:  # 0.5 is half the player's height (since scale_y=1)
            self.y = 0.5
            self.velocity_y = 0
            self.grounded = True
        else:
            self.grounded = False

    def input(self, key):
        # Jump on spacebar press
        if key == 'space' and self.grounded:
            self.velocity_y = self.jump_power
            self.grounded = False

# Define a glitchy block entity for surreal effect (scale jitters over time)
class Block(Entity):
    def __init__(self, position=(0, 0, 0), color=color.random_color()):
        super().__init__(
            model='cube',
            texture=None,
            color=color,
            position=position,
            scale=(1, 1, 1)  # start with uniform scale
        )
        # Initial random scale variation
        offset = random.uniform(-0.05, 0.05)
        self.scale = Vec3(1 + offset, 1 + offset, 1 + offset)

    def update(self):
        # Slight random jitter in scale for glitch effect (uniform in all directions)
        offset = random.uniform(-0.02, 0.02)    # small random offset
        self.scale = Vec3(
            self.scale.x + offset,
            self.scale.y + offset,
            self.scale.z + offset
        )
        # Clamp scale to prevent it from becoming too small or too large
        self.scale = Vec3(
            max(0.1, min(2, self.scale.x)),
            max(0.1, min(2, self.scale.y)),
            max(0.1, min(2, self.scale.z))
        )

# Function to create the level
def create_level():
    # Ground platform (large cube as the floor)
    ground = Entity(
        model='cube',
        color=color.green,
        texture=None,
        scale=(40, 1, 40),    # wide, flat ground
        position=(0, -0.5, 0),# center at -0.5 so top surface is at y=0
        collider='box'
    )

    # Generate a grid of glitchy blocks
    for x in range(-5, 6):
        for z in range(-5, 6):
            if random.random() < 0.3:  # 30% chance to spawn a block
                Block(position=(x, 0, z))

# Create game entities
player = Player()  # the player character
create_level()     # create the level with ground and blocks

# Set camera behind and above the player for a third-person view
camera.parent = player
camera.position = (0, 5, -15)   # offset camera slightly above and behind the player
camera.rotation_x = 20          # angle the camera downward to view the scene
camera.fov = 90                 # wide field of view for a surreal feel

# Run the Ursina app (start the game loop)
app.run()
