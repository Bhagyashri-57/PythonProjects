import pygame as pg
import cv2
import mediapipe as mp
import random
import time


# ============================================================
# SETTINGS
# ============================================================

WIDTH = 1000
HEIGHT = 800
FPS = 60

# Player
PLAYER_WIDTH = 70
PLAYER_HEIGHT = 70
PLAYER_SPEED = 8

# Player laser
PLAYER_BULLET_WIDTH = 8
PLAYER_BULLET_HEIGHT = 25
PLAYER_BULLET_SPEED = 12
SHOOT_COOLDOWN = 250

# Enemy laser
ENEMY_WIDTH = 16
ENEMY_HEIGHT = 50
ENEMY_SPEED = 4

# Enemy spawning
ENEMY_SPAWN_INTERVAL = 900

# Camera
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

SHOW_CAMERA = True


# ============================================================
# PLAYER
# ============================================================

class Player:

    def __init__(self):

        self.rect = pg.Rect(
            WIDTH // 2 - PLAYER_WIDTH // 2,
            HEIGHT - 110,
            PLAYER_WIDTH,
            PLAYER_HEIGHT
        )

    def move_to(self, x):

        self.rect.centerx = int(x)

        if self.rect.left < 0:
            self.rect.left = 0

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def keyboard_move(self):

        keys = pg.key.get_pressed()

        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rect.x -= PLAYER_SPEED

        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rect.x += PLAYER_SPEED

        if self.rect.left < 0:
            self.rect.left = 0

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def draw(self, screen):

        cx = self.rect.centerx
        top = self.rect.top
        bottom = self.rect.bottom
        left = self.rect.left
        right = self.rect.right

        # Engine flame
        flame_height = random.randint(10, 22)

        pg.draw.polygon(
            screen,
            (255, 120, 20),
            [
                (cx - 12, bottom - 5),
                (cx, bottom + flame_height),
                (cx + 12, bottom - 5)
            ]
        )

        pg.draw.polygon(
            screen,
            (255, 230, 50),
            [
                (cx - 6, bottom - 3),
                (cx, bottom + flame_height - 5),
                (cx + 6, bottom - 3)
            ]
        )

        # Main spaceship
        pg.draw.polygon(
            screen,
            (40, 180, 255),
            [
                (cx, top),
                (cx - 20, top + 30),
                (left + 5, bottom - 12),
                (cx - 10, bottom - 20),
                (cx, bottom - 5),
                (cx + 10, bottom - 20),
                (right - 5, bottom - 12),
                (cx + 20, top + 30)
            ]
        )

        # Left wing
        pg.draw.polygon(
            screen,
            (20, 80, 190),
            [
                (cx - 15, top + 25),
                (left, bottom - 8),
                (cx - 8, bottom - 20)
            ]
        )

        # Right wing
        pg.draw.polygon(
            screen,
            (20, 80, 190),
            [
                (cx + 15, top + 25),
                (right, bottom - 8),
                (cx + 8, bottom - 20)
            ]
        )

        # Cockpit
        pg.draw.ellipse(
            screen,
            (180, 245, 255),
            (cx - 11, top + 12, 22, 27)
        )

        pg.draw.ellipse(
            screen,
            (255, 255, 255),
            (cx - 5, top + 15, 8, 10)
        )


# ============================================================
# PLAYER BULLET
# ============================================================

class PlayerBullet:

    def __init__(self, x, y):

        self.rect = pg.Rect(
            x - PLAYER_BULLET_WIDTH // 2,
            y,
            PLAYER_BULLET_WIDTH,
            PLAYER_BULLET_HEIGHT
        )

    def update(self):

        self.rect.y -= PLAYER_BULLET_SPEED

    def draw(self, screen):

        glow = self.rect.inflate(8, 4)

        pg.draw.rect(
            screen,
            (0, 100, 255),
            glow,
            border_radius=5
        )

        pg.draw.rect(
            screen,
            (50, 220, 255),
            self.rect,
            border_radius=4
        )

        center = self.rect.inflate(-4, -8)

        pg.draw.rect(
            screen,
            (255, 255, 255),
            center,
            border_radius=3
        )


# ============================================================
# ENEMY LASER
# ============================================================

class Enemy:

    def __init__(self):

        x = random.randint(
            30,
            WIDTH - 30
        )

        y = random.randint(
            -400,
            -50
        )

        self.rect = pg.Rect(
            x - ENEMY_WIDTH // 2,
            y,
            ENEMY_WIDTH,
            ENEMY_HEIGHT
        )

        self.speed = random.uniform(
            ENEMY_SPEED,
            ENEMY_SPEED + 2
        )

    def update(self):

        self.rect.y += self.speed

    def draw(self, screen):

        cx = self.rect.centerx

        # Red glow
        glow = pg.Rect(
            cx - 10,
            self.rect.top - 4,
            20,
            self.rect.height + 8
        )

        pg.draw.rect(
            screen,
            (150, 0, 30),
            glow,
            border_radius=8
        )

        # Main laser
        pg.draw.rect(
            screen,
            (255, 30, 50),
            self.rect,
            border_radius=6
        )

        # Yellow center
        center = pg.Rect(
            cx - 4,
            self.rect.top + 5,
            8,
            self.rect.height - 10
        )

        pg.draw.rect(
            screen,
            (255, 220, 50),
            center,
            border_radius=4
        )

        # White highlight
        highlight = pg.Rect(
            cx - 2,
            self.rect.top + 8,
            4,
            self.rect.height // 2
        )

        pg.draw.rect(
            screen,
            (255, 255, 255),
            highlight,
            border_radius=2
        )


# ============================================================
# EXPLOSION
# ============================================================

class Explosion:

    def __init__(self, x, y):

        self.x = x
        self.y = y
        self.radius = 5
        self.life = 15

    def update(self):

        self.radius += 4
        self.life -= 1

    def draw(self, screen):

        if self.life <= 0:
            return

        pg.draw.circle(
            screen,
            (255, 100, 20),
            (self.x, self.y),
            self.radius
        )

        pg.draw.circle(
            screen,
            (255, 230, 50),
            (self.x, self.y),
            max(2, self.radius // 2)
        )


# ============================================================
# MAIN GAME
# ============================================================

class SpaceInvaders:

    def __init__(self):

        pg.init()

        self.screen = pg.display.set_mode(
            (WIDTH, HEIGHT)
        )

        pg.display.set_caption(
            "Space Invaders - Hand Control"
        )

        self.clock = pg.time.Clock()

        # ----------------------------------------------------
        # Fonts
        # ----------------------------------------------------

        self.font = pg.font.SysFont(
            "Arial",
            26
        )

        self.small_font = pg.font.SysFont(
            "Arial",
            18
        )

        self.title_font = pg.font.SysFont(
            "Arial",
            60,
            bold=True
        )

        # ----------------------------------------------------
        # Game state
        # ----------------------------------------------------

        self.running = True
        self.state = "menu"

        self.player = Player()

        self.player_bullets = []
        self.enemies = []
        self.explosions = []

        self.score = 0
        self.lives = 3

        self.last_shot = 0
        self.last_enemy = 0

        self.start_time = 0

        # ----------------------------------------------------
        # Stars
        # ----------------------------------------------------

        self.stars = []

        for _ in range(150):

            self.stars.append(
                [
                    random.randint(0, WIDTH),
                    random.randint(0, HEIGHT),
                    random.randint(1, 3)
                ]
            )

        # ----------------------------------------------------
        # MENU BUTTONS
        # ----------------------------------------------------

        self.play_button = pg.Rect(
            WIDTH // 2 - 130,
            350,
            260,
            65
        )

        self.menu_quit_button = pg.Rect(
            WIDTH // 2 - 130,
            440,
            260,
            65
        )

        # ----------------------------------------------------
        # GAME OVER BUTTONS
        # ----------------------------------------------------

        self.restart_button = pg.Rect(
            WIDTH // 2 - 130,
            350,
            260,
            65
        )

        self.game_over_quit_button = pg.Rect(
            WIDTH // 2 - 130,
            440,
            260,
            65
        )

        # ----------------------------------------------------
        # MEDIAPIPE
        # ----------------------------------------------------

        self.mp_hands = mp.solutions.hands

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5
        )

        # ----------------------------------------------------
        # CAMERA
        # ----------------------------------------------------

        self.camera = cv2.VideoCapture(0)

        self.camera_frame = None
        self.hand_detected = False

        if self.camera.isOpened():

            self.camera.set(
                cv2.CAP_PROP_FRAME_WIDTH,
                CAMERA_WIDTH
            )

            self.camera.set(
                cv2.CAP_PROP_FRAME_HEIGHT,
                CAMERA_HEIGHT
            )

        else:

            print(
                "Camera not found. Keyboard mode enabled."
            )

    # ========================================================
    # RESET
    # ========================================================

    def reset_game(self):

        self.player = Player()

        self.player_bullets.clear()
        self.enemies.clear()
        self.explosions.clear()

        self.score = 0
        self.lives = 3

        self.last_shot = 0
        self.last_enemy = pg.time.get_ticks()

        self.start_time = time.time()

    # ========================================================
    # CAMERA
    # ========================================================

    def get_hand_position(self):

        if not self.camera.isOpened():

            self.hand_detected = False
            return None

        success, frame = self.camera.read()

        if not success:

            self.hand_detected = False
            return None

        # Mirror image
        frame = cv2.flip(
            frame,
            1
        )

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        result = self.hands.process(
            rgb
        )

        self.hand_detected = False

        if result.multi_hand_landmarks:

            hand = result.multi_hand_landmarks[0]

            # Index finger tip
            index_tip = hand.landmark[8]

            # Convert to game position
            x = index_tip.x * WIDTH

            self.hand_detected = True

            mp.solutions.drawing_utils.draw_landmarks(
                frame,
                hand,
                self.mp_hands.HAND_CONNECTIONS
            )

            self.camera_frame = frame

            return x

        self.camera_frame = frame

        return None

    # ========================================================
    # SHOOT
    # ========================================================

    def shoot(self):

        current_time = pg.time.get_ticks()

        if (
            current_time - self.last_shot
            >= SHOOT_COOLDOWN
        ):

            bullet = PlayerBullet(
                self.player.rect.centerx,
                self.player.rect.top
            )

            self.player_bullets.append(
                bullet
            )

            self.last_shot = current_time

    # ========================================================
    # UPDATE
    # ========================================================

    def update_game(self):

        # ----------------------------------------------------
        # Hand movement
        # ----------------------------------------------------

        hand_x = self.get_hand_position()

        if hand_x is not None:

            current_x = self.player.rect.centerx

            smooth_x = (
                current_x * 0.7 +
                hand_x * 0.3
            )

            self.player.move_to(
                smooth_x
            )

        else:

            self.player.keyboard_move()

        # ----------------------------------------------------
        # Keyboard shooting
        # ----------------------------------------------------

        keys = pg.key.get_pressed()

        if keys[pg.K_SPACE]:

            self.shoot()

        # ----------------------------------------------------
        # Spawn enemy lasers
        # ----------------------------------------------------

        current_time = pg.time.get_ticks()

        spawn_interval = max(
            300,
            ENEMY_SPAWN_INTERVAL -
            self.score * 10
        )

        if (
            current_time - self.last_enemy
            >= spawn_interval
        ):

            self.enemies.append(
                Enemy()
            )

            self.last_enemy = current_time

        # ----------------------------------------------------
        # Player bullets
        # ----------------------------------------------------

        for bullet in self.player_bullets[:]:

            bullet.update()

            if bullet.rect.bottom < 0:

                self.player_bullets.remove(
                    bullet
                )

        # ----------------------------------------------------
        # Enemy lasers
        # ----------------------------------------------------

        for enemy in self.enemies[:]:

            enemy.update()

            # Enemy escaped
            if enemy.rect.top > HEIGHT:

                self.enemies.remove(
                    enemy
                )

                self.lives -= 1

                continue

            # Enemy hits player
            if enemy.rect.colliderect(
                self.player.rect
            ):

                self.enemies.remove(
                    enemy
                )

                self.lives -= 1

                self.explosions.append(
                    Explosion(
                        self.player.rect.centerx,
                        self.player.rect.centery
                    )
                )

        # ----------------------------------------------------
        # Player bullet collision
        # ----------------------------------------------------

        for bullet in self.player_bullets[:]:

            for enemy in self.enemies[:]:

                if bullet.rect.colliderect(
                    enemy.rect
                ):

                    if bullet in self.player_bullets:

                        self.player_bullets.remove(
                            bullet
                        )

                    if enemy in self.enemies:

                        self.enemies.remove(
                            enemy
                        )

                    self.score += 1

                    self.explosions.append(
                        Explosion(
                            enemy.rect.centerx,
                            enemy.rect.centery
                        )
                    )

                    break

        # ----------------------------------------------------
        # Explosions
        # ----------------------------------------------------

        for explosion in self.explosions[:]:

            explosion.update()

            if explosion.life <= 0:

                self.explosions.remove(
                    explosion
                )

        # ----------------------------------------------------
        # GAME OVER
        # ----------------------------------------------------

        if self.lives <= 0:

            self.state = "game_over"

    # ========================================================
    # BACKGROUND
    # ========================================================

    def draw_background(self):

        self.screen.fill(
            (3, 5, 25)
        )

        for star in self.stars:

            star[1] += star[2] * 0.4

            if star[1] > HEIGHT:

                star[1] = 0

                star[0] = random.randint(
                    0,
                    WIDTH
                )

            pg.draw.circle(
                self.screen,
                (180, 200, 255),
                (
                    int(star[0]),
                    int(star[1])
                ),
                star[2]
            )

    # ========================================================
    # GAME SCREEN
    # ========================================================

    def draw_game(self):

        self.draw_background()

        self.player.draw(
            self.screen
        )

        for bullet in self.player_bullets:

            bullet.draw(
                self.screen
            )

        for enemy in self.enemies:

            enemy.draw(
                self.screen
            )

        for explosion in self.explosions:

            explosion.draw(
                self.screen
            )

        # Score
        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            score_text,
            (20, 15)
        )

        # Lives
        lives_text = self.font.render(
            f"Lives: {self.lives}",
            True,
            (255, 100, 100)
        )

        self.screen.blit(
            lives_text,
            (20, 50)
        )

        # Time
        elapsed = int(
            time.time() - self.start_time
        )

        time_text = self.font.render(
            f"Time: {elapsed}s",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            time_text,
            (20, 85)
        )

        # Hand status
        if self.hand_detected:

            status = "HAND DETECTED"
            status_color = (50, 255, 100)

        else:

            status = "KEYBOARD MODE"
            status_color = (255, 200, 50)

        status_text = self.small_font.render(
            status,
            True,
            status_color
        )

        self.screen.blit(
            status_text,
            (20, 120)
        )

        # Instructions
        instruction = self.small_font.render(
            "Index Finger = Move | SPACE = Shoot | M = Camera | ESC = Quit",
            True,
            (190, 200, 220)
        )

        self.screen.blit(
            instruction,
            (
                WIDTH // 2 -
                instruction.get_width() // 2,
                HEIGHT - 28
            )
        )

        # Camera
        if (
            SHOW_CAMERA
            and self.camera_frame is not None
        ):

            frame = cv2.cvtColor(
                self.camera_frame,
                cv2.COLOR_BGR2RGB
            )

            frame = cv2.resize(
                frame,
                (200, 150)
            )

            camera_surface = pg.surfarray.make_surface(
                frame.swapaxes(0, 1)
            )

            camera_x = WIDTH - 215
            camera_y = 15

            self.screen.blit(
                camera_surface,
                (camera_x, camera_y)
            )

            pg.draw.rect(
                self.screen,
                (255, 255, 255),
                (
                    camera_x,
                    camera_y,
                    200,
                    150
                ),
                2
            )

        pg.display.flip()

    # ========================================================
    # MENU
    # ========================================================

    def draw_menu(self):

        self.draw_background()

        overlay = pg.Surface(
            (WIDTH, HEIGHT),
            pg.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 150)
        )

        self.screen.blit(
            overlay,
            (0, 0)
        )

        title = self.title_font.render(
            "SPACE INVADERS",
            True,
            (80, 210, 255)
        )

        self.screen.blit(
            title,
            (
                WIDTH // 2 -
                title.get_width() // 2,
                100
            )
        )

        subtitle = self.font.render(
            "HAND CONTROLLED SPACE BATTLE",
            True,
            (230, 230, 230)
        )

        self.screen.blit(
            subtitle,
            (
                WIDTH // 2 -
                subtitle.get_width() // 2,
                180
            )
        )

        # PLAY
        pg.draw.rect(
            self.screen,
            (40, 180, 255),
            self.play_button,
            border_radius=12
        )

        play_text = self.font.render(
            "PLAY",
            True,
            (0, 0, 30)
        )

        self.screen.blit(
            play_text,
            (
                self.play_button.centerx -
                play_text.get_width() // 2,
                self.play_button.centery -
                play_text.get_height() // 2
            )
        )

        # QUIT
        pg.draw.rect(
            self.screen,
            (230, 60, 70),
            self.menu_quit_button,
            border_radius=12
        )

        quit_text = self.font.render(
            "QUIT",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            quit_text,
            (
                self.menu_quit_button.centerx -
                quit_text.get_width() // 2,
                self.menu_quit_button.centery -
                quit_text.get_height() // 2
            )
        )

        instructions = [
            "INDEX FINGER → Move spaceship",
            "SPACE → Shoot",
            "M → Camera on/off",
            "ESC → Exit"
        ]

        y = 550

        for line in instructions:

            text = self.small_font.render(
                line,
                True,
                (220, 220, 220)
            )

            self.screen.blit(
                text,
                (
                    WIDTH // 2 -
                    text.get_width() // 2,
                    y
                )
            )

            y += 30

        pg.display.flip()

    # ========================================================
    # GAME OVER
    # ========================================================

    def draw_game_over(self):

        self.draw_background()

        overlay = pg.Surface(
            (WIDTH, HEIGHT),
            pg.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 180)
        )

        self.screen.blit(
            overlay,
            (0, 0)
        )

        title = self.title_font.render(
            "GAME OVER",
            True,
            (255, 70, 70)
        )

        self.screen.blit(
            title,
            (
                WIDTH // 2 -
                title.get_width() // 2,
                130
            )
        )

        score_text = self.font.render(
            f"YOUR SCORE: {self.score}",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            score_text,
            (
                WIDTH // 2 -
                score_text.get_width() // 2,
                230
            )
        )

        # ====================================================
        # RESTART BUTTON
        # ====================================================

        pg.draw.rect(
            self.screen,
            (40, 180, 255),
            self.restart_button,
            border_radius=12
        )

        restart_text = self.font.render(
            "RESTART",
            True,
            (0, 0, 30)
        )

        self.screen.blit(
            restart_text,
            (
                self.restart_button.centerx -
                restart_text.get_width() // 2,
                self.restart_button.centery -
                restart_text.get_height() // 2
            )
        )

        # ====================================================
        # QUIT BUTTON
        # ====================================================

        pg.draw.rect(
            self.screen,
            (230, 60, 70),
            self.game_over_quit_button,
            border_radius=12
        )

        quit_text = self.font.render(
            "QUIT",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            quit_text,
            (
                self.game_over_quit_button.centerx -
                quit_text.get_width() // 2,
                self.game_over_quit_button.centery -
                quit_text.get_height() // 2
            )
        )

        pg.display.flip()

    # ========================================================
    # EVENT HANDLER
    # ========================================================

    def handle_events(self):

        for event in pg.event.get():

            # ------------------------------------------------
            # WINDOW CLOSE BUTTON
            # ------------------------------------------------

            if event.type == pg.QUIT:

                self.running = False

            # ------------------------------------------------
            # MOUSE
            # ------------------------------------------------

            elif event.type == pg.MOUSEBUTTONDOWN:

                mouse_x, mouse_y = event.pos

                # ============================================
                # MENU
                # ============================================

                if self.state == "menu":

                    if self.play_button.collidepoint(
                        mouse_x,
                        mouse_y
                    ):

                        self.reset_game()

                        self.state = "playing"

                    elif self.menu_quit_button.collidepoint(
                        mouse_x,
                        mouse_y
                    ):

                        print("Menu Quit clicked")

                        self.running = False

                # ============================================
                # GAME OVER
                # ============================================

                elif self.state == "game_over":

                    if self.restart_button.collidepoint(
                        mouse_x,
                        mouse_y
                    ):

                        print("Restart clicked")

                        self.reset_game()

                        self.state = "playing"

                    elif self.game_over_quit_button.collidepoint(
                        mouse_x,
                        mouse_y
                    ):

                        # ====================================
                        # THIS IS THE IMPORTANT FIX
                        # ====================================

                        print("Game Over Quit clicked")

                        self.running = False

            # ------------------------------------------------
            # KEYBOARD
            # ------------------------------------------------

            elif event.type == pg.KEYDOWN:

                # ESC works everywhere
                if event.key == pg.K_ESCAPE:

                    self.running = False

                # MENU
                elif self.state == "menu":

                    if event.key == pg.K_RETURN:

                        self.reset_game()

                        self.state = "playing"

                # PLAYING
                elif self.state == "playing":

                    if event.key == pg.K_SPACE:

                        self.shoot()

                    elif event.key == pg.K_m:

                        global SHOW_CAMERA

                        SHOW_CAMERA = not SHOW_CAMERA

                # GAME OVER
                elif self.state == "game_over":

                    if event.key == pg.K_RETURN:

                        self.reset_game()

                        self.state = "playing"

    # ========================================================
    # MAIN LOOP
    # ========================================================

    def run(self):

        while self.running:

            self.clock.tick(FPS)

            self.handle_events()

            if self.state == "menu":

                self.draw_menu()

            elif self.state == "playing":

                self.update_game()

                self.draw_game()

            elif self.state == "game_over":

                self.draw_game_over()

        # ----------------------------------------------------
        # CLEANUP
        # ----------------------------------------------------

        if self.camera.isOpened():

            self.camera.release()

        self.hands.close()

        cv2.destroyAllWindows()

        pg.quit()


# ============================================================
# START GAME
# ============================================================

if __name__ == "__main__":

    game = SpaceInvaders()

    game.run()