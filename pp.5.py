import pygame
import math
import random

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Proactive Hazard Detection Simulation")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (169, 169, 169)  # Color for the lane

# Car settings
car_width, car_height = 50, 30
car_speed = 5
hazard_detection_range = 150  # Distance at which hazards are detected
hazard_stop_distance = 100   # Distance at which the vehicle should stop
avoidance_distance = 150      # Distance to move forward after changing lane
lane_y = HEIGHT // 2  # The y position for the lane

# Define car object
class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = car_speed
        self.angle = 0  # Direction the car is facing (0 degrees -> moving right)
        self.original_angle = 0
        self.avoiding_hazard = False
        self.lane_change_direction = 1  # 1 for down, -1 for up
        self.lane_change_distance_travelled = 0
        self.lane_change_state = 0  # 0 = moving forward, 1 = changing lane, 2 = returning to original path
        self.stopped = False

    def move(self):
        if self.stopped:
            self.stopped = False

        if self.avoiding_hazard:
            if self.lane_change_state == 1:
                # Move vertically (up or down) to avoid hazard
                self.y += self.speed * self.lane_change_direction
                self.lane_change_distance_travelled += self.speed
                if self.lane_change_distance_travelled >= avoidance_distance:
                    self.lane_change_state = 2
                    self.lane_change_distance_travelled = 0
            elif self.lane_change_state == 2:
                # Move forward while avoiding the hazard
                self.x += self.speed
                self.lane_change_distance_travelled += self.speed
                if self.lane_change_distance_travelled >= avoidance_distance:
                    self.lane_change_state = 3
                    self.lane_change_distance_travelled = 0
            elif self.lane_change_state == 3:
                # Return to the original lane
                self.y -= self.speed * self.lane_change_direction
                self.lane_change_distance_travelled += self.speed
                if abs(self.y - lane_y) < 5:  # If the car is almost back in the lane
                    self.y = lane_y  # Snap the car back to the lane
                    self.avoiding_hazard = False
                    self.lane_change_state = 0
        else:
            # Move straight forward in the lane if no hazards are detected
            self.x += self.speed

    def draw(self, screen):
        # Draw the car
        pygame.draw.rect(screen, GREEN, (self.x, self.y, car_width, car_height))

        # Draw hazard detection circle (always visible)
        pygame.draw.circle(screen, RED, (int(self.x + car_width // 2), int(self.y + car_height // 2)), hazard_detection_range, 1)

    def detect_hazard(self, hazards):
        for hazard in hazards:
            # Calculate distance between car and hazard
            dist = ((hazard.x - self.x) ** 2 + (hazard.y - self.y) ** 2) ** 0.5
            
            # Check if hazard is within detection range and in front of the car
            if dist < hazard_detection_range and self.is_hazard_in_lane(hazard):
                if dist < hazard_stop_distance:
                    self.speed = 0  # Stop the car if within stop distance
                    self.stopped = True
                    self.avoiding_hazard = True
                    self.lane_change_state = 1  # Start lane change
                    self.lane_change_direction = -1 if self.lane_change_direction == 1 else 1
                else:
                    self.speed = car_speed - 2  # Slow down when close to hazard
                return True
        self.speed = car_speed  # Reset speed if no hazard is detected
        return False

    def is_hazard_in_lane(self, hazard):
        """Check if a hazard is in the same lane as the car."""
        return lane_y - car_height < hazard.y < lane_y + car_height

# Define hazard (obstacle) object
class Hazard:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40

    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))

# Main loop
def main():
    car = Car(WIDTH // 2 - 100, lane_y)  # Start a little to the left of the center
    
    # Manually placed hazards
    hazards = [
        Hazard((WIDTH // 2) + 200, lane_y),
        Hazard((WIDTH // 2) + 400, lane_y),
        Hazard(random.randint(100, WIDTH - 100), lane_y),
    ]
    
    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(30)  # 30 frames per second
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw the lane
        pygame.draw.rect(screen, GRAY, (0, lane_y - 50, WIDTH, 100))

        # Detect hazards and update car state
        car.detect_hazard(hazards)

        # Move the car
        car.move()

        # Draw hazards and the car
        for hazard in hazards:
            hazard.draw(screen)
        car.draw(screen)

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
