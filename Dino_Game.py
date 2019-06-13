import pygame

# Initialize
pygame.init()

# Set window size/title
window = pygame.display.set_mode((96, 16))
pygame.display.set_caption("Dino Game")

# Dino starting coordinates
x = 5
y = 9

# Cactus starting X coordinate
cactus_x = 96

# Jumping controls to prevent multiple jumps.
jumping = False
jump_timer = 20

# Walk Counter to determine which sprite is displayed.
walk_count = 4

# Pre-Load sprites
d1 = pygame.image.load('d1.png')
d2 = pygame.image.load('d2.png')

# Starting Sprite
dino = d1

# Game Loop
run = True
while run:
    # Alters update rate
    pygame.time.delay(100)

    # default game quit script
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Key Input object (stored as array)
    keys = pygame.key.get_pressed()
    
    # Pressing Q ends the loops
    if keys[pygame.K_q]:
            run = False

    # Up or Space Jumps
    if keys[pygame.K_UP] or keys[pygame.K_SPACE]:   
        if not(jumping):
            jumping = True
        
    # Updates draw with jump "animation"    
    if jumping:
        if jump_timer > 10:
            y -= 1
            jump_timer -= 1
        elif jump_timer > 0: 
            jump_timer -= 1
            y += 1
        else:
            jump_timer = 20
            jumping = False
    
    # Erase previous draw
    window.fill((0,0,0))

    # Animate Dino. Stop animation if jumping.
    if not(jumping):
        if walk_count > 2:
            dino = d1
            walk_count -= 1
        elif walk_count > 0:
            dino = d2
            walk_count -= 1
        else:
            dino = d1
            walk_count = 4

    # Draw dino sprite
    window.blit(dino, (x, y))
    
    # Draw cactus (window, color, (x coord, y coord, width, height) )
    pygame.draw.rect(window, (255,255,255), (cactus_x, 11, 3, 5))
    
    # Move Cactus across window. Reset if off screen.
    if(cactus_x <= -3):
        cactus_x = 96
    else:
        cactus_x -= 1
    
    # Udpate screen.
    pygame.display.update()

# End program after loop.    
pygame.quit()
