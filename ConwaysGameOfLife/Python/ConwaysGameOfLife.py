import pygame
import numpy as np
import time
import tkinter as tk
from tkinter import simpledialog
import collections

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 900, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Conway's Game of Life")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
GRID_COLOR = (50, 50, 50)  # Dark gray for grid lines
BLUE = (100, 149, 237)  # Color for freeze button

# Define grid properties
cell_size = 20  # Default cell size
grid_width = 250  # Larger grid
grid_height = 250
grid = np.zeros((grid_height, grid_width))

# Camera properties
camera_x = 0
camera_y = 0
zoom = 1.0
MIN_ZOOM = 0.2
MAX_ZOOM = 3.0
ZOOM_SPEED = 0.1
MOVE_SPEED = 5  # Reduced from 20 to 5 for slower movement

# Statistics tracking
stats = {
    'born': 0,
    'died': 0,
    'lasting': 0,
    'total': 0
}
history = collections.deque(maxlen=100)  # Store last 100 population counts

def screen_to_grid(x, y):
    """Convert screen coordinates to grid coordinates"""
    grid_x = int((x - camera_x) / (cell_size * zoom))
    grid_y = int((y - camera_y) / (cell_size * zoom))
    return grid_x, grid_y

def grid_to_screen(x, y):
    """Convert grid coordinates to screen coordinates"""
    screen_x = x * cell_size * zoom + camera_x
    screen_y = y * cell_size * zoom + camera_y
    return screen_x, screen_y

def draw_button(screen, text, position, size, color):
    """Draw a button with text."""
    pygame.draw.rect(screen, color, (*position, *size))
    font = pygame.font.Font(None, 36)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=(position[0] + size[0]//2,
                                            position[1] + size[1]//2))
    screen.blit(text_surface, text_rect)
    return pygame.Rect(*position, *size)

def count_neighbors(grid, x, y):
    """Count the number of live neighbors for a cell."""
    total = 0
    # Check each neighboring cell
    for i in range(-1, 2):
        for j in range(-1, 2):
            row = x + i
            col = y + j
            # Only count if within bounds
            if 0 <= row < grid_height and 0 <= col < grid_width:
                total += grid[row, col]
    total -= grid[x, y]  # Subtract the cell itself
    return total

def update_grid():
    """Update the grid based on Conway's Game of Life rules."""
    global grid, stats
    new_grid = grid.copy()
    
    # Reset stats for this generation
    stats['born'] = 0
    stats['died'] = 0
    stats['lasting'] = 0
    stats['total'] = 0
    
    for i in range(grid_height):
        for j in range(grid_width):
            # Kill cells at the edges
            if i == 0 or i == grid_height-1 or j == 0 or j == grid_width-1:
                new_grid[i, j] = 0
                continue
            
            neighbors = count_neighbors(grid, i, j)
            
            if grid[i, j] == 1:  # Live cell
                if neighbors < 2 or neighbors > 3:
                    new_grid[i, j] = 0  # Cell dies
                    stats['died'] += 1
                else:
                    stats['lasting'] += 1
            else:  # Dead cell
                if neighbors == 3:
                    new_grid[i, j] = 1  # Cell becomes alive
                    stats['born'] += 1
    
    grid = new_grid
    stats['total'] = np.sum(grid)
    history.append(stats['total'])

def draw_grid_and_cells():
    """Draw the grid lines and cells with camera transformation"""
    # Calculate visible grid range
    start_x = max(0, int(-camera_x / (cell_size * zoom)))
    start_y = max(0, int(-camera_y / (cell_size * zoom)))
    end_x = min(grid_width, int((width - camera_x) / (cell_size * zoom)) + 1)
    end_y = min(grid_height, int((height - camera_y) / (cell_size * zoom)) + 1)

    # Draw grid lines only within the grid bounds
    for x in range(start_x, end_x + 1):
        screen_x = grid_to_screen(x, 0)[0]
        start_y_pos = max(0, grid_to_screen(0, 0)[1])
        end_y_pos = min(height, grid_to_screen(0, grid_height)[1])
        pygame.draw.line(screen, GRID_COLOR,
                        (screen_x, start_y_pos),
                        (screen_x, end_y_pos))

    for y in range(start_y, end_y + 1):
        screen_y = grid_to_screen(0, y)[1]
        start_x_pos = max(0, grid_to_screen(0, 0)[0])
        end_x_pos = min(width, grid_to_screen(grid_width, 0)[0])
        pygame.draw.line(screen, GRID_COLOR,
                        (start_x_pos, screen_y),
                        (end_x_pos, screen_y))

    # Draw cells
    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            if grid[y, x] == 1:
                screen_x, screen_y = grid_to_screen(x, y)
                cell_width = max(1, int(cell_size * zoom - 1))
                pygame.draw.rect(screen, WHITE,
                               (screen_x + 1, screen_y + 1,
                                cell_width, cell_width))

def get_camera_position():
    """Open a dialog to get new camera coordinates"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    try:
        # Get X coordinate
        x = simpledialog.askinteger("Set Camera Position", 
                                   "Enter X coordinate:",
                                   initialvalue=-camera_x)
        if x is None:  # User cancelled
            return None
            
        # Get Y coordinate
        y = simpledialog.askinteger("Set Camera Position", 
                                   "Enter Y coordinate:",
                                   initialvalue=-camera_y)
        if y is None:  # User cancelled
            return None
            
        return -x, -y  # Return negative values since camera moves opposite to position
    finally:
        root.destroy()

def draw_stats():
    """Draw statistics and population graph"""
    # Draw stats text
    font = pygame.font.Font(None, 24)
    stats_text = [
        f"Born: {stats['born']}",
        f"Died: {stats['died']}",
        f"Lasting: {stats['lasting']}",
        f"Total: {stats['total']}"
    ]
    
    for i, text in enumerate(stats_text):
        text_surface = font.render(text, True, WHITE)
        screen.blit(text_surface, (10, 40 + i * 25))
    
    # Draw population graph
    if history:
        # Graph dimensions
        graph_width = 200
        graph_height = 100
        graph_x = 10
        graph_y = 150
        
        # Draw graph background
        pygame.draw.rect(screen, GRID_COLOR, (graph_x, graph_y, graph_width, graph_height))
        
        # Draw population line
        max_pop = max(max(history), 1)  # Avoid division by zero
        points = []
        for i, pop in enumerate(history):
            x = graph_x + (i * graph_width) // len(history)
            y = graph_y + graph_height - int((pop * graph_height) / max_pop)
            points.append((x, y))
            
        if len(points) > 1:
            pygame.draw.lines(screen, WHITE, False, points, 2)

# Main game loop
running = True
simulation_started = False
paused = False
frozen = False
fast_speed = False  # New variable for speed control

# Create buttons
start_button = pygame.Rect(width - 100, 10, 90, 40)
clear_button = pygame.Rect(width - 200, 10, 90, 40)
freeze_button = pygame.Rect(width - 300, 10, 90, 40)
random_button = pygame.Rect(width - 400, 10, 90, 40)  # New random button
speed_button = pygame.Rect(width - 500, 10, 90, 40)   # New speed button

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Handle button clicks
            if start_button.collidepoint(mouse_pos):
                simulation_started = True
            elif clear_button.collidepoint(mouse_pos):
                grid = np.zeros((grid_height, grid_width))
                simulation_started = False
                frozen = False
            elif freeze_button.collidepoint(mouse_pos):
                frozen = not frozen
            elif random_button.collidepoint(mouse_pos):
                # Generate random world
                grid = np.random.choice([0, 1], size=(grid_height, grid_width), p=[0.85, 0.15])
                # Set edges to 0
                grid[0, :] = grid[-1, :] = grid[:, 0] = grid[:, -1] = 0
            elif speed_button.collidepoint(mouse_pos):
                fast_speed = not fast_speed
            # Handle cell toggling with left mouse button
            elif (not simulation_started or frozen) and not any(button.collidepoint(mouse_pos) 
                 for button in [start_button, clear_button, freeze_button, random_button, speed_button]):
                grid_x, grid_y = screen_to_grid(*mouse_pos)
                if 0 < grid_x < grid_width-1 and 0 < grid_y < grid_height-1:
                    if event.button == 1:  # Left click toggles cell state
                        grid[grid_y, grid_x] = 1 - grid[grid_y, grid_x]  # Toggle between 0 and 1
                    elif event.button == 2:  # Middle click still erases
                        grid[grid_y, grid_x] = 0
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button in [1, 2]:  # Left or middle mouse button
                last_cell = None
        
        elif event.type == pygame.MOUSEMOTION:
            # Handle continuous drawing while dragging
            if (not simulation_started or frozen) and (pygame.mouse.get_pressed()[0] or 
                pygame.mouse.get_pressed()[1]):
                grid_x, grid_y = screen_to_grid(*event.pos)
                if 0 < grid_x < grid_width-1 and 0 < grid_y < grid_height-1:
                    if pygame.mouse.get_pressed()[0]:  # Left button sets to alive
                        grid[grid_y, grid_x] = 1
                    elif pygame.mouse.get_pressed()[1]:  # Middle button sets to dead
                        grid[grid_y, grid_x] = 0
        
        # Handle zooming with Ctrl+Scroll
        elif event.type == pygame.MOUSEWHEEL and pygame.key.get_pressed()[pygame.K_LCTRL]:
            old_zoom = zoom
            zoom = max(MIN_ZOOM, min(MAX_ZOOM, zoom + event.y * ZOOM_SPEED))
            # Adjust camera to zoom towards mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()
            camera_x += (mouse_x - camera_x) * (1 - zoom/old_zoom)
            camera_y += (mouse_y - camera_y) * (1 - zoom/old_zoom)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                new_pos = get_camera_position()
                if new_pos:
                    camera_x, camera_y = new_pos
            elif event.key == pygame.K_SPACE:  # Add space bar handler
                if not simulation_started or frozen:  # Only allow ticking when not running
                    update_grid()

    # Handle keyboard movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]: 
        camera_x += MOVE_SPEED
    if keys[pygame.K_d]: 
        camera_x -= MOVE_SPEED
    if keys[pygame.K_w]: 
        camera_y += MOVE_SPEED
    if keys[pygame.K_s]: 
        camera_y -= MOVE_SPEED
    if keys[pygame.K_LEFT]:  # Add left/right key zooming
        old_zoom = zoom
        zoom = max(MIN_ZOOM, zoom - ZOOM_SPEED)
        # Zoom towards center of screen
        camera_x += (width/2 - camera_x) * (1 - zoom/old_zoom)
        camera_y += (height/2 - camera_y) * (1 - zoom/old_zoom)
    if keys[pygame.K_RIGHT]:
        old_zoom = zoom
        zoom = min(MAX_ZOOM, zoom + ZOOM_SPEED)
        # Zoom towards center of screen
        camera_x += (width/2 - camera_x) * (1 - zoom/old_zoom)
        camera_y += (height/2 - camera_y) * (1 - zoom/old_zoom)

    # Update simulation if appropriate
    if simulation_started and not paused and not frozen:
        update_grid()
        if fast_speed:
            pass
        else:
            time.sleep(0.1)   # Normal speed

    # Draw everything
    screen.fill(BLACK)
    draw_grid_and_cells()

    # Draw buttons (these stay fixed on screen)
    button_color = GRAY if simulation_started else WHITE
    draw_button(screen, "Start" if not simulation_started else "Running",
                (width - 100, 10), (90, 40), button_color)
    draw_button(screen, "Clear", (width - 200, 10), (90, 40), WHITE)
    draw_button(screen, "Freeze", (width - 300, 10), (90, 40),
                BLUE if frozen else WHITE)
    draw_button(screen, "Random", (width - 400, 10), (90, 40), WHITE)
    draw_button(screen, "Faster", (width - 500, 10), (90, 40),
                BLUE if fast_speed else WHITE)

    # Draw camera info
    font = pygame.font.Font(None, 24)
    info_text = f"Zoom: {zoom:.1f}x | Pos: ({-camera_x:.0f}, {-camera_y:.0f})Space for single step"
    text_surface = font.render(info_text, True, WHITE)
    screen.blit(text_surface, (10, 10))

    # Draw stats and graph
    draw_stats()

    pygame.display.flip()

pygame.quit()
