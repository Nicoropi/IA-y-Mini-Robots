import pygame
import math
import random
import sys

# --- Config ---
WIDTH, HEIGHT = 800, 600
FPS = 60
NUM_OBSTACLES = 4
ROBOT_RADIUS = 15
SENSOR_RANGE = 120
SENSOR_ANGLES = [-0.5, 0, 0.5]  # Izq, Centro, Der (rads)
MAX_SPEED = 3.0
BASE_SPEED = 2.0
OBSTACLE_SIZE_MIN = 40
OBSTACLE_SIZE_MAX = 80
WALL_THICKNESS = 12

ARENA_MARGIN = 20
ARENA_TOP = 70  # franja superior para el HUD
ARENA = pygame.Rect(
    ARENA_MARGIN,
    ARENA_TOP,
    WIDTH - 2 * ARENA_MARGIN,
    HEIGHT - ARENA_TOP - ARENA_MARGIN,
)

# --- Colores ---
BG = (240, 240, 240)
ROBOT_COLOR = (50, 120, 200)
WHEEL_COLOR = (30, 30, 30)
SENSOR_COLOR = (220, 50, 50, 160)
SENSOR_HIT_COLOR = (50, 220, 50)
OBSTACLE_COLOR = (180, 60, 60)
WALL_COLOR = (90, 90, 90)
WALL_BORDER = (50, 50, 50)
TEXT_COLOR = (40, 40, 40)


class Obstaculo:
    def __init__(self, x, y, w, h, color=OBSTACLE_COLOR, border=(120, 30, 30)):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.border = border

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, self.border, self.rect, 2)


class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.theta = 0.0
        self.vl = 0.0  # velocidad rueda izquierda
        self.vr = 0.0  # velocidad rueda derecha
        self.wheel_base = ROBOT_RADIUS * 1.8

    def set_vl(self, v):
        self.vl = max(-MAX_SPEED, min(MAX_SPEED, v))

    def set_vr(self, v):
        self.vr = max(-MAX_SPEED, min(MAX_SPEED, v))

    def apply_diff_drive(self):
        self.theta += (self.vr - self.vl) / self.wheel_base
        speed = (self.vl + self.vr) / 2.0
        self.x += speed * math.cos(self.theta)
        self.y += speed * math.sin(self.theta)

        self.x = max(ARENA.left + ROBOT_RADIUS, min(ARENA.right - ROBOT_RADIUS, self.x))
        self.y = max(ARENA.top + ROBOT_RADIUS, min(ARENA.bottom - ROBOT_RADIUS, self.y))

    def get_sensor_readings(self, obstaculos):
        readings = []
        for angle_offset in SENSOR_ANGLES:
            ray_angle = self.theta + angle_offset
            rx = self.x + ROBOT_RADIUS * math.cos(ray_angle)
            ry = self.y + ROBOT_RADIUS * math.sin(ray_angle)
            dx = math.cos(ray_angle)
            dy = math.sin(ray_angle)
            min_dist = SENSOR_RANGE
            hit = False
            for obs in obstaculos:
                dist = ray_vs_rect(rx, ry, dx, dy, obs.rect)
                if dist is not None and dist < min_dist:
                    min_dist = dist
                    hit = True
            readings.append((min_dist, hit))
        return readings

    def draw(self, surface):
        # Cuerpo
        pygame.draw.circle(surface, ROBOT_COLOR, (int(self.x), int(self.y)), ROBOT_RADIUS)
        pygame.draw.circle(surface, (30, 80, 150), (int(self.x), int(self.y)), ROBOT_RADIUS, 2)

        # Direccion
        ex = self.x + ROBOT_RADIUS * math.cos(self.theta)
        ey = self.y + ROBOT_RADIUS * math.sin(self.theta)
        pygame.draw.line(surface, (255, 255, 255), (int(self.x), int(self.y)), (int(ex), int(ey)), 3)

        # Ruedas
        for side in [-1, 1]:
            wx = self.x + side * ROBOT_RADIUS * 0.9 * math.cos(self.theta + math.pi / 2)
            wy = self.y + side * ROBOT_RADIUS * 0.9 * math.sin(self.theta + math.pi / 2)
            pygame.draw.circle(surface, WHEEL_COLOR, (int(wx), int(wy)), 5)

    def draw_sensors(self, surface, readings):
        for i, (dist, hit) in enumerate(readings):
            ray_angle = self.theta + SENSOR_ANGLES[i]
            rx = self.x + ROBOT_RADIUS * math.cos(ray_angle)
            ry = self.y + ROBOT_RADIUS * math.sin(ray_angle)
            end_x = rx + dist * math.cos(ray_angle)
            end_y = ry + dist * math.sin(ray_angle)
            color = SENSOR_HIT_COLOR if hit else SENSOR_COLOR
            pygame.draw.line(surface, color, (int(rx), int(ry)), (int(end_x), int(end_y)), 2)


def ray_vs_rect(ox, oy, dx, dy, rect):
    inv_dx = 1.0 / dx if dx != 0 else float('inf')
    inv_dy = 1.0 / dy if dy != 0 else float('inf')

    t1 = (rect.left - ox) * inv_dx
    t2 = (rect.right - ox) * inv_dx
    t3 = (rect.top - oy) * inv_dy
    t4 = (rect.bottom - oy) * inv_dy

    tmin = max(min(t1, t2), min(t3, t4))
    tmax = min(max(t1, t2), max(t3, t4))

    if tmax < 0:
        return None
    if tmin > tmax:
        return None
    if tmin < 0:
        tmin = tmax
    if tmin < 0:
        return None
    return tmin


def generar_paredes():
    a, rango, t = ARENA, ARENA.right, WALL_THICKNESS
    return [
        Obstaculo(a.left, a.top, a.width, t, color=WALL_COLOR, border=WALL_BORDER),
        Obstaculo(a.left, a.bottom - t, a.width, t, color=WALL_COLOR, border=WALL_BORDER),
        Obstaculo(a.left, a.top, t, a.height, color=WALL_COLOR, border=WALL_BORDER),
        Obstaculo(rango - t, a.top, t, a.height, color=WALL_COLOR, border=WALL_BORDER),
    ]


def generar_obstaculos(exclude=None):
    obstaculos = []
    tries = 0
    while len(obstaculos) < NUM_OBSTACLES and tries < 200:
        w = random.randint(OBSTACLE_SIZE_MIN, OBSTACLE_SIZE_MAX)
        h = random.randint(OBSTACLE_SIZE_MIN, OBSTACLE_SIZE_MAX)
        x = random.randint(50, WIDTH - w - 50)
        y = random.randint(50, HEIGHT - h - 50)
        r = pygame.Rect(x, y, w, h)
        if exclude and r.inflate(60, 60).colliderect(exclude):
            tries += 1
            continue
        obstaculos.append(Obstaculo(x, y, w, h))
        tries += 1
    return obstaculos


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Robot Evitador de Obstaculos - Braitenberg")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 16)

    robot_start = pygame.Rect(WIDTH // 2 - 20, HEIGHT // 2 - 20, 40, 40)
    robot = Robot(WIDTH // 2, HEIGHT // 2)
    paredes = generar_paredes()
    obstaculos = paredes + generar_obstaculos(exclude=robot_start)

    paused = False
    show_sensors = True

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    robot = Robot(WIDTH // 2, HEIGHT // 2)
                    obstaculos = paredes + generar_obstaculos(exclude=robot_start)
                elif event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_s:
                    show_sensors = not show_sensors

        readings = robot.get_sensor_readings(obstaculos)

        if not paused:
            left_dist, left_hit = readings[0]
            center_dist, center_hit = readings[1]
            right_dist, right_hit = readings[2]

            if left_hit and center_hit and right_hit:
                vl = 0.0
                vr = BASE_SPEED
            else:
                norm_left = 1.0 - left_dist / SENSOR_RANGE
                norm_right = 1.0 - right_dist / SENSOR_RANGE
                norm_center = 1.0 - center_dist / SENSOR_RANGE

                vl = BASE_SPEED - norm_left * 2.5 - norm_center * 1.5
                vr = BASE_SPEED - norm_right * 2.5 - norm_center * 1.5

            robot.set_vl(vl)
            robot.set_vr(vr)
            robot.apply_diff_drive()

            readings = robot.get_sensor_readings(obstaculos)

        screen.fill(BG)

        for obs in obstaculos:
            obs.draw(screen)

        if show_sensors:
            robot.draw_sensors(screen, readings)
        robot.draw(screen)

        # HUD
        texts = [
            f"P={('PAUSA' if paused else 'PLAY')}  R=Reset  S=Sensores",
            f"Theta: {math.degrees(robot.theta):.0f}  Pos: ({robot.x:.0f}, {robot.y:.0f})",
            f"Sensores [L/C/R]: {readings[0][0]:.0f} / {readings[1][0]:.0f} / {readings[2][0]:.0f}",
        ]
        for i, t in enumerate(texts):
            surf = font.render(t, True, TEXT_COLOR)
            screen.blit(surf, (10, 10 + i * 20))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
