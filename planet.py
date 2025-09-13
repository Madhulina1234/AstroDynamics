import pygame
import math

pygame.init()

# --- Window setup ---
WIDTH, HEIGHT = 1800, 1000
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Planet Simulation with Zoom + Distances (km)")

# --- Colors ---
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
RED = (188, 39, 50)
DARK_GREY = (80, 78, 81)
ORANGE = (255, 165, 0)
LIGHT_BROWN = (210, 180, 140)
CYAN = (175, 238, 238)
DARK_BLUE = (72, 61, 139)
RING_COLOR = (200, 200, 200)

# --- Log-scale config ---
MAX_AU = 30.07       # Neptune’s semi-major axis (AU)
MARGIN = 40
HALF_W = WIDTH / 2
HALF_H = HEIGHT / 2
K_LOG = (HALF_W - MARGIN) / math.log10(MAX_AU + 1)

# --- Fonts ---
FONT = pygame.font.SysFont("comicsans", 16)

# --- Planet class ---
class Planet:
    AU = 149.6e6 * 1000       # meters
    G = 6.67428e-11
    TIMESTEP = 3600 * 24      # 1 day per frame

    def __init__(self, x, y, radius, color, mass, has_ring=False):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass
        self.has_ring = has_ring

        self.orbit = []
        self.sun = False
        self.distance_to_sun = 0

        self.x_vel = 0
        self.y_vel = 0

    def attraction(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        distance = math.sqrt(dx**2 + dy**2)   # FIXED

        if other.sun:
            self.distance_to_sun = distance

        force = Planet.G * self.mass * other.mass / distance**2
        theta = math.atan2(dy, dx)
        fx = math.cos(theta) * force
        fy = math.sin(theta) * force
        return fx, fy

    def update_position(self, planets):
        total_fx = total_fy = 0
        for planet in planets:
            if self == planet:
                continue
            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy

        self.x_vel += total_fx / self.mass * Planet.TIMESTEP
        self.y_vel += total_fy / self.mass * Planet.TIMESTEP

        self.x += self.x_vel * Planet.TIMESTEP
        self.y += self.y_vel * Planet.TIMESTEP
        self.orbit.append((self.x, self.y))

    def _log_scaled_pos(self, zoom):
        r_m = math.hypot(self.x, self.y)
        if r_m == 0:
            return int(HALF_W), int(HALF_H)
        r_au = r_m / self.AU
        r_px = (K_LOG * math.log10(r_au + 1)) * zoom
        angle = math.atan2(self.y, self.x)
        sx = int(HALF_W + r_px * math.cos(angle))
        sy = int(HALF_H + r_px * math.sin(angle))
        return sx, sy

    def _log_scaled_pos_from(self, pos, zoom):
        px, py = pos
        r_m = math.hypot(px, py)
        if r_m == 0:
            return int(HALF_W), int(HALF_H)
        r_au = r_m / self.AU
        r_px = (K_LOG * math.log10(r_au + 1)) * zoom
        angle = math.atan2(py, px)
        sx = int(HALF_W + r_px * math.cos(angle))
        sy = int(HALF_H + r_px * math.sin(angle))
        return sx, sy

    def draw(self, win, zoom):
        x, y = self._log_scaled_pos(zoom)

        # Orbit path
        if len(self.orbit) > 2:
            scaled_points = []
            for pos in self.orbit[-400:]:
                sx, sy = self._log_scaled_pos_from(pos, zoom)
                scaled_points.append((sx, sy))
            if len(scaled_points) > 2:
                pygame.draw.lines(win, self.color, False, scaled_points, 1)

        # Saturn ring
        if self.has_ring:
            ring_width = self.radius * 4
            ring_height = self.radius * 2
            ring_rect = pygame.Rect(
                x - ring_width // 2,
                y - ring_height // 2,
                ring_width,
                ring_height
            )
            pygame.draw.ellipse(win, RING_COLOR, ring_rect, 2)

        # Planet
        pygame.draw.circle(win, self.color, (x, y), self.radius)

        # Distance text in km
        if not self.sun:
            dist_km = int(self.distance_to_sun / 1000)
            dist_text = f"{dist_km:,} km"
            text_surface = FONT.render(dist_text, True, (0, 0, 0))
            win.blit(text_surface, (x + self.radius + 4, y - self.radius))


def main():
    run = True
    clock = pygame.time.Clock()
    zoom = 1.0

    # Sun
    sun = Planet(0, 0, 30, YELLOW, 1.98892 * 10**30)
    sun.sun = True

    # Planets
    mercury = Planet(0.387 * Planet.AU, 0, 6, DARK_GREY, 0.330 * 10**24)
    venus   = Planet(0.723 * Planet.AU, 0, 10, ORANGE, 4.8685 * 10**24)
    earth   = Planet(1 * Planet.AU, 0, 12, BLUE, 5.9742 * 10**24)
    mars    = Planet(1.524 * Planet.AU, 0, 8, RED, 6.39 * 10**23)
    jupiter = Planet(5.203 * Planet.AU, 0, 20, LIGHT_BROWN, 1.898 * 10**27)
    saturn  = Planet(9.537 * Planet.AU, 0, 18, ORANGE, 5.683 * 10**26, has_ring=True)
    uranus  = Planet(19.191 * Planet.AU, 0, 14, CYAN, 8.681 * 10**25)
    neptune = Planet(30.07 * Planet.AU, 0, 14, DARK_BLUE, 1.024 * 10**26)

    # Orbital velocities (km/s → m/s)
    mercury.y_vel = -47.4 * 1000
    venus.y_vel   = -35.0 * 1000
    earth.y_vel   = -29.8 * 1000
    mars.y_vel    = -24.1 * 1000
    jupiter.y_vel = -13.1 * 1000
    saturn.y_vel  = -9.7 * 1000
    uranus.y_vel  = -6.8 * 1000
    neptune.y_vel = -5.4 * 1000

    planets = [sun, mercury, venus, earth, mars, jupiter, saturn, uranus, neptune]

    while run:
        clock.tick(60)
        WIN.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # scroll up
                    zoom *= 1.1
                elif event.button == 5:  # scroll down
                    zoom /= 1.1

        for planet in planets:
            if not planet.sun:
                planet.update_position(planets)
            planet.draw(WIN, zoom)

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
