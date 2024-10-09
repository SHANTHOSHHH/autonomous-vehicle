import tkinter as tk
import math
import random
import time
from ml_model import MLModel

class AutonomousCar:
    def __init__(self):
        self.speed = 0
        self.steering_angle = 0
        self.brake_state = False
        self.car_x = 400  # Initial x position  
        self.car_y = 500  # Initial y position
        self.angle = 0  # Orientation in degrees
        self.sensors = []  # For sensor/radar data
        self.manual_input = False
        self.last_manual_input_time = time.time()
        self.input_timeout = 5  # Timeout before switching back to autonomous mode
        self.max_forward_speed = 20
        self.max_reverse_speed = -10
        self.is_reversing = False
        self.acceleration_rate = 0.2# Increased rate for better visibility
        self.deceleration_rate = 0.1  # Rate at which speed decreases

    def accelerate(self, increment):
        """ Update the speed based on acceleration input """
        if not self.brake_state:
            self.speed += increment * self.acceleration_rate
            self.is_reversing = self.speed < 0
            self.speed = max(self.max_reverse_speed, min(self.speed, self.max_forward_speed))  # Cap the speed
            print(f"Accelerating: Speed={self.speed}")

    def decelerate(self):
        """ Gradually decelerate the car when no input is given """
        if self.speed > 0:
            self.speed -= self.deceleration_rate
        elif self.speed < 0:
            self.speed += self.deceleration_rate

    def steer(self, angle_increment):
        """ Update the steering angle based on input """
        if self.speed != 0 and not self.brake_state:
            self.steering_angle += angle_increment
            self.steering_angle = max(-30, min(self.steering_angle, 30))  # Cap the steering angle

    def reset_steering(self):
        """ Reset the steering angle to zero when no key is pressed """
        self.steering_angle = 0

    def apply_brake(self):
        """ Apply the brake and stop the car """
        self.brake_state = True
        self.speed = 0
        self.steering_angle = 0

    def release_brake(self):
        """ Release the brake and allow movement """
        self.brake_state = False

    def update_position(self,left_boundary, right_boundary,upper_boundary,lower_boundary):
        direction =0
        """ Update the car's position based on speed and angle """
        if self.speed != 0:
            # Calculate the direction based on the car's angle
            rad_angle = math.radians(self.angle)
            direction = 1 if self.speed > 0 else -1  # Forward or reverse

            # Scale the movement for better visibility
            movement_scale = 5
            
           # Update the car's x and y position (temporary new position)
            new_car_x = self.car_x + direction * abs(self.speed) * math.cos(rad_angle) * movement_scale
            new_car_y = self.car_y + direction * abs(self.speed) * math.sin(rad_angle) * movement_scale

        # Boundary Check (restrict car within road boundaries)
            if new_car_x < left_boundary:  # Left boundary
                self.car_x = left_boundary
                print("Hit left boundary. Can't move further left.")
            elif new_car_x > right_boundary:  # Right boundary
                self.car_x = right_boundary
                print("Hit right boundary. Can't move further right.")
            elif new_car_y < upper_boundary:  # Upper boundary
                self.car_y = upper_boundary
                print("Hit upper boundary. Can't move further up.")
            elif new_car_y > lower_boundary:  # Lower boundary
                self.car_y = lower_boundary
                print("Hit lower boundary. Can't move further down.")
            else:
            # Update to the new position if within boundaries
                self.car_x = new_car_x
                self.car_y = new_car_y

        # Update the car's angle based on steering and speed
        self.angle += self.steering_angle * 0.1 * direction
        self.angle %= 360  
        self.update_sensors()  # Simulate sensor updates

    def update_sensors(self):
        """ Simulate radar sensors (just basic simulation here) """
        self.sensors = []
        for sensor_angle in [-45, 0, 45]:  # Left, forward, right
            sensor_x = self.car_x + math.cos(math.radians(self.angle + sensor_angle)) * 100
            sensor_y = self.car_y + math.sin(math.radians(self.angle + sensor_angle)) * 100
            self.sensors.append((sensor_x, sensor_y))


class AutonomousCarWithML(AutonomousCar):
    def __init__(self):
        super().__init__()
        self.ml_model = MLModel()
    def get_ml_predictions(self):
        """ Simulate simple ML model predictions """
        sensor_data = self.sensors

        # Simulate basic decision-making for autonomous driving
        if random.random() > 0.2:  # Simulate continuous movement (increased chance of acceleration)
            return {
                'accelerate': True,
                'brake': False,
                'steer_left': random.choice([True, False]),
                'steer_right': random.choice([True, False])
            }
        else:
            return {
                'accelerate': False,
                'brake': True,
                'steer_left': False,
                'steer_right': False
            }

    def update_autonomous_mode(self,left_boundary, right_boundary,upper_boundary,lower_boundary):
        """ Apply ML predictions to control the car """
        predictions = self.get_ml_predictions()
        acceleration = self.ml_model.get_acceleration()
        steering_angle = self.ml_model.get_steering_angle()  # Get steering angle from ML model
        brake_signal = self.ml_model.get_brake_signal()  # Get brake signal from ML model
        if brake_signal:
            self.apply_brake()
            print("Autonomous Mode: Brake applied")
        else:
           self.release_brake()
           self.accelerate(acceleration)  # Use ML acceleration
           print(f"Autonomous Mode: Accelerating, Speed={self.speed}")
        # Steering
         # Apply steering based on ML model
        if steering_angle < 0:
           self.steer(-2)  # Turn left
           print("Autonomous Mode: Steering Left")
        elif steering_angle > 0:
            self.steer(2)  # Turn right
            print("Autonomous Mode: Steering Right")
        else:
            self.reset_steering()
            print("Autonomous Mode: Moving Straight")
        self.update_position(left_boundary, right_boundary,upper_boundary,lower_boundary)  # Update car's position


class CarSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', self.exit_fullscreen)
        self.root.bind("<KeyPress>", self.key_press)
        self.root.bind("<KeyRelease>", self.key_release)

        self.car = AutonomousCarWithML()
        self.autonomous_mode = True  # Start with autonomous mode ON
        self.manual_control = {'forward': False, 'backward': False, 'left': False, 'right': False}

        self.canvas = tk.Canvas(self.root, bg="white", width=1920, height=1080)
        self.canvas.pack(fill="both", expand=True)

        self.draw_road()  # Draw the road
        self.update_movement()  # Start the movement updates

    def draw_road(self):
        road_height = 400
        road_color = "gray"
        lane_marking_color = "white"
        self.left_boundary = 0
        self.right_boundary = 1650
        self.upper_boundary = 300
        self.lower_boundary = self.upper_boundary + road_height
        # Draw the road
        self.canvas.create_rectangle(self.left_boundary,self.upper_boundary ,self.right_boundary,self.lower_boundary,
                                     fill=road_color, tags="road")

        lane_y = self.upper_boundary + (self.lower_boundary - self.upper_boundary) // 2  # Place lane markings in the middle of the road
        for i in range(self.left_boundary, self.right_boundary, 40):
            self.canvas.create_line(i, lane_y, i + 20, lane_y, fill=lane_marking_color, width=4, tags="road")
    def draw_car(self):
        """ Draw the car and sensors on the canvas """
        self.canvas.delete("car")  # Clear previous car drawings

        car_width, car_height = 60, 30
        car_polygon = self.get_rotated_rectangle(self.car.car_x, self.car.car_y, car_width, car_height, self.car.angle)

        # Print position for debugging
        
        # Draw the car
        self.canvas.create_polygon(car_polygon, fill="blue", tags="car")

        # Draw sensors
        for sensor_x, sensor_y in self.car.sensors:
            self.canvas.create_line(self.car.car_x, self.car.car_y, sensor_x, sensor_y, fill="green", tags="car")
            
        self.car.update_position(self.left_boundary, self.right_boundary,self.upper_boundary,self.lower_boundary)

    def get_rotated_rectangle(self, x, y, width, height, angle):
        """ Calculate the corners of a rotated rectangle """
        half_width, half_height = width / 2, height / 2
        corners = [(-half_width, -half_height), (half_width, -half_height),
                   (half_width, half_height), (-half_width, half_height)]

        rotated_corners = []
        for cx, cy in corners:
            rotated_x = x + (cx * math.cos(math.radians(angle)) - cy * math.sin(math.radians(angle)))
            rotated_y = y + (cx * math.sin(math.radians(angle)) + cy * math.cos(math.radians(angle)))
            rotated_corners.append((rotated_x, rotated_y))

        return rotated_corners

    def key_press(self, event):
        """ Handle key press events for manual control """
        self.car.manual_input = True  # Track manual input
        self.car.last_manual_input_time = time.time()  # Reset the timer when a key is pressed
        if event.keysym in ['w', 'a', 's', 'd']:
            self.autonomous_mode = False  # Switch to manual mode
            print("Manual control activated by driver")
        
        if event.keysym == 'm':
         # Switch between manual and autonomous modes
            self.autonomous_mode = not self.autonomous_mode
            if self.autonomous_mode:
                print("Switched to Autonomous mode")
                self.car.speed = 0  # Stop manual inputs from affecting the car
                self.car.steering_angle = 0
            else:
                print("Switched to Manual mode")
                self.car.speed = 0
        if self.autonomous_mode:
            return 
        if event.keysym == 'w':
            self.manual_control['forward'] = True
        if event.keysym == 's':
            self.manual_control['backward'] = True
        if event.keysym == 'a':
            self.manual_control['left'] = True
        if event.keysym == 'd':
            self.manual_control['right'] = True
        if event.keysym == 'm':
            self.autonomous_mode = not self.autonomous_mode  # Switch between modes
            if self.autonomous_mode:
                print("Switched to Autonomous mode")
                self.car.speed = 0
                self.car.steering_angle = 0  # Stop the car when switching to autonomous mode
            else:
               print("Switched to Manual mode")
               self.car.speed = 0
    def key_release(self, event):
        """ Handle key release events for manual control """
        if event.keysym == 'w':
            self.manual_control['forward'] = False
        if event.keysym == 's':
            self.manual_control['backward'] = False
        if event.keysym == 'a':
            self.manual_control['left'] = False
            self.car.reset_steering()  # Stop steering when key is released
        if event.keysym == 'd':
            self.manual_control['right'] = False
            self.car.reset_steering()  # Stop steering when key is released

    def exit_fullscreen(self, event=None):
        """ Exit fullscreen mode """
        self.root.attributes('-fullscreen', False)

    def update_movement(self):
        """ Update the car's movement and redraw the car """
        if self.autonomous_mode:
            self.car.update_autonomous_mode(self.left_boundary,self.right_boundary,self.upper_boundary,self.lower_boundary)
        else:
            # Handle manual control
            if self.manual_control['forward']:
                self.car.accelerate(1)
            if self.manual_control['backward']:
                self.car.accelerate(-1)
            if not self.manual_control['forward'] and not self.manual_control['backward']:
                self.car.decelerate()  # Gradually decelerate when no input is given
            if self.manual_control['left']:
                self.car.steer(-2)
            if self.manual_control['right']:
                self.car.steer(2)

         # Pass boundaries to draw_car
        
        self.draw_car()  # Redraw the car on the canvas
        self.root.after(50, self.update_movement)  # Update every 50 milliseconds
        if not self.autonomous_mode and (time.time() - self.car.last_manual_input_time) > self.car.input_timeout:
            print("Switching back to Autonomous mode due to inactivity")
            self.autonomous_mode = True
if __name__ == "__main__":
    root = tk.Tk()
    app = CarSimulatorApp(root)
    root.mainloop()
