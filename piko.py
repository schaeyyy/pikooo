import pygame
import math
import sys

pygame.init()

# =========================================================
# WINDOW
# =========================================================
WIDTH = 900
HEIGHT = 750

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PIKO - Digital Filipino Traditional Game")

CLOCK = pygame.time.Clock()
FPS = 60

# =========================================================
# COLORS
# =========================================================
BG = (245, 235, 210)
LINE = (45, 35, 30)
BOX_COLOR = (255, 245, 220)
TARGET_COLOR = (255, 220, 120)
PAMATO_COLOR = (245, 170, 170)

PLAYER_COLOR = (90, 150, 230)
PATO_COLOR = (70, 70, 70)

WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
GREEN = (70, 160, 90)
RED = (200, 60, 60)

FONT = pygame.font.SysFont("arial", 24)
SMALL_FONT = pygame.font.SysFont("arial", 18)
BIG_FONT = pygame.font.SysFont("arial", 44, bold=True)

# =========================================================
# BOARD
# =========================================================
BOX_W = 120
BOX_H = 62

CENTER_X = WIDTH // 2

LEFT_X = CENTER_X - BOX_W - 8
RIGHT_X = CENTER_X + 8

boxes = {
    1: pygame.Rect(
        CENTER_X - BOX_W // 2,
        610,
        BOX_W,
        BOX_H
    ),

    2: pygame.Rect(
        LEFT_X,
        545,
        BOX_W,
        BOX_H
    ),

    3: pygame.Rect(
        RIGHT_X,
        545,
        BOX_W,
        BOX_H
    ),

    4: pygame.Rect(
        CENTER_X - BOX_W // 2,
        480,
        BOX_W,
        BOX_H
    ),

    5: pygame.Rect(
        LEFT_X,
        415,
        BOX_W,
        BOX_H
    ),

    6: pygame.Rect(
        RIGHT_X,
        415,
        BOX_W,
        BOX_H
    ),

    7: pygame.Rect(
        CENTER_X - BOX_W // 2,
        350,
        BOX_W,
        BOX_H
    ),

    8: pygame.Rect(
        LEFT_X,
        285,
        BOX_W,
        BOX_H
    ),

    9: pygame.Rect(
        RIGHT_X,
        285,
        BOX_W,
        BOX_H
    ),

    10: pygame.Rect(
        CENTER_X - BOX_W // 2,
        220,
        BOX_W,
        BOX_H
    )
}

# =========================================================
# PLAYER
# =========================================================
PLAYER_SIZE = 28

START_X = CENTER_X - PLAYER_SIZE // 2
START_Y = 675

player = pygame.Rect(
    START_X,
    START_Y,
    PLAYER_SIZE,
    PLAYER_SIZE
)

player_x = float(START_X)
player_y = float(START_Y)

# =========================================================
# GAME
# =========================================================
ROUND = 1
LIVES = 3
SCORE = 0

STATE = "THROW"

pamato_box = ROUND

# =========================================================
# MESSAGE
# =========================================================
message = ""
message_timer = 0


def set_message(text, frames=70):
    global message
    global message_timer

    message = text
    message_timer = frames


# =========================================================
# RESET PLAYER
# =========================================================
def reset_player():

    global player_x
    global player_y

    player_x = float(START_X)
    player_y = float(START_Y)

    player.topleft = (
        round(player_x),
        round(player_y)
    )


# =========================================================
# LOSE LIFE
# =========================================================
def lose_life(reason):

    global LIVES
    global STATE

    global jumping
    global throw_charging
    global pato_active

    LIVES -= 1

    jumping = False
    throw_charging = False
    pato_active = False

    if LIVES <= 0:

        STATE = "GAMEOVER"

        set_message(
            "GAME OVER",
            120
        )

    else:

        STATE = "THROW"

        set_message(
            reason + " Try again!",
            100
        )

        reset_player()


# =========================================================
# ROUND ROUTE
# =========================================================
route = []
route_index = 0


def make_route():

    global route
    global route_index

    # Go upward while skipping the pamato box.
    outbound = [
        number
        for number in range(1, 11)
        if number != pamato_box
    ]

    # Return downward.
    return_route = outbound[-2::-1]

    route = outbound + return_route

    route_index = 0


# =========================================================
# START ROUND
# =========================================================
def start_round():

    global pamato_box
    global STATE

    global throw_power
    global throw_charging
    global pato_active
    global aim_offset

    global jumping
    global jump_charge

    pamato_box = ROUND

    throw_power = 0.0
    throw_charging = False

    pato_active = False

    aim_offset = 0.0

    jumping = False
    jump_charge = 0.0

    reset_player()

    STATE = "THROW"


# =========================================================
# THROW SYSTEM
# =========================================================
throw_charging = False
throw_power = 0.0

THROW_MIN = 7.0
THROW_MAX = 18.0
THROW_CHARGE_SPEED = 0.22

THROW_IDEAL = 13.0

aim_offset = 0.0

pato_active = False

pato_x = float(START_X)
pato_y = float(START_Y)

pato_start_x = 0.0
pato_start_y = 0.0

pato_end_x = 0.0
pato_end_y = 0.0

pato_t = 0.0


def start_throw():

    global pato_active

    global pato_start_x
    global pato_start_y

    global pato_end_x
    global pato_end_y

    global pato_t
    global throw_charging

    target = boxes[pamato_box]

    start_x = player.centerx
    start_y = player.centery

    # -----------------------------------------------------
    # POWER AFFECTS DISTANCE
    # -----------------------------------------------------
    ratio = throw_power / THROW_IDEAL

    target_x = target.centerx + aim_offset
    target_y = target.centery

    pato_start_x = float(start_x)
    pato_start_y = float(start_y)

    pato_end_x = (
        start_x +
        (target_x - start_x) * ratio
    )

    pato_end_y = (
        start_y +
        (target_y - start_y) * ratio
    )

    pato_t = 0.0

    pato_active = True
    throw_charging = False


def update_throw():

    global throw_power
    global pato_t
    global pato_active

    # -----------------------------------------------------
    # CHARGE THROW
    # -----------------------------------------------------
    if throw_charging:

        throw_power += THROW_CHARGE_SPEED

        if throw_power > THROW_MAX:

            throw_power = THROW_MIN

    # -----------------------------------------------------
    # PATO FLIGHT
    # -----------------------------------------------------
    if pato_active:

        pato_t += 0.035

        if pato_t >= 1.0:

            pato_t = 1.0

            target = boxes[pamato_box]

            # Smaller landing zone
            landing_area = target.inflate(
                -16,
                -16
            )

            landed = landing_area.collidepoint(
                round(pato_end_x),
                round(pato_end_y)
            )

            pato_active = False

            if landed:

                begin_play()

            else:

                lose_life(
                    "Pato missed."
                )


def begin_play():

    global STATE

    make_route()

    reset_player()

    STATE = "PLAY"

    set_message(
        "Hop to Box " + str(route[route_index]),
        90
    )


# =========================================================
# JUMP SYSTEM
# =========================================================
jumping = False

jump_charge = 0.0

JUMP_MIN_POWER = 0.25
JUMP_MAX_POWER = 1.0

JUMP_CHARGE_SPEED = 0.1

# Horizontal movement
AIR_SPEED = 4.5

# Vertical jump
MIN_JUMP_HEIGHT = 75
MAX_JUMP_HEIGHT = 135

# Jump duration
MIN_JUMP_TIME = 38
MAX_JUMP_TIME = 52

jump_t = 0.0
jump_duration = 40.0

jump_start_x = 0.0
jump_start_y = 0.0

jump_velocity_x = 0.0
jump_height = 90.0


# =========================================================
# START JUMP
# =========================================================
def begin_jump():

    global jumping

    global jump_charge

    global jump_t
    global jump_duration

    global jump_start_x
    global jump_start_y

    global jump_velocity_x
    global jump_height

    if route_index >= len(route):
        return

    # -----------------------------------------------------
    # POWER
    # -----------------------------------------------------
    power = (
        JUMP_MIN_POWER +
        (
            JUMP_MAX_POWER -
            JUMP_MIN_POWER
        ) * jump_charge
    )

    # -----------------------------------------------------
    # JUMP HEIGHT
    # -----------------------------------------------------
    jump_height = (
        MIN_JUMP_HEIGHT +
        (
            MAX_JUMP_HEIGHT -
            MIN_JUMP_HEIGHT
        ) * power
    )

    # -----------------------------------------------------
    # JUMP TIME
    # -----------------------------------------------------
    jump_duration = (
        MIN_JUMP_TIME +
        (
            MAX_JUMP_TIME -
            MIN_JUMP_TIME
        ) * power
    )

    jump_start_x = float(player_x)
    jump_start_y = float(player_y)

    # -----------------------------------------------------
    # INITIAL HORIZONTAL VELOCITY
    # -----------------------------------------------------
    keys = pygame.key.get_pressed()

    jump_velocity_x = 0.0

    if keys[pygame.K_a]:

        jump_velocity_x = -AIR_SPEED

    elif keys[pygame.K_d]:

        jump_velocity_x = AIR_SPEED

    jump_t = 0.0

    jumping = True

    jump_charge = 0.0


# =========================================================
# UPDATE JUMP
# =========================================================
def update_jump(keys):

    global jump_charge
    global jumping

    global jump_t

    global player_x
    global player_y

    global jump_velocity_x

    global route_index

    # =====================================================
    # CHARGE
    # =====================================================
    if not jumping:

        if keys[pygame.K_SPACE]:

            jump_charge += JUMP_CHARGE_SPEED

            if jump_charge > 1.0:

                jump_charge = 0.0

        return

    # =====================================================
    # AIR CONTROL
    # =====================================================
    if keys[pygame.K_a]:

        jump_velocity_x -= 0.45

    if keys[pygame.K_d]:

        jump_velocity_x += 0.45

    # Limit horizontal speed
    jump_velocity_x = max(
        -AIR_SPEED,
        min(
            AIR_SPEED,
            jump_velocity_x
        )
    )

    # Move horizontally
    player_x += jump_velocity_x

    # Keep player inside screen
    if player_x < 20:

        player_x = 20
        jump_velocity_x = 0

    if player_x > WIDTH - PLAYER_SIZE - 20:

        player_x = WIDTH - PLAYER_SIZE - 20
        jump_velocity_x = 0

    # =====================================================
    # JUMP PROGRESS
    # =====================================================
    jump_t += 1.0 / jump_duration

    if jump_t >= 1.0:

        jump_t = 1.0

        # -------------------------------------------------
        # END OF JUMP
        # -------------------------------------------------
        target_number = route[route_index]
        target = boxes[target_number]

        # Player position remains where YOU controlled it.
        player_y = float(
            target.centery -
            PLAYER_SIZE // 2
        )

        player.topleft = (
            round(player_x),
            round(player_y)
        )

        jumping = False

        # -------------------------------------------------
        # STRICTER CENTER LANDING
        # -------------------------------------------------
        center_margin_x = 30
        center_margin_y = 18

        safe_area = pygame.Rect(
            target.left + center_margin_x,
            target.top + center_margin_y,
            target.width - center_margin_x * 2,
            target.height - center_margin_y * 2
        )

        player_center = (
            player.centerx,
            player.centery
        )

        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------
        if safe_area.collidepoint(player_center):

            route_index += 1

            if route_index >= len(route):

                complete_round()

            else:

                set_message(
                    "Good! Next: Box " +
                    str(route[route_index]),
                    45
                )

        # -------------------------------------------------
        # FAIL
        # -------------------------------------------------
        else:

            lose_life(
                "You missed the center!"
            )


# =========================================================
# COMPLETE ROUND
# =========================================================
def complete_round():

    global ROUND
    global SCORE
    global STATE

    SCORE += 100

    if ROUND >= 10:

        STATE = "WIN"

        set_message(
            "YOU FINISHED ALL 10 ROUNDS!",
            180
        )

        return

    ROUND += 1

    start_round()

    set_message(
        "Round " + str(ROUND),
        90
    )


# =========================================================
# PLAYER VISUAL
# =========================================================
def update_player_visual():

    if jumping:

        t = max(
            0.0,
            min(
                1.0,
                jump_t
            )
        )

        # -------------------------------------------------
        # Horizontal position is manually controlled
        # -------------------------------------------------
        visual_x = player_x

        # -------------------------------------------------
        # Vertical arc
        # -------------------------------------------------
        base_y = (
            jump_start_y +
            (
                player_y -
                jump_start_y
            ) * t
        )

        arc = (
            jump_height *
            math.sin(
                math.pi * t
            )
        )

        visual_y = base_y - arc

        player.x = round(visual_x)
        player.y = round(visual_y)

    else:

        player.x = round(player_x)
        player.y = round(player_y)


# =========================================================
# DRAW BOARD
# =========================================================
def draw_board():

    for number, rect in boxes.items():

        color = BOX_COLOR

        # Pamato box
        if number == pamato_box:

            color = PAMATO_COLOR

        # Current target
        if (
            STATE == "PLAY"
            and route_index < len(route)
            and number == route[route_index]
        ):

            color = TARGET_COLOR

        pygame.draw.rect(
            SCREEN,
            color,
            rect
        )

        pygame.draw.rect(
            SCREEN,
            LINE,
            rect,
            3
        )

        # -------------------------------------------------
        # CENTER LANDING MARK
        # -------------------------------------------------
        if (
            STATE == "PLAY"
            and route_index < len(route)
            and number == route[route_index]
        ):

            center_x = rect.centerx
            center_y = rect.centery

            pygame.draw.circle(
                SCREEN,
                GREEN,
                (center_x, center_y),
                20

            )

        number_text = FONT.render(
            str(number),
            True,
            LINE
        )

        number_rect = number_text.get_rect(
            center=rect.center
        )

        SCREEN.blit(
            number_text,
            number_rect
        )

    # START LINE
    pygame.draw.line(
        SCREEN,
        LINE,
        (CENTER_X - 100, 700),
        (CENTER_X + 100, 700),
        4
    )

    start_text = SMALL_FONT.render(
        "START",
        True,
        LINE
    )

    SCREEN.blit(
        start_text,
        start_text.get_rect(
            center=(CENTER_X, 720)
        )
    )


# =========================================================
# DRAW THROW ARROW
# =========================================================
def draw_throw_arrow():

    target = boxes[pamato_box]

    start_x = player.centerx
    start_y = player.centery

    target_x = target.centerx + aim_offset
    target_y = target.centery

    pygame.draw.line(
        SCREEN,
        RED,
        (start_x, start_y),
        (target_x, target_y),
        3
    )

    angle = math.atan2(
        target_y - start_y,
        target_x - start_x
    )

    size = 12

    p1 = (
        target_x,
        target_y
    )

    p2 = (
        target_x -
        size * math.cos(
            angle - math.pi / 6
        ),
        target_y -
        size * math.sin(
            angle - math.pi / 6
        )
    )

    p3 = (
        target_x -
        size * math.cos(
            angle + math.pi / 6
        ),
        target_y -
        size * math.sin(
            angle + math.pi / 6
        )
    )

    pygame.draw.polygon(
        SCREEN,
        RED,
        [p1, p2, p3]
    )


# =========================================================
# DRAW PATO
# =========================================================
def draw_pato():

    if not pato_active:
        return

    t = pato_t

    x = (
        pato_start_x +
        (
            pato_end_x -
            pato_start_x
        ) * t
    )

    y = (
        pato_start_y +
        (
            pato_end_y -
            pato_start_y
        ) * t
    )

    arc = (
        90 *
        math.sin(
            math.pi * t
        )
    )

    y -= arc

    pygame.draw.circle(
        SCREEN,
        PATO_COLOR,
        (round(x), round(y)),
        10
    )


# =========================================================
# DRAW UI
# =========================================================
def draw_ui():

    title = BIG_FONT.render(
        "PIKO",
        True,
        BLACK
    )

    SCREEN.blit(
        title,
        (30, 20)
    )

    round_text = FONT.render(
        f"Round: {ROUND}/10",
        True,
        BLACK
    )

    lives_text = FONT.render(
        f"Lives: {LIVES}",
        True,
        BLACK
    )

    score_text = FONT.render(
        f"Score: {SCORE}",
        True,
        BLACK
    )

    SCREEN.blit(
        round_text,
        (30, 75)
    )

    SCREEN.blit(
        lives_text,
        (30, 110)
    )

    SCREEN.blit(
        score_text,
        (30, 145)
    )

    # =====================================================
    # THROW UI
    # =====================================================
    if STATE == "THROW":

        instructions = SMALL_FONT.render(
            "A/D = Aim | Hold SPACE = Charge | Release = Throw",
            True,
            BLACK
        )

        SCREEN.blit(
            instructions,
            (250, 30)
        )

        power_text = SMALL_FONT.render(
            f"Throw Power: {throw_power:.1f}   "
            f"Target: Box {pamato_box}",
            True,
            BLACK
        )

        SCREEN.blit(
            power_text,
            (250, 55)
        )

    # =====================================================
    # PLAY UI
    # =====================================================
    elif STATE == "PLAY":

        instructions = SMALL_FONT.render(
            "A/D = Move | Hold SPACE = Charge Hop | Release = Jump",
            True,
            BLACK
        )

        SCREEN.blit(
            instructions,
            (250, 30)
        )

        next_box = route[route_index]

        power_text = SMALL_FONT.render(
            f"Jump Power: {jump_charge * 100:.0f}%   "
            f"Target: Box {next_box}",
            True,
            BLACK
        )

        SCREEN.blit(
            power_text,
            (250, 55)
        )

        center_text = SMALL_FONT.render(
            "Land near the GREEN center!",
            True,
            GREEN
        )

        SCREEN.blit(
            center_text,
            (250, 80)
        )

    # =====================================================
    # MESSAGE
    # =====================================================
    if message_timer > 0:

        color = GREEN

        if (
            "miss" in message.lower()
            or "game" in message.lower()
            or "center" in message.lower()
        ):

            color = RED

        msg = FONT.render(
            message,
            True,
            color
        )

        SCREEN.blit(
            msg,
            msg.get_rect(
                center=(
                    WIDTH // 2,
                    185
                )
            )
        )


# =========================================================
# END SCREEN
# =========================================================
def draw_end_screen():

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 140)
    )

    SCREEN.blit(
        overlay,
        (0, 0)
    )

    if STATE == "GAMEOVER":

        title = BIG_FONT.render(
            "GAME OVER",
            True,
            WHITE
        )

        info = FONT.render(
            "Press R to restart",
            True,
            WHITE
        )

    else:

        title = BIG_FONT.render(
            "YOU WIN!",
            True,
            WHITE
        )

        info = FONT.render(
            "All 10 rounds completed!",
            True,
            WHITE
        )

    SCREEN.blit(
        title,
        title.get_rect(
            center=(
                WIDTH // 2,
                320
            )
        )
    )

    SCREEN.blit(
        info,
        info.get_rect(
            center=(
                WIDTH // 2,
                380
            )
        )
    )


# =========================================================
# START GAME
# =========================================================
start_round()

# =========================================================
# MAIN LOOP
# =========================================================
running = True

while running:

    CLOCK.tick(FPS)

    # =====================================================
    # EVENTS
    # =====================================================
    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        # -------------------------------------------------
        # KEY DOWN
        # -------------------------------------------------
        if event.type == pygame.KEYDOWN:

            # ESC
            if event.key == pygame.K_ESCAPE:

                running = False

            # -------------------------------------------------
            # RESTART
            # -------------------------------------------------
            if (
                event.key == pygame.K_r
                and STATE in ("GAMEOVER", "WIN")
            ):

                ROUND = 1
                LIVES = 3
                SCORE = 0

                start_round()

            # -------------------------------------------------
            # THROW
            # -------------------------------------------------
            if STATE == "THROW":

                if (
                    event.key == pygame.K_SPACE
                    and not pato_active
                ):

                    throw_charging = True

                    if throw_power <= 0:

                        throw_power = THROW_MIN

            # -------------------------------------------------
            # JUMP
            # -------------------------------------------------
            elif STATE == "PLAY":

                if (
                    event.key == pygame.K_SPACE
                    and not jumping
                ):

                    jump_charge = 0.0

        # -------------------------------------------------
        # KEY UP
        # -------------------------------------------------
        if event.type == pygame.KEYUP:

            # THROW RELEASE
            if (
                STATE == "THROW"
                and event.key == pygame.K_SPACE
            ):

                if (
                    throw_charging
                    and not pato_active
                ):

                    throw_charging = False

                    start_throw()

            # JUMP RELEASE
            elif (
                STATE == "PLAY"
                and event.key == pygame.K_SPACE
            ):

                if not jumping:

                    begin_jump()

    # =====================================================
    # KEYS
    # =====================================================
    keys = pygame.key.get_pressed()

    # =====================================================
    # AIM
    # =====================================================
    if (
        STATE == "THROW"
        and not pato_active
    ):

        if keys[pygame.K_a]:

            aim_offset -= 1.5

        if keys[pygame.K_d]:

            aim_offset += 1.5

        aim_offset = max(
            -45,
            min(
                45,
                aim_offset
            )
        )

    # =====================================================
    # UPDATE
    # =====================================================
    if STATE == "THROW":

        update_throw()

    elif STATE == "PLAY":

        update_jump(keys)

        update_player_visual()

    # =====================================================
    # MESSAGE TIMER
    # =====================================================
    if message_timer > 0:

        message_timer -= 1

    # =====================================================
    # DRAW
    # =====================================================
    SCREEN.fill(BG)

    draw_board()

    if STATE == "THROW":

        draw_throw_arrow()

    draw_pato()

    pygame.draw.rect(
        SCREEN,
        PLAYER_COLOR,
        player
    )

    pygame.draw.rect(
        SCREEN,
        LINE,
        player,
        2
    )

    draw_ui()

    if STATE in ("GAMEOVER", "WIN"):

        draw_end_screen()

    pygame.display.flip()


# =========================================================
# EXIT
# =========================================================
pygame.quit()
sys.exit()