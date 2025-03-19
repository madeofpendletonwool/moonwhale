#!/usr/bin/env python3
"""
Moonwhale Setup App
A controller-friendly interface for configuring the Moonwhale container
"""

import pygame
import sys
import os
import time
from pygame.locals import *

# Initialize pygame
pygame.init()

# Try initializing joysticks
pygame.joystick.init()
joysticks = []

print(f"Joystick count: {pygame.joystick.get_count()}")
for i in range(pygame.joystick.get_count()):
    try:
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        joysticks.append(joystick)
        print(f"Initialized joystick {i}: {joystick.get_name()}")
    except Exception as e:
        print(f"Failed to initialize joystick {i}: {e}")

# Set up the display
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
try:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
except:
    # Fallback to windowed mode
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption("Moonwhale Setup")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BLUE = (0, 30, 60)
BLUE = (0, 120, 215)
LIGHT_BLUE = (0, 174, 219)
HIGHLIGHT = (0, 220, 255)

# Fonts
try:
    font_large = pygame.font.SysFont('Arial', 60)
    font_medium = pygame.font.SysFont('Arial', 36)
    font_small = pygame.font.SysFont('Arial', 24)
except:
    # Fallback to default font
    font_large = pygame.font.Font(None, 60)
    font_medium = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 24)

# Load logo - try both filenames
script_dir = os.path.dirname(os.path.abspath(__file__))
logo = None

# Try loading PNG first
try:
    logo_path = os.path.join(script_dir, "images/moonwhale.jpg")
    logo = pygame.image.load(logo_path)
    logo = pygame.transform.scale(logo, (200, 200))
    print(f"Logo loaded from {logo_path}")
except:
    # Try JPG next
    try:
        logo_path = os.path.join(script_dir, "images/moonwhale.jpg")
        logo = pygame.image.load(logo_path)
        logo = pygame.transform.scale(logo, (200, 200))
        print(f"Logo loaded from {logo_path}")
    except Exception as e:
        print(f"Could not load logo: {e}")

# Menu options
menu_items = [
    "Install Gaming Emulators",
    "Install Web Browser",
    "Install Media Player",
    "System Settings",
    "Exit"
]

selected_index = 0
last_key_time = time.time()
key_cooldown = 0.3  # seconds between key presses

# Main app loop
def main():
    global selected_index, last_key_time

    clock = pygame.time.Clock()
    running = True

    print("DEBUG INFO:")
    print(f"PyGame version: {pygame.version.ver}")
    print(f"Joystick count: {pygame.joystick.get_count()}")
    print(f"Display driver: {pygame.display.get_driver()}")

    while running:
        current_time = time.time()
        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            # We want to process keyboard events even with cooldown
            # otherwise the app feels unresponsive
            elif event.type == KEYDOWN:
                print(f"Key pressed: {event.key}")
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_UP or event.key == K_w:
                    if current_time - last_key_time > key_cooldown:
                        selected_index = (selected_index - 1) % len(menu_items)
                        last_key_time = current_time
                elif event.key == K_DOWN or event.key == K_s:
                    if current_time - last_key_time > key_cooldown:
                        selected_index = (selected_index + 1) % len(menu_items)
                        last_key_time = current_time
                elif event.key == K_RETURN or event.key == K_SPACE:
                    handle_selection(selected_index)
                    if selected_index == len(menu_items) - 1:  # Exit option
                        running = False

            # Controller support
            elif event.type == JOYAXISMOTION:
                # Only process joystick events after cooldown
                if current_time - last_key_time < key_cooldown:
                    continue

                # Vertical movement on left stick (Y-axis is usually 1)
                if event.axis in [1, 3]:  # Try both common Y-axis values
                    if event.value < -0.5:  # Up
                        selected_index = (selected_index - 1) % len(menu_items)
                        last_key_time = current_time
                    elif event.value > 0.5:  # Down
                        selected_index = (selected_index + 1) % len(menu_items)
                        last_key_time = current_time

            elif event.type == JOYBUTTONDOWN:
                button = event.button
                # Common A button is 0, X is 2, Start might be 7 or 9
                if button in [0, 2, 7, 9]:  # Try common "select" buttons
                    handle_selection(selected_index)
                    if selected_index == len(menu_items) - 1:  # Exit option
                        running = False
                # Common B button is 1, or Back button might be 6 or 8
                elif button in [1, 6, 8]:  # Try common "back" buttons
                    running = False

            # Hat (D-pad) support
            elif event.type == JOYHATMOTION:
                if current_time - last_key_time < key_cooldown:
                    continue

                hat_value = event.value
                if hat_value[1] == 1:  # Up on d-pad
                    selected_index = (selected_index - 1) % len(menu_items)
                    last_key_time = current_time
                elif hat_value[1] == -1:  # Down on d-pad
                    selected_index = (selected_index + 1) % len(menu_items)
                    last_key_time = current_time

        # Drawing
        draw_screen()

        # Cap frame rate
        clock.tick(30)

    pygame.quit()
    sys.exit()

def draw_screen():
    # Background
    screen.fill(DARK_BLUE)

    # Draw header with logo
    header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 120)
    pygame.draw.rect(screen, BLUE, header_rect)

    # Draw logo
    if logo:
        screen.blit(logo, (20, 10))

    # Draw title
    title = font_large.render("Moonwhale Setup", True, WHITE)
    screen.blit(title, (240, 30))

    # Draw menu items
    menu_start_y = 160
    for i, item in enumerate(menu_items):
        color = HIGHLIGHT if i == selected_index else WHITE
        bg_rect = pygame.Rect(100, menu_start_y + i * 80, SCREEN_WIDTH - 200, 60)
        if i == selected_index:
            pygame.draw.rect(screen, LIGHT_BLUE, bg_rect)
            item_text = font_medium.render(item, True, BLACK)
        else:
            pygame.draw.rect(screen, BLUE, bg_rect)
            item_text = font_medium.render(item, True, WHITE)

        # Center text in button
        text_x = bg_rect.centerx - item_text.get_width() // 2
        text_y = bg_rect.centery - item_text.get_height() // 2
        screen.blit(item_text, (text_x, text_y))

    # Draw footer with controls
    footer_rect = pygame.Rect(0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, 60)
    pygame.draw.rect(screen, BLUE, footer_rect)

    # Draw controls guide
    if pygame.joystick.get_count() > 0:
        controls = font_small.render("Controls: D-Pad/Stick Navigate | A/X Select | B/Back Exit", True, WHITE)
    else:
        controls = font_small.render("Controls: ↑↓ Navigate | Enter/Space Select | Esc Back", True, WHITE)

    screen.blit(controls, (SCREEN_WIDTH // 2 - controls.get_width() // 2, SCREEN_HEIGHT - 40))

    # Update the display
    pygame.display.flip()

def handle_selection(index):
    print(f"Selected: {menu_items[index]}")
    if index == 0:  # Install Gaming Emulators
        show_message("Coming Soon", "Gaming emulator installation will be available in a future update.")
    elif index == 1:  # Install Web Browser
        show_message("Coming Soon", "Web browser installation will be available in a future update.")
    elif index == 2:  # Install Media Player
        show_message("Coming Soon", "Media player installation will be available in a future update.")
    elif index == 3:  # System Settings
        show_message("Coming Soon", "System settings will be available in a future update.")
    # Exit option handled in main loop

def show_message(title, message):
    # Draw a modal dialog
    dialog_width = 600
    dialog_height = 300
    dialog_x = (SCREEN_WIDTH - dialog_width) // 2
    dialog_y = (SCREEN_HEIGHT - dialog_height) // 2

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # Semi-transparent black
    screen.blit(overlay, (0, 0))

    dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
    pygame.draw.rect(screen, BLUE, dialog_rect)
    pygame.draw.rect(screen, WHITE, dialog_rect, 2)  # Border

    # Title
    title_text = font_medium.render(title, True, WHITE)
    screen.blit(title_text, (dialog_x + (dialog_width - title_text.get_width()) // 2, dialog_y + 20))

    # Message (wrapped)
    lines = wrap_text(message, font_small, dialog_width - 40)
    for i, line in enumerate(lines):
        text = font_small.render(line, True, WHITE)
        screen.blit(text, (dialog_x + 20, dialog_y + 80 + i * 30))

    # OK button
    ok_rect = pygame.Rect(dialog_x + (dialog_width - 100) // 2, dialog_y + dialog_height - 60, 100, 40)
    pygame.draw.rect(screen, LIGHT_BLUE, ok_rect)
    ok_text = font_small.render("OK", True, BLACK)
    screen.blit(ok_text, (ok_rect.centerx - ok_text.get_width() // 2, ok_rect.centery - ok_text.get_height() // 2))

    pygame.display.flip()

    # Wait for any input to dismiss the dialog
    waiting = True
    wait_time = time.time()
    while waiting:
        for event in pygame.event.get():
            # Add a small delay before accepting input to prevent accidental dismissal
            if time.time() - wait_time < 0.5:
                continue

            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                waiting = False
            elif event.type == JOYBUTTONDOWN:
                waiting = False
            elif event.type == MOUSEBUTTONDOWN:
                waiting = False

def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return lines

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
