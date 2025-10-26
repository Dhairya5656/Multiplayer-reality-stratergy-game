import pygame
import random
import time
import cv2
import numpy as np

# ---------- Configuration ----------
WIDTH, HEIGHT = 1280, 720
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
MARGIN = 120

# Assets (replace with your own file names or keep simple rectangles)
BACKGROUND_IMAGE = "background.png"
PLAYER_IMAGE = "player.png"
ENEMY_IMAGE = "enemy.png"
BULLET_IMAGE = "bullet.png"

# Game params
PLAYER_WIDTH, PLAYER_HEIGHT = 100, 60
PLAYER_VELOCITY = 12
BULLET_WIDTH, BULLET_HEIGHT = 10, 20
BULLET_VELOCITY = 18
ENEMY_WIDTH, ENEMY_HEIGHT = 80, 60
ENEMY_VELOCITY = 2
SPAWN_CHANCE = 0.02
MAX_ENEMIES = 12
TIME_LIMIT = 30

# Camera preview
CAM_W, CAM_H = 320, 240
CAM_POS = (10, 50)

# ---------- Initialization ----------
pygame.init()
pygame.mixer.init()  # <-- Initialize mixer

# Load and play background music
pygame.mixer.music.load("cool_adventure_intro.ogg")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)  # loop indefinitely

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders — Reality Mode")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 28)
large_font = pygame.font.SysFont('Arial', 48)

# Try loading images
def load_image(path, size=None, fill_color=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception:
        surf = pygame.Surface(size if size else (50, 50), pygame.SRCALPHA)
        if fill_color:
            surf.fill(fill_color)
        else:
            surf.fill((200, 200, 200))
        return surf

background = load_image(BACKGROUND_IMAGE, (WIDTH, HEIGHT))
player_image = load_image(PLAYER_IMAGE, (PLAYER_WIDTH, PLAYER_HEIGHT), fill_color=(0, 120, 200))
enemy_image = load_image(ENEMY_IMAGE, (ENEMY_WIDTH, ENEMY_HEIGHT), fill_color=(200, 30, 30))
bullet_image = load_image(BULLET_IMAGE, (BULLET_WIDTH, BULLET_HEIGHT), fill_color=(255, 255, 0))

# ---------- Game state helper ----------
class GameState:
    MENU = 'menu'
    PLAYING = 'playing'
    GAMEOVER = 'gameover'

# ---------- Core game class ----------
class SpaceInvadersReality:
    def __init__(self):
        self.reset_game_vars()
        self.state = GameState.MENU
        self.cam = None
        self.cam_running = False

    def reset_game_vars(self):
        self.player_x1 = WIDTH // 4 - PLAYER_WIDTH // 2
        self.player_x2 = 3 * WIDTH // 4 - PLAYER_WIDTH // 2
        self.player_y = HEIGHT - PLAYER_HEIGHT - 20
        self.bullets1 = []
        self.bullets2 = []
        self.enemies = []
        self.score1 = 0
        self.score2 = 0
        self.start_time = None
        self.time_limit = TIME_LIMIT
        self.game_over_reason = ''

    def start_camera(self):
        if not self.cam_running:
            self.cam = cv2.VideoCapture(0)
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_W)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_H)
            self.cam_running = True

    def stop_camera(self):
        if self.cam_running and self.cam is not None:
            try:
                self.cam.release()
            except Exception:
                pass
        self.cam = None
        self.cam_running = False

    def get_camera_surface(self):
        if not self.cam_running or self.cam is None:
            return None
        ret, frame = self.cam.read()
        if not ret:
            return None
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (CAM_W, CAM_H))
        frame = np.rot90(frame)
        surf = pygame.surfarray.make_surface(frame)
        surf = pygame.transform.flip(surf, True, False)
        return surf

    def create_enemy(self):
        enemy_x = random.randint(50, WIDTH - 50 - ENEMY_WIDTH)
        enemy_y = random.randint(-200, -50)
        direction = random.choice([-1, 1])
        return [enemy_x, enemy_y, direction]

    def update_enemies(self):
        for enemy in self.enemies[:]:
            enemy[1] += ENEMY_VELOCITY
            enemy[0] += enemy[2] * 3
            if enemy[0] < 10:
                enemy[0] = 10
                enemy[2] = -enemy[2]
            if enemy[0] > WIDTH - ENEMY_WIDTH - 10:
                enemy[0] = WIDTH - ENEMY_WIDTH - 10
                enemy[2] = -enemy[2]
            if enemy[1] > HEIGHT:
                try:
                    self.enemies.remove(enemy)
                except ValueError:
                    pass

    def check_collisions(self):
        for enemy in self.enemies[:]:
            enemy_rect = pygame.Rect(enemy[0], enemy[1], ENEMY_WIDTH, ENEMY_HEIGHT)
            hit1 = None
            for b in self.bullets1:
                bullet_rect = pygame.Rect(b[0], b[1], BULLET_WIDTH, BULLET_HEIGHT)
                if bullet_rect.colliderect(enemy_rect):
                    hit1 = b
                    break
            if hit1:
                try:
                    self.enemies.remove(enemy)
                    self.bullets1.remove(hit1)
                    self.score1 += 1
                except ValueError:
                    pass
                continue

            hit2 = None
            for b in self.bullets2:
                bullet_rect = pygame.Rect(b[0], b[1], BULLET_WIDTH, BULLET_HEIGHT)
                if bullet_rect.colliderect(enemy_rect):
                    hit2 = b
                    break
            if hit2:
                try:
                    self.enemies.remove(enemy)
                    self.bullets2.remove(hit2)
                    self.score2 += 1
                except ValueError:
                    pass

    def draw_hud(self):
        score_text = font.render(f"Player 1: {self.score1}   Player 2: {self.score2}", True, BLACK)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))
        elapsed = int(time.time() - self.start_time) if self.start_time else 0
        remaining = max(0, self.time_limit - elapsed)
        timer_text = font.render(f"Time: {remaining}s", True, BLACK)
        screen.blit(timer_text, (WIDTH - 170, 10))

    def draw_game(self):
        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill(WHITE)

        cam_surf = self.get_camera_surface() if self.cam_running else None
        if cam_surf:
            screen.blit(cam_surf, CAM_POS)
            pygame.draw.rect(screen, BLACK, (CAM_POS[0] - 2, CAM_POS[1] - 2, CAM_W + 4, CAM_H + 4), 2)
        else:
            pygame.draw.rect(screen, (180, 180, 180), (CAM_POS[0], CAM_POS[1], CAM_W, CAM_H))
            ph = font.render("Camera off", True, BLACK)
            screen.blit(ph, (CAM_POS[0] + 10, CAM_POS[1] + CAM_H//2 - 10))

        screen.blit(player_image, (self.player_x1, self.player_y))
        screen.blit(player_image, (self.player_x2, self.player_y))

        for b in self.bullets1:
            screen.blit(bullet_image, (b[0], b[1]))
        for b in self.bullets2:
            screen.blit(bullet_image, (b[0], b[1]))
        for e in self.enemies:
            screen.blit(enemy_image, (e[0], e[1]))

        self.draw_hud()
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'quit'
                if self.state == GameState.MENU and event.key == pygame.K_s:
                    self.start_round()
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_SPACE:
                        bx = self.player_x1 + PLAYER_WIDTH // 2 - BULLET_WIDTH // 2
                        by = self.player_y - BULLET_HEIGHT
                        self.bullets1.append([bx, by])
                    if event.key == pygame.K_RETURN:
                        bx = self.player_x2 + PLAYER_WIDTH // 2 - BULLET_WIDTH // 2
                        by = self.player_y - BULLET_HEIGHT
                        self.bullets2.append([bx, by])
                elif self.state == GameState.GAMEOVER:
                    if event.key == pygame.K_r:
                        self.reset_game_vars()
                        self.start_round()
                    if event.key == pygame.K_m:
                        self.stop_camera()
                        self.reset_game_vars()
                        self.state = GameState.MENU
        return None

    def start_round(self):
        self.reset_game_vars()
        self.state = GameState.PLAYING
        self.start_time = time.time()
        self.start_camera()

    def update_playing(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and self.player_x1 > MARGIN - PLAYER_WIDTH:
            self.player_x1 -= PLAYER_VELOCITY
        if keys[pygame.K_d] and self.player_x1 < WIDTH // 2 - PLAYER_WIDTH - MARGIN//2:
            self.player_x1 += PLAYER_VELOCITY
        if keys[pygame.K_LEFT] and self.player_x2 > WIDTH // 2 + MARGIN//2:
            self.player_x2 -= PLAYER_VELOCITY
        if keys[pygame.K_RIGHT] and self.player_x2 < WIDTH - PLAYER_WIDTH - (MARGIN - 40):
            self.player_x2 += PLAYER_VELOCITY

        self.bullets1 = [[x, y - BULLET_VELOCITY] for x, y in self.bullets1 if y > -BULLET_HEIGHT]
        self.bullets2 = [[x, y - BULLET_VELOCITY] for x, y in self.bullets2 if y > -BULLET_HEIGHT]

        if len(self.enemies) < MAX_ENEMIES and random.random() < SPAWN_CHANCE:
            self.enemies.append(self.create_enemy())

        self.update_enemies()
        self.check_collisions()

        elapsed = int(time.time() - self.start_time)
        if elapsed >= self.time_limit:
            self.game_over_reason = 'Time Up'
            self.end_round()

    def end_round(self):
        self.stop_camera()
        self.state = GameState.GAMEOVER

    def draw_menu(self):
        screen.fill(WHITE)
        title = large_font.render("Space Invaders — Reality Mode", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))

        pygame.draw.rect(screen, (220, 220, 220), (CAM_POS[0], CAM_POS[1], CAM_W, CAM_H))
        t = font.render("Camera will activate when you start the game", True, BLACK)
        screen.blit(t, (CAM_POS[0], CAM_POS[1] + CAM_H + 10))

        info = font.render("Press S to START   |   Press ESC to QUIT", True, BLACK)
        screen.blit(info, (WIDTH//2 - info.get_width()//2, HEIGHT//2))

        tips = font.render("Player1: A/D + SPACE    Player2: ←/→ + ENTER    Press M to return to Menu (from GameOver)", True, BLACK)
        screen.blit(tips, (WIDTH//2 - tips.get_width()//2, HEIGHT - 60))

        pygame.display.flip()

    def draw_gameover(self):
        screen.fill(WHITE)
        over = large_font.render("Game Over", True, BLACK)
        screen.blit(over, (WIDTH//2 - over.get_width()//2, 60))

        res = font.render(f"Reason: {self.game_over_reason}", True, BLACK)
        screen.blit(res, (WIDTH//2 - res.get_width()//2, 140))

        score_text = font.render(f"Final Scores — Player1: {self.score1}   Player2: {self.score2}", True, BLACK)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 200))

        opts = font.render("Press R to RESTART   |   M for MENU   |   ESC to QUIT", True, BLACK)
        screen.blit(opts, (WIDTH//2 - opts.get_width()//2, HEIGHT - 120))

        pygame.display.flip()

    def run_once(self):
        cmd = self.handle_events()
        if cmd == 'quit':
            return False

        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.update_playing()
            self.draw_game()
        elif self.state == GameState.GAMEOVER:
            self.draw_gameover()

        return True

# ---------- Main loop ----------
def main():
    game = SpaceInvadersReality()
    running = True
    while running:
        running = game.run_once()
        clock.tick(60)

    # cleanup
    pygame.mixer.music.stop()  # stop music
    game.stop_camera()
    pygame.quit()

if __name__ == '__main__':
    main()

