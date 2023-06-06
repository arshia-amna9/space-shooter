import pygame
import random
import sys
import pickle

# Game constants
WIDTH = 800
HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Player constants
PLAYER_SPEED = 5
BULLET_SPEED = 10

# Asteroid constants
ASTEROID_MIN_SPEED = 1
ASTEROID_MAX_SPEED = 5
ASTEROID_SIZE = 50

# Power-up constants
POWERUP_SIZE = 30
SHIELD_DURATION = 3000  # in milliseconds

# Sound effects
BULLET_SOUND_FILE = "bullet.wav"
ASTEROID_DESTROY_SOUND_FILE = "explosion.wav"
POWERUP_COLLECT_SOUND_FILE = "powerup.wav"

# Save file
SAVE_FILE = "save.dat"

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

# Load images
player_img = pygame.image.load("spaceship.png")
bullet_img = pygame.image.load("bullet.png")
asteroid_img = pygame.image.load("asteroid.png")
powerup_img = pygame.image.load("powerup.png")
background_img = pygame.image.load("galaxy_background.png")

# Set image dimensions
player_img = pygame.transform.scale(player_img, (60, 60))
bullet_img = pygame.transform.scale(bullet_img, (10, 30))
asteroid_img = pygame.transform.scale(asteroid_img, (ASTEROID_SIZE, ASTEROID_SIZE))
powerup_img = pygame.transform.scale(powerup_img, (POWERUP_SIZE, POWERUP_SIZE))
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

# Set font
font = pygame.font.Font(None, 32)

# Load sound effects
bullet_sound = pygame.mixer.Sound(BULLET_SOUND_FILE)
asteroid_destroy_sound = pygame.mixer.Sound(ASTEROID_DESTROY_SOUND_FILE)
powerup_collect_sound = pygame.mixer.Sound(POWERUP_COLLECT_SOUND_FILE)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.speed = PLAYER_SPEED
        self.shield = False
        self.shield_start_time = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        elif keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        # Keep player within the screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH


class Asteroid(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = asteroid_img
        self.rect = self.image.get_rect(x=x, y=y)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > HEIGHT:
            self.kill()


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = powerup_img
        self.rect = self.image.get_rect(x=x, y=y)
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > HEIGHT:
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect(x=x, y=y)
        self.speed = BULLET_SPEED

    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()


all_sprites = pygame.sprite.Group()
asteroids_group = pygame.sprite.Group()
powerups_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

score = 0
high_score = 0
lives = 3

asteroids_spawn_time = pygame.time.get_ticks()
powerup_spawn_time = pygame.time.get_ticks()

game_over = False
game_paused = False
game_reset = False




def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)


def spawn_asteroid():
    x = random.randrange(0, WIDTH - ASTEROID_SIZE)
    y = random.randrange(-HEIGHT, -ASTEROID_SIZE)
    speed = random.randrange(ASTEROID_MIN_SPEED, ASTEROID_MAX_SPEED + 1)
    asteroid = Asteroid(x, y, speed)
    all_sprites.add(asteroid)
    asteroids_group.add(asteroid)


def spawn_powerup():
    x = random.randrange(0, WIDTH - POWERUP_SIZE)
    y = random.randrange(-HEIGHT, -POWERUP_SIZE)
    powerup = PowerUp(x, y)
    all_sprites.add(powerup)
    powerups_group.add(powerup)


def spawn_bullet(x, y):
    bullet = Bullet(x, y)
    all_sprites.add(bullet)
    bullets_group.add(bullet)
    bullet_sound.play()  # Play bullet sound effect


def save_game():
    asteroids_data = []
    for asteroid in asteroids_group:
        asteroids_data.append({
            "x": asteroid.rect.x,
            "y": asteroid.rect.y,
            "speed": asteroid.speed
        })

    powerups_data = []
    for powerup in powerups_group:
        powerups_data.append({
            "x": powerup.rect.x,
            "y": powerup.rect.y
        })

    bullets_data = []
    for bullet in bullets_group:
        bullets_data.append({
            "x": bullet.rect.x,
            "y": bullet.rect.y
        })

    save_data = {
        "score": score,
        "high_score": high_score,
        "lives": lives,
        "player_x": player.rect.x,
        "player_y": player.rect.y,
        "asteroids": asteroids_data,
        "powerups": powerups_data,
        "bullets": bullets_data
    }

    with open(SAVE_FILE, "wb") as file:
        pickle.dump(save_data, file)
    print("Game saved successfully!")

def load_game():
    try:
        with open(SAVE_FILE, "rb") as file:
            save_data = pickle.load(file)
        global score, high_score, lives
        score = save_data["score"]
        high_score = save_data["high_score"]
        lives = save_data["lives"]
        player.rect.x = save_data["player_x"]
        player.rect.y = save_data["player_y"]
        asteroids_data = save_data["asteroids"]
        powerups_data = save_data["powerups"]
        bullets_data = save_data["bullets"]
        for asteroid_data in asteroids_data:
            asteroid = Asteroid(**asteroid_data)
            all_sprites.add(asteroid)
            asteroids_group.add(asteroid)
        for powerup_data in powerups_data:
            powerup = PowerUp(**powerup_data)
            all_sprites.add(powerup)
            powerups_group.add(powerup)
        for bullet_data in bullets_data:
            bullet = Bullet(**bullet_data)
            all_sprites.add(bullet)
            bullets_group.add(bullet)
        print("Game loaded successfully!")
    except FileNotFoundError:
        print("No saved game found!")


def show_start_screen():
    screen.blit(background_img, (0, 0))
    draw_text("SPACE SHOOTER", font, WHITE, WIDTH // 2, HEIGHT // 4)
    draw_text("Press SPACE to start", font, WHITE, WIDTH // 2, HEIGHT // 2)
    draw_text("Press L to load game", font, WHITE, WIDTH // 2, HEIGHT // 1.5)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                elif event.key == pygame.K_l:
                    load_game()


def reset_game():
    global game_over, game_paused, game_reset, score, lives
    game_over = False
    game_paused = False
    game_reset = False
    all_sprites.empty()  # Clear all sprites
    player = Player()  # Create a new player instance
    all_sprites.add(player)  # Add the player to the sprite group
    asteroids_group.empty()  # Clear the asteroids group
    powerups_group.empty()  # Clear the power-ups group
    bullets_group.empty()  # Clear the bullets group
    score = 0
    lives = 3
    asteroids_spawn_time = pygame.time.get_ticks()  # Reset spawn time
    powerup_spawn_time = pygame.time.get_ticks()  # Reset spawn time


def show_game_over_screen():
    global high_score, score, lives, game_reset
    if score > high_score:
        high_score = score
    score = 0
    lives = 3
    screen.blit(background_img, (0, 0))
    draw_text("GAME OVER", font, WHITE, WIDTH // 2, HEIGHT // 4)
    draw_text("Score: " + str(score), font, WHITE, WIDTH // 2, HEIGHT // 2)
    draw_text("High Score: " + str(high_score), font, WHITE, WIDTH // 2, HEIGHT // 1.7)
    draw_text("Press SPACE to play again", font, WHITE, WIDTH // 2, HEIGHT // 1.4)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_reset = True
                    waiting = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_SPACE:
                    reset_game()
                    waiting = False
                    return game_reset



def show_pause_screen():
    screen.blit(background_img, (0, 0))
    draw_text("PAUSED", font, WHITE, WIDTH // 2, HEIGHT // 2)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    waiting = False


# Game loop
show_start_screen()
running = True
while running:
    # Keep the game running at the right speed
    clock.tick(FPS)

    if game_over:
        game_reset = show_game_over_screen()  # Show game over screen
        if game_reset:
            reset_game()
        else:
            running = False
            continue

    if game_paused:
        show_pause_screen()
        continue
    else:
        # Process input (events)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_paused:
                    spawn_bullet(player.rect.centerx, player.rect.top)
                elif event.key == pygame.K_p:
                    game_paused = not game_paused
                    if game_paused:
                        show_pause_screen()

    if not game_over and not game_paused:
        # Update
        all_sprites.update()

        # Spawn asteroids
        time_now = pygame.time.get_ticks()
        if time_now - asteroids_spawn_time >= 1000:
            spawn_asteroid()
            asteroids_spawn_time = time_now

        # Spawn power-ups
        if time_now - powerup_spawn_time >= 5000:
            spawn_powerup()
            powerup_spawn_time = time_now

        # Check for collision between player and asteroids
        if pygame.sprite.spritecollide(player, asteroids_group, True):
            if player.shield:
                player.shield = False
                player.image = player_img
            else:
                lives -= 1
                if lives == 0:
                    game_over = True
                    show_game_over_screen()  # Show game over screen
                else:
                    player.rect.x = WIDTH // 2
                    player.rect.y = HEIGHT - 50

        # Check for collision between bullets and asteroids
        for bullet in bullets_group:
            asteroids_hit = pygame.sprite.spritecollide(bullet, asteroids_group, True)
            for asteroid in asteroids_hit:
                bullet.kill()
                asteroid_destroy_sound.play()  # Play asteroid destroy sound effect
                score += 10

        # Check for collision between player and power-ups
        powerups_collected = pygame.sprite.spritecollide(player, powerups_group, True)
        for powerup in powerups_collected:
            player.shield = True
            player.image = pygame.image.load("shield.png")
            player.image = pygame.transform.scale(player.image, (60, 60))
            player.shield_start_time = pygame.time.get_ticks()
            powerup_collect_sound.play()  # Play power-up collect sound effect

        # Check if the shield duration has expired
        if player.shield:
            if pygame.time.get_ticks() - player.shield_start_time >= SHIELD_DURATION:
                player.shield = False
                player.image = player_img

    # Draw / render
    screen.blit(background_img, (0, 0))
    all_sprites.draw(screen)

    # Draw scores
    draw_text("Score: " + str(score), font, WHITE, WIDTH // 2, 10)
    draw_text("High Score: " + str(high_score), font, WHITE, WIDTH // 2, 50)
    draw_text("Lives: " + str(lives), font, WHITE, WIDTH - 100, 10)

    # Update the display
    pygame.display.flip()

# Save game when the player quits or game over
save_game()

# Quit the game
pygame.quit()
sys.exit()
