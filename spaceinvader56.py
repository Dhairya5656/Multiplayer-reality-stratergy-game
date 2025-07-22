import pygame
import random
import time


pygame.init()


WIDTH, HEIGHT = 1920, 1080  # Set resolution for full screen (adjust as needed)
WHITE = (255, 255, 255)
MARGIN = 150  # Margin between the two players

# Set up the game window (Fullscreen)
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Space Invaders")

# Load images
background = pygame.image.load("background.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))  # Scale the background image
player_image = pygame.image.load("player.png")
player_image = pygame.transform.scale(player_image, (100, 60))  # Increased size for player
enemy_image = pygame.image.load("enemy.png")
enemy_image = pygame.transform.scale(enemy_image, (100, 80))  
bullet_image = pygame.image.load("bullet.png")
bullet_image = pygame.transform.scale(bullet_image, (20, 40))  # Increased size for bullet (20x40)

# Player setup
player_width, player_height = 100, 60  # Updated player size
player_x1 = WIDTH // 4 - player_width // 2
player_y = HEIGHT - player_height - 20
player_velocity = 30  # Increased speed for faster movement

player_x2 = 3 * WIDTH // 4 - player_width // 2

# Bullet setup
bullet_width, bullet_height = 20, 40  
bullet_velocity = 10  # Increased bullet speed

# Enemy setup
enemy_width, enemy_height = 100, 80  # Increased enemy size
enemy_velocity = 2
enemies = []

# Score setup
score1 = 0
score2 = 0

# Timer setup
start_time = time.time()
time_limit = 30  # 30 seconds time limit

# Font setup
font = pygame.font.SysFont('Arial', 30)

# Game Over Flag
game_over = False

# Function to create a new enemy
def create_enemy():
    enemy_x = random.randint(50, WIDTH - 50)
    enemy_y = random.randint(-150, -50)
    direction = random.choice([-1, 1])  
    return [enemy_x, enemy_y, direction]

# Function to draw the game elements
def draw_game():
    global player_x1, player_x2, score1, score2

    # Draw the background
    screen.blit(background, (0, 0))

    # Draw players
    screen.blit(player_image, (player_x1, player_y))
    screen.blit(player_image, (player_x2, player_y))

    # Draw bullets
    for bullet in bullets1:
        screen.blit(bullet_image, (bullet[0], bullet[1]))
    for bullet in bullets2:
        screen.blit(bullet_image, (bullet[0], bullet[1]))

    # Draw enemies
    for enemy in enemies:
        screen.blit(enemy_image, (enemy[0], enemy[1]))

    # Draw score
    score_text = font.render(f"Player 1: {score1}   Player 2: {score2}", True, (0, 0, 0))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

    # Draw timer
    elapsed_time = int(time.time() - start_time)
    remaining_time = max(0, time_limit - elapsed_time)
    timer_text = font.render(f"Time: {remaining_time}s", True, (0, 0, 0))
    screen.blit(timer_text, (WIDTH - 150, 10))

    pygame.display.update()  


def check_collisions():
    global score1, score2

    for enemy in enemies[:]:
        if any(bullet[1] < enemy[1] + enemy_height and
               bullet[0] > enemy[0] and bullet[0] < enemy[0] + enemy_width
               for bullet in bullets1):
            enemies.remove(enemy)
            score1 += 1

        if any(bullet[1] < enemy[1] + enemy_height and
               bullet[0] > enemy[0] and bullet[0] < enemy[0] + enemy_width
               for bullet in bullets2):
            enemies.remove(enemy)
            score2 += 1

# Function to update the enemies
def update_enemies():
    for enemy in enemies:
        enemy[1] += enemy_velocity
        enemy[0] += enemy[2] * 5  # Move left or right based on direction
        # Reverse direction if the enemy hits the screen border
        if enemy[0] < 50 or enemy[0] > WIDTH - 150:
            enemy[2] = -enemy[2]

        if enemy[1] > HEIGHT:
            enemies.remove(enemy)

# Game Loop
bullets1 = []
bullets2 = []
while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # Player 1 shooting
                bullets1.append([player_x1 + player_width // 2 - bullet_width // 2, player_y - bullet_height])
            if event.key == pygame.K_RETURN:  # Player 2 shooting
                bullets2.append([player_x2 + player_width // 2 - bullet_width // 2, player_y - bullet_height])

    keys = pygame.key.get_pressed()

    # Player 1 movement (left and right)
    if keys[pygame.K_a] and player_x1 > MARGIN:
        player_x1 -= player_velocity
    if keys[pygame.K_d] and player_x1 < WIDTH // 2 - player_width - MARGIN:
        player_x1 += player_velocity

    # Player 2 movement (left and right)
    if keys[pygame.K_LEFT] and player_x2 > WIDTH // 2 + MARGIN:
        player_x2 -= player_velocity
    if keys[pygame.K_RIGHT] and player_x2 < WIDTH - player_width - MARGIN:
        player_x2 += player_velocity

    # Update bullets
    bullets1 = [[x, y - bullet_velocity] for x, y in bullets1 if y > 0]
    bullets2 = [[x, y - bullet_velocity] for x, y in bullets2 if y > 0]

    # Add new enemies
    if random.random() < 0.05:  # 5% chance to spawn an enemy every frame
        enemies.append(create_enemy())

    
    update_enemies()

    # Check collisions
    check_collisions()

    # Draw the game
    draw_game()

    # End game when time runs out
    if int(time.time() - start_time) >= time_limit:
        game_over = True

    pygame.time.delay(30)  # Delay for smooth frame rate

pygame.quit()
