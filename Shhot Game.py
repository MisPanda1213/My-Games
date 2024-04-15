import pygame
import random
import json

# Initialize pygame
pygame.init()

# Set up the screen
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Simple Shooting Game")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Load high scores
def load_high_scores():
    try:
        with open("high_scores.json", "r") as f:
            high_scores = json.load(f)
    except FileNotFoundError:
        high_scores = {}
    return high_scores

# Save high scores
def save_high_scores(high_scores):
    with open("high_scores.json", "w") as f:
        json.dump(high_scores, f)

# Define player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Load rocket image and scale it
        self.image = pygame.image.load("rocket.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (125, 125))  # Scale to 125x125 pixels
        self.rect = self.image.get_rect()
        self.rect.centerx = screen_width // 2
        self.rect.bottom = screen_height - 10
        self.speed_x = 0

    def update(self):
        self.speed_x = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.speed_x = -5
        if keys[pygame.K_RIGHT]:
            self.speed_x = 5
        self.rect.x += self.speed_x
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width

# Define enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Load ball image
        self.image = pygame.image.load("Ball.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))  # Scale to 60x60 pixels
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(screen_width - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed_y = random.randrange(1, 5)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > screen_height + 10:
            self.rect.x = random.randrange(screen_width - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed_y = random.randrange(1, 5)

# Define bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -10

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()

# Set up sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# Initialize score
score = 0
font = pygame.font.Font(None, 36)

# Load high scores
high_scores = load_high_scores()

# Load explosion sound
explosion_sound = pygame.mixer.Sound("bomb.wav")

# Load background image
background = pygame.image.load("space.png").convert()
background = pygame.transform.scale(background, (screen_width, screen_height))

# Define game over screen
def game_over_screen():
    screen.fill(BLACK)
    game_over_text = font.render("The game is over, you lost", True, WHITE)
    screen.blit(game_over_text, (150, 200))
    retry_text = font.render("Retry", True, GREEN)
    retry_rect = retry_text.get_rect(center=(screen_width // 2, 300))
    pygame.draw.rect(screen, BLACK, retry_rect)
    screen.blit(retry_text, retry_rect)
    exit_text = font.render("Exit", True, RED)
    exit_rect = exit_text.get_rect(center=(screen_width // 2, 400))
    pygame.draw.rect(screen, BLACK, exit_rect)
    screen.blit(exit_text, exit_rect)

    pygame.display.flip()

    # Wait for player to click retry or exit
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if retry_rect.collidepoint(event.pos):
                    name = input_name_screen()
                    if name:
                        high_scores[name] = max(score, high_scores.get(name, 0))
                        save_high_scores(high_scores)
                    return "retry"
                elif exit_rect.collidepoint(event.pos):
                    return "exit"

# Define input name screen
def input_name_screen():
    screen.fill(BLACK)
    input_text = font.render("Enter your name:", True, WHITE)
    screen.blit(input_text, (250, 200))
    pygame.display.flip()
    input_active = True
    input_string = ""
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    input_string = input_string[:-1]
                else:
                    input_string += event.unicode
        screen.fill(BLACK)
        input_text = font.render("Enter your name:", True, WHITE)
        screen.blit(input_text, (250, 200))
        name_text = font.render(input_string, True, WHITE)
        screen.blit(name_text, (250, 250))
        pygame.display.flip()
    return input_string

# Define high scores screen
def high_scores_screen():
    screen.fill(BLACK)
    title_text = font.render("High Scores", True, RED)
    screen.blit(title_text, (300, 50))
    y_offset = 100
    for i, (name, score) in enumerate(sorted(high_scores.items(), key=lambda x: x[1], reverse=True)[:5], start=1):
        score_text = font.render(f"{i}. {name}: {score}", True, WHITE)
        screen.blit(score_text, (200, y_offset))
        y_offset += 50
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

# Function to update missed enemies count
def update_missed_enemies():
    global missed_enemies
    missed_enemies += 1

# Function to check if more than 20 red balls are missed
def check_missed_enemies():
    global missed_enemies
    if missed_enemies > 20:
        result = game_over_screen()
        if result == "exit":
            high_scores_screen()
        elif result == "retry":
            # Reset game
            all_sprites.empty()
            enemies.empty()
            bullets.empty()
            player.rect.centerx = screen_width // 2  # Reset player position
            player.rect.bottom = screen_height - 10
            all_sprites.add(player)
            score = 0
            missed_enemies = 0  # Reset missed enemies count

# Main game loop
running = True
clock = pygame.time.Clock()
missed_enemies = 0  # Initialize missed enemies count
while running:
    clock.tick(60)

    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullet = Bullet(player.rect.centerx, player.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)

    # Update
    all_sprites.update()

    # Check for collisions
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for hit in hits:
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)
        score += 1
        explosion_sound.play()  # Play explosion sound

    hits = pygame.sprite.spritecollide(player, enemies, False)
    if hits:
        result = game_over_screen()
        if result == "exit":
            high_scores_screen()
        elif result == "retry":
            # Reset game
            all_sprites.empty()
            enemies.empty()
            bullets.empty()
            player.rect.centerx = screen_width // 2  # Reset player position
            player.rect.bottom = screen_height - 10
            all_sprites.add(player)
            score = 0

    # Generate new enemies
    if len(enemies) < 5:
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)

    # Check if enemies missed
    for enemy in enemies:
        if enemy.rect.top > screen_height:
            update_missed_enemies()  # Update missed enemies count

    # Check if more than 20 red balls are missed
    check_missed_enemies()

    # Render
    screen.blit(background, (0, 0))  # Display background image
    all_sprites.draw(screen)
    
    # Draw score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    pygame.display.flip()

pygame.quit()



























      

