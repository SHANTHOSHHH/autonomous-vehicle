# actuator_control.py (mock version for testing on Windows)
# This will simulate brake control

def control_accelerator(speed):
    print(f"Mock: Accelerator set to speed: {speed}")

def control_steering(angle):
    print(f"Mock: Steering angle set to {angle} degrees")

def control_brake(state):
    if state == 1:
        print("Mock: Brake applied")
    else:
        print("Mock: Brake released")
