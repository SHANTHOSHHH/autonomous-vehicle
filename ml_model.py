# ml_model.py
import random
class MLModel:
    def get_acceleration(self):
        # Simulate acceleration decision
        return random.choice([1, 0, -1])  # Return 1 for accelerate, 0 for maintain speed, -1 for decelerate

    def get_steering_angle(self):
        # Simulate steering decision
        return random.choice([-1, 0, 1])  # -1 for left, 0 for straight, 1 for right

    def get_brake_signal(self):
        # Simulate brake decision (e.g., object detection in path)
        return random.random() < 0.1  # 10% chance of braking
