import pygame
import yaml
import os
import sys
import subprocess
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Pygame joystick to command execution")
parser.add_argument("-c", "--config", default="config.yaml", help="Path to the configuration file")
parser.add_argument("-j", "--joystick", type=int, default=0, help="Joystick identifier")
parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")

args = parser.parse_args()

# Load YAML configuration file
with open(args.config, 'r') as file:
    config = yaml.safe_load(file)

image_path = config.get("image")
image = None
if image_path and os.path.isfile(image_path):
    image = pygame.image.load(image_path)
    image = pygame.transform.scale(image, (640, 480))  # Scale the image to fit the window

# Initialize Pygame
pygame.init()
pygame.joystick.init()

# Check for the number of connected joysticks
joystick_count = pygame.joystick.get_count()

# Create an instance of the specified joystick
if joystick_count > args.joystick:
    joystick = pygame.joystick.Joystick(args.joystick)
    joystick.init()
else:
    print("No joystick detected")
    exit()

# Create a window
screen = pygame.display.set_mode((640, 480))

# Main event loop
running = True
while running:
    if image:
        screen.blit(image, (0, 0))
        pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle button press events
        if event.type == pygame.JOYBUTTONDOWN:
            if args.debug:
                print(f"Button {event.button} pressed")
            for button, command in config.get("button_mappings", {}).items():
                if event.button == int(button):
                    subprocess.run(command, shell=True)

        # Handle axis motion events (assuming a dead zone of 0.2)
        if event.type == pygame.JOYAXISMOTION:
            for axis, command in config.get("axis_mappings", {}).items():
                value = joystick.get_axis(int(axis))
                if abs(value) > 0.2:
                    if args.debug:
                        print(f"Axis {axis} moved: {value}")
                    formatted_command = command.format(value=value)
                    subprocess.run(formatted_command, shell=True)

        # Handle trigger events (assuming a dead zone of 0.2)
        if event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP:
            for trigger, command in config.get("trigger_mappings", {}).items():
                value = joystick.get_axis(int(trigger))
                if abs(value) > 0.2:
                    if args.debug:
                        print(f"Trigger {trigger} moved: {value}")
                    formatted_command = command.format(value=value)
                    subprocess.run(formatted_command, shell=True)

# Cleanup
joystick.quit()
pygame.joystick.quit()
pygame.quit()
