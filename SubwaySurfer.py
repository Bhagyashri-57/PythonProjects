import pygame
import cv2
import mediapipe as mp
import random
import math
import os
import sys
import time

# ============================================================
# CONFIGURATION
# ============================================================

WIDTH = 1100
HEIGHT = 800
FPS = 60

ROAD_TOP = 210
ROAD_BOTTOM = HEIGHT

LANES = [-1, 0, 1]

# Player
PLAYER_W = 58
PLAYER_H = 90

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
GREEN = (50, 220, 100)
YELLOW = (255, 215, 0)
BLUE = (50, 150, 255)
ORANGE = (255, 150, 30)

# ============================================================
# PYGAME INITIALIZATION
# ============================================================

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Subway Runner - MediaPipe")

clock = pygame.time.Clock()

font_big = pygame.font.SysFont("arial", 55, bold=True)
font_medium = pygame.font.SysFont("arial", 32, bold=True)
font_small = pygame.font.SysFont("arial", 22, bold=True)

# ============================================================
# MEDIAPIPE
# ============================================================

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.55,
    min_tracking_confidence=0.55
)

# ============================================================
# CAMERA
# ============================================================

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ERROR: Camera could not be opened.")
    print("The game can still run using keyboard controls.")

# ============================================================
# ASSET LOADING
# ============================================================

ASSET_DIR = "assets"


def load_image(filename, size=None):
    path = os.path.join(ASSET_DIR, filename)

    if not os.path.exists(path):
        return None

    try:
        img = pygame.image.load(path).convert_alpha()

        if size:
            img = pygame.transform.smoothscale(img, size)

        return img

    except:
        return None


# Optional realistic assets
player_img = load_image("player.png", (PLAYER_W, PLAYER_H))
train_img = load_image("train.png")
coin_img = load_image("coin.png", (38, 38))
building_img = load_image("building.png")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def lane_x(lane):
    """
    Convert lane number (-1, 0, 1) into screen X.
    """

    center = WIDTH // 2

    if lane == -1:
        return center - 145

    if lane == 0:
        return center

    return center + 145


def perspective_y(distance):
    """
    Converts distance from horizon to screen Y.
    """

    distance = clamp(distance, 0, 1)

    return ROAD_TOP + (distance ** 1.8) * (HEIGHT - ROAD_TOP)


def perspective_scale(distance):
    return 0.25 + distance * 0.9


# ============================================================
# BACKGROUND
# ============================================================

def draw_sky():
    """
    Draws a realistic-looking sunset/blue sky.
    """

    horizon = ROAD_TOP

    for y in range(horizon):

        ratio = y / horizon

        r = int(35 + ratio * 80)
        g = int(100 + ratio * 80)
        b = int(180 + ratio * 50)

        pygame.draw.line(
            screen,
            (r, g, b),
            (0, y),
            (WIDTH, y)
        )

    # Sun
    pygame.draw.circle(
        screen,
        (255, 220, 130),
        (WIDTH // 2 + 270, 110),
        45
    )

    # Sun glow
    for radius in range(100, 50, -10):
        pygame.draw.circle(
            screen,
            (255, 200, 100),
            (WIDTH // 2 + 270, 110),
            radius,
            2
        )


def draw_cloud(x, y, scale=1):
    pygame.draw.ellipse(
        screen,
        (235, 240, 245),
        (
            x,
            y,
            int(90 * scale),
            int(35 * scale)
        )
    )

    pygame.draw.circle(
        screen,
        (245, 245, 250),
        (int(x + 30 * scale), int(y)),
        int(25 * scale)
    )

    pygame.draw.circle(
        screen,
        (245, 245, 250),
        (int(x + 60 * scale), int(y - 8 * scale)),
        int(30 * scale)
    )


def draw_background_buildings():
    """
    City skyline behind railway.
    """

    building_colors = [
        (75, 82, 95),
        (90, 92, 100),
        (65, 72, 84),
        (105, 95, 90),
        (70, 80, 90)
    ]

    x = 0

    while x < WIDTH:

        w = random.randint(50, 100)
        h = random.randint(60, 150)

        y = ROAD_TOP - h

        color = random.choice(building_colors)

        pygame.draw.rect(
            screen,
            color,
            (x, y, w, h)
        )

        # Windows
        for wx in range(x + 10, x + w - 5, 18):

            for wy in range(y + 12, ROAD_TOP - 5, 25):

                if random.random() > 0.35:

                    pygame.draw.rect(
                        screen,
                        (245, 210, 110),
                        (wx, wy, 8, 12)
                    )

        x += w + random.randint(5, 15)


def draw_railway():
    """
    Perspective railway.
    """

    # Ground
    pygame.draw.polygon(
        screen,
        (75, 76, 78),
        [
            (0, ROAD_TOP),
            (WIDTH, ROAD_TOP),
            (WIDTH, HEIGHT),
            (0, HEIGHT)
        ]
    )

    # Side areas
    pygame.draw.polygon(
        screen,
        (42, 45, 47),
        [
            (0, ROAD_TOP),
            (WIDTH // 2 - 210, ROAD_TOP),
            (WIDTH // 2 - 500, HEIGHT),
            (0, HEIGHT)
        ]
    )

    pygame.draw.polygon(
        screen,
        (42, 45, 47),
        [
            (WIDTH, ROAD_TOP),
            (WIDTH // 2 + 210, ROAD_TOP),
            (WIDTH // 2 + 500, HEIGHT),
            (WIDTH, HEIGHT)
        ]
    )

    center = WIDTH // 2

    # Track corridors
    for lane in LANES:

        x = lane_x(lane)

        # Rails
        top_x1 = center + lane * 75
        top_x2 = center + lane * 125

        bottom_x1 = x - 40
        bottom_x2 = x + 40

        pygame.draw.line(
            screen,
            (180, 180, 180),
            (top_x1, ROAD_TOP),
            (bottom_x1, HEIGHT),
            5
        )

        pygame.draw.line(
            screen,
            (180, 180, 180),
            (top_x2, ROAD_TOP),
            (bottom_x2, HEIGHT),
            5
        )

    # Railway sleepers
    for i in range(18):

        d = i / 18

        y = perspective_y(d)

        half_width = 70 + d * 470

        pygame.draw.line(
            screen,
            (85, 60, 45),
            (center - half_width, y),
            (center + half_width, y),
            max(2, int(5 * d))
        )


# ============================================================
# DECORATION
# ============================================================

def draw_poles():

    center = WIDTH // 2

    for side in [-1, 1]:

        for i in range(8):

            d = i / 8

            y = perspective_y(d)

            x = center + side * (260 + d * 280)

            height = 100 + d * 100

            pygame.draw.line(
                screen,
                (35, 35, 35),
                (x, y),
                (x, y - height),
                max(2, int(4 * d))
            )

            pygame.draw.line(
                screen,
                (35, 35, 35),
                (x - 20, y - height),
                (x + 20, y - height),
                4
            )


# ============================================================
# PLAYER
# ============================================================

class Player:

    def __init__(self):

        self.lane = 0

        self.x = lane_x(self.lane)

        self.y = HEIGHT - 150

        self.target_x = self.x

        self.jumping = False
        self.sliding = False

        self.jump_start = 0

        self.slide_start = 0

        self.velocity_y = 0

    def move_left(self):

        if self.lane > -1:
            self.lane -= 1

            self.target_x = lane_x(self.lane)

    def move_right(self):

        if self.lane < 1:
            self.lane += 1

            self.target_x = lane_x(self.lane)

    def jump(self):

        if not self.jumping and not self.sliding:

            self.jumping = True
            self.jump_start = time.time()

    def slide(self):

        if not self.jumping:

            self.sliding = True
            self.slide_start = time.time()

    def update(self):

        # Smooth lane movement
        self.x += (self.target_x - self.x) * 0.25

        # Jump
        if self.jumping:

            elapsed = time.time() - self.jump_start

            jump_duration = 0.75

            if elapsed >= jump_duration:

                self.jumping = False

            else:

                progress = elapsed / jump_duration

                self.y = (
                    HEIGHT - 150
                    - math.sin(progress * math.pi) * 180
                )

        else:

            self.y = HEIGHT - 150

        # Slide
        if self.sliding:

            if time.time() - self.slide_start > 0.7:

                self.sliding = False

    def get_rect(self):

        if self.sliding:

            return pygame.Rect(
                int(self.x - PLAYER_W // 2),
                int(self.y + 30),
                PLAYER_W,
                PLAYER_H // 2
            )

        return pygame.Rect(
            int(self.x - PLAYER_W // 2),
            int(self.y),
            PLAYER_W,
            PLAYER_H
        )

    def draw(self):

        rect = self.get_rect()

        if player_img:

            image = player_img

            if self.sliding:

                image = pygame.transform.scale(
                    image,
                    (PLAYER_W + 15, PLAYER_H // 2)
                )

            screen.blit(
                image,
                image.get_rect(center=rect.center)
            )

            return

        # Character shadow
        pygame.draw.ellipse(
            screen,
            (25, 25, 25),
            (
                int(self.x - 30),
                HEIGHT - 65,
                60,
                15
            )
        )

        if self.sliding:

            # Body
            pygame.draw.ellipse(
                screen,
                (35, 80, 210),
                rect
            )

            # Head
            pygame.draw.circle(
                screen,
                (220, 170, 120),
                (
                    int(self.x + 20),
                    int(self.y + 40)
                ),
                18
            )

        else:

            # Legs
            pygame.draw.line(
                screen,
                (20, 20, 30),
                (self.x, self.y + 65),
                (self.x - 15, self.y + 90),
                9
            )

            pygame.draw.line(
                screen,
                (20, 20, 30),
                (self.x, self.y + 65),
                (self.x + 15, self.y + 90),
                9
            )

            # Body
            pygame.draw.rect(
                screen,
                (30, 90, 220),
                (
                    int(self.x - 22),
                    int(self.y + 25),
                    44,
                    45
                ),
                border_radius=10
            )

            # Head
            pygame.draw.circle(
                screen,
                (220, 170, 120),
                (
                    int(self.x),
                    int(self.y + 15)
                ),
                20
            )

            # Hair
            pygame.draw.arc(
                screen,
                (30, 20, 15),
                (
                    int(self.x - 20),
                    int(self.y - 5),
                    40,
                    35
                ),
                math.pi,
                math.pi * 2,
                8
            )


# ============================================================
# OBSTACLES
# ============================================================

class Train:

    def __init__(self, lane):

        self.lane = lane

        self.distance = 0.05

        self.speed = 0.012

        self.passed = False

        self.width = 95
        self.height = 150

    def update(self):

        self.distance += self.speed

    def get_rect(self):

        scale = perspective_scale(self.distance)

        x = lane_x(self.lane)

        y = perspective_y(self.distance)

        width = int(self.width * scale)
        height = int(self.height * scale)

        return pygame.Rect(
            int(x - width // 2),
            int(y - height),
            width,
            height
        )

    def draw(self):

        rect = self.get_rect()

        if self.distance > 0.8:

            rect = self.get_rect()

        # Train body
        pygame.draw.rect(
            screen,
            (190, 45, 45),
            rect,
            border_radius=8
        )

        # Front
        pygame.draw.rect(
            screen,
            (65, 70, 75),
            (
                rect.x + rect.width * 0.15,
                rect.y + rect.height * 0.2,
                rect.width * 0.7,
                rect.height * 0.3
            )
        )

        # Windows
        for i in range(3):

            wx = rect.x + int(
                rect.width * (0.18 + i * 0.25)
            )

            wy = rect.y + int(rect.height * 0.25)

            pygame.draw.rect(
                screen,
                (60, 150, 200),
                (
                    wx,
                    wy,
                    int(rect.width * 0.16),
                    int(rect.height * 0.16)
                )
            )

        # Headlights
        pygame.draw.circle(
            screen,
            (255, 245, 180),
            (
                rect.centerx - int(rect.width * 0.28),
                rect.bottom - int(rect.height * 0.2)
            ),
            max(2, int(rect.width * 0.05))
        )

        pygame.draw.circle(
            screen,
            (255, 245, 180),
            (
                rect.centerx + int(rect.width * 0.28),
                rect.bottom - int(rect.height * 0.2)
            ),
            max(2, int(rect.width * 0.05))
        )


# ============================================================
# COINS
# ============================================================

class Coin:

    def __init__(self, lane):

        self.lane = lane

        self.distance = 0.05

        self.speed = 0.014

        self.collected = False

    def update(self):

        self.distance += self.speed

    def get_rect(self):

        scale = perspective_scale(self.distance)

        size = max(8, int(30 * scale))

        x = lane_x(self.lane)

        y = perspective_y(self.distance) - int(80 * scale)

        return pygame.Rect(
            int(x - size // 2),
            int(y - size // 2),
            size,
            size
        )

    def draw(self):

        rect = self.get_rect()

        if coin_img:

            image = pygame.transform.smoothscale(
                coin_img,
                (rect.width, rect.height)
            )

            screen.blit(
                image,
                rect
            )

        else:

            pygame.draw.circle(
                screen,
                YELLOW,
                rect.center,
                rect.width // 2
            )

            pygame.draw.circle(
                screen,
                (255, 235, 100),
                rect.center,
                max(2, rect.width // 3)
            )


# ============================================================
# GAME CLASS
# ============================================================

class Game:

    def __init__(self):

        self.player = Player()

        self.trains = []
        self.coins = []

        self.score = 0

        self.coins_collected = 0

        self.lives = 3

        self.game_over = False

        self.game_started = False

        self.speed = 0.012

        self.last_spawn = time.time()

        self.last_coin_spawn = time.time()

        self.camera_x = 0

        self.gesture_text = "Keyboard / Hand Control"

        self.last_hand_action = 0

        self.hand_cooldown = 0.5

    def reset(self):

        self.player = Player()

        self.trains.clear()

        self.coins.clear()

        self.score = 0

        self.coins_collected = 0

        self.lives = 3

        self.game_over = False

        self.game_started = True

        self.speed = 0.012

        self.last_spawn = time.time()

        self.last_coin_spawn = time.time()

    def spawn_train(self):

        lane = random.choice(LANES)

        train = Train(lane)

        train.speed = self.speed

        self.trains.append(train)

    def spawn_coin_line(self):

        lane = random.choice(LANES)

        for i in range(5):

            coin = Coin(lane)

            coin.distance = 0.05 - i * 0.06

            coin.speed = self.speed + 0.002

            self.coins.append(coin)

    def update(self):

        if self.game_over:
            return

        self.player.update()

        # Increase speed slowly
        self.speed += 0.000005

        # Spawn trains
        if time.time() - self.last_spawn > max(
            0.8,
            1.5 - self.score / 2500
        ):

            self.spawn_train()

            self.last_spawn = time.time()

        # Spawn coins
        if time.time() - self.last_coin_spawn > 2:

            self.spawn_coin_line()

            self.last_coin_spawn = time.time()

        # Update trains
        for train in self.trains:

            train.speed = self.speed
            train.update()

        # Update coins
        for coin in self.coins:

            coin.speed = self.speed + 0.002
            coin.update()

        # Collision
        player_rect = self.player.get_rect()

        for train in self.trains:

            if train.distance > 0.78:

                if train.lane == self.player.lane:

                    train_rect = train.get_rect()

                    if player_rect.colliderect(train_rect):

                        self.lives -= 1

                        train.distance = 2

                        if self.lives <= 0:

                            self.game_over = True

        # Coins
        for coin in self.coins:

            if coin.collected:
                continue

            if coin.distance > 0.65:

                if coin.lane == self.player.lane:

                    if player_rect.colliderect(
                        coin.get_rect()
                    ):

                        coin.collected = True

                        self.coins_collected += 1

                        self.score += 100

        # Remove objects
        self.trains = [
            train
            for train in self.trains
            if train.distance < 1.2
        ]

        self.coins = [
            coin
            for coin in self.coins
            if coin.distance < 1.2
            and not coin.collected
        ]

        self.score += 1

    def draw_hud(self):

        score_text = font_medium.render(
            f"SCORE: {self.score}",
            True,
            WHITE
        )

        coin_text = font_medium.render(
            f"COINS: {self.coins_collected}",
            True,
            YELLOW
        )

        lives_text = font_medium.render(
            f"LIVES: {self.lives}",
            True,
            (255, 100, 100)
        )

        screen.blit(score_text, (25, 20))
        screen.blit(coin_text, (25, 60))
        screen.blit(lives_text, (25, 100))

        # Gesture information
        gesture = font_small.render(
            self.gesture_text,
            True,
            WHITE
        )

        screen.blit(
            gesture,
            (
                WIDTH - gesture.get_width() - 20,
                20
            )
        )

    def draw_game_over(self):

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill((0, 0, 0, 180))

        screen.blit(
            overlay,
            (0, 0)
        )

        text = font_big.render(
            "GAME OVER",
            True,
            RED
        )

        screen.blit(
            text,
            (
                WIDTH // 2 - text.get_width() // 2,
                220
            )
        )

        score = font_medium.render(
            f"Final Score: {self.score}",
            True,
            WHITE
        )

        screen.blit(
            score,
            (
                WIDTH // 2 - score.get_width() // 2,
                300
            )
        )

        # Restart button
        restart_rect = pygame.Rect(
            WIDTH // 2 - 150,
            390,
            300,
            65
        )

        pygame.draw.rect(
            screen,
            GREEN,
            restart_rect,
            border_radius=12
        )

        restart_text = font_medium.render(
            "RESTART",
            True,
            BLACK
        )

        screen.blit(
            restart_text,
            restart_text.get_rect(
                center=restart_rect.center
            )
        )

        # Quit button
        quit_rect = pygame.Rect(
            WIDTH // 2 - 150,
            480,
            300,
            65
        )

        pygame.draw.rect(
            screen,
            RED,
            quit_rect,
            border_radius=12
        )

        quit_text = font_medium.render(
            "QUIT",
            True,
            WHITE
        )

        screen.blit(
            quit_text,
            quit_text.get_rect(
                center=quit_rect.center
            )
        )

        return restart_rect, quit_rect

    def draw(self):

        # Background
        draw_sky()

        draw_cloud(120, 90, 1)
        draw_cloud(700, 60, 0.8)
        draw_cloud(430, 125, 0.7)

        draw_background_buildings()

        draw_poles()

        draw_railway()

        # Coins behind trains
        for coin in self.coins:
            coin.draw()

        # Trains
        for train in self.trains:
            train.draw()

        # Player
        self.player.draw()

        # HUD
        self.draw_hud()

        if self.game_over:

            return self.draw_game_over()

        return None


# ============================================================
# MEDIAPIPE HAND CONTROL
# ============================================================

def process_hand(frame, game):

    frame_rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    result = hands.process(frame_rgb)

    if not result.multi_hand_landmarks:
        return

    hand = result.multi_hand_landmarks[0]

    # Draw landmarks
    mp_draw.draw_landmarks(
        frame,
        hand,
        mp_hands.HAND_CONNECTIONS
    )

    wrist = hand.landmark[
        mp_hands.HandLandmark.WRIST
    ]

    index = hand.landmark[
        mp_hands.HandLandmark.INDEX_FINGER_TIP
    ]

    middle = hand.landmark[
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP
    ]

    x = index.x
    y = index.y

    current_time = time.time()

    if current_time - game.last_hand_action < game.hand_cooldown:

        return

    # ----------------------------------------
    # LEFT
    # ----------------------------------------

    if x < 0.30:

        game.player.move_left()

        game.gesture_text = "HAND: LEFT"

        game.last_hand_action = current_time

        return

    # ----------------------------------------
    # RIGHT
    # ----------------------------------------

    if x > 0.70:

        game.player.move_right()

        game.gesture_text = "HAND: RIGHT"

        game.last_hand_action = current_time

        return

    # ----------------------------------------
    # JUMP
    # ----------------------------------------

    if y < 0.30:

        game.player.jump()

        game.gesture_text = "HAND: JUMP"

        game.last_hand_action = current_time

        return

    # ----------------------------------------
    # SLIDE
    # ----------------------------------------

    if y > 0.75:

        game.player.slide()

        game.gesture_text = "HAND: SLIDE"

        game.last_hand_action = current_time


# ============================================================
# MAIN LOOP
# ============================================================

def main():

    game = Game()

    running = True

    while running:

        clock.tick(FPS)

        # ----------------------------------------------------
        # EVENTS
        # ----------------------------------------------------

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    running = False

                if event.key == pygame.K_LEFT:

                    game.player.move_left()

                if event.key == pygame.K_RIGHT:

                    game.player.move_right()

                if event.key == pygame.K_UP:

                    game.player.jump()

                if event.key == pygame.K_DOWN:

                    game.player.slide()

                if event.key == pygame.K_r:

                    game.reset()

                if event.key == pygame.K_q:

                    running = False

            # Game over buttons
            if event.type == pygame.MOUSEBUTTONDOWN:

                if game.game_over:

                    restart_rect, quit_rect = game.draw()

                    if restart_rect.collidepoint(event.pos):

                        game.reset()

                    if quit_rect.collidepoint(event.pos):

                        running = False

        # ----------------------------------------------------
        # CAMERA
        # ----------------------------------------------------

        if camera.isOpened():

            ret, frame = camera.read()

            if ret:

                frame = cv2.flip(
                    frame,
                    1
                )

                process_hand(
                    frame,
                    game
                )

                # Camera display
                cv2.putText(
                    frame,
                    "Hand Control",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )

                cv2.imshow(
                    "MediaPipe Camera",
                    frame
                )

                # OpenCV quit
                if cv2.waitKey(1) & 0xFF == ord("q"):

                    running = False

        # ----------------------------------------------------
        # GAME UPDATE
        # ----------------------------------------------------

        game.update()

        # ----------------------------------------------------
        # DRAW
        # ----------------------------------------------------

        game.draw()

        pygame.display.flip()

    # --------------------------------------------------------
    # CLEANUP
    # --------------------------------------------------------

    camera.release()

    cv2.destroyAllWindows()

    pygame.quit()

    sys.exit()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()