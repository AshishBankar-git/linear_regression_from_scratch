import pygame
import random
import os

pygame.init()
WIDTH = 400
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Game - Image Version")


try:
    car_img = pygame.image.load('car4.png').convert_alpha()
    c_r = pygame.image.load('car1.png').convert_alpha()
    player_car_img = pygame.transform.scale(car_img, (40, 70))
    obstacle_car_img = pygame.transform.scale(c_r, (40, 70))
except Exception as e:
    print(f"Could not find or load car.png: {e}")
    print("Using colored blocks instead.")
    player_car_img = None
    obstacle_car_img = None

# Colors
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
GREEN = (34, 139, 34)
RED = (200, 0, 0)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 30)
big_font = pygame.font.SysFont("Arial", 50)

def show_game_over(final_score):
    """ Displays the final score and waits for user input """
    screen.fill(BLACK)
    msg = big_font.render("GAME OVER", True, RED)
    score_msg = font.render(f"Final Score: {final_score}", True, WHITE)
    retry_msg = font.render("Press any key to Quit", True, WHITE)
    
    screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 3))
    screen.blit(score_msg, (WIDTH // 2 - score_msg.get_width() // 2, HEIGHT // 2))
    screen.blit(retry_msg, (WIDTH // 2 - retry_msg.get_width() // 2, HEIGHT // 2 + 50))  
    pygame.display.update()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                waiting = False

# Game Variables
car_width = 40
car_height = 70
car_x = WIDTH // 2 - car_width // 2
car_y = HEIGHT - 100
car_speed = 6

obstacles = []
trees = []
lines = [[WIDTH//2 - 5, i * 80] for i in range(8)]
score = 0
base_game_speed = 5 
running = True

# Distance control variable
MIN_DISTANCE_BETWEEN_OBSTACLES = 180 

while running:
    game_speed = base_game_speed + (score // 500)
    current_car_speed = car_speed + (score // 2000)

    screen.fill(GREEN)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and car_x > 85: 
        car_x -= current_car_speed
    if keys[pygame.K_RIGHT] and car_x < WIDTH - 125: 
        car_x += current_car_speed

   
    pygame.draw.rect(screen, GRAY, (80, 0, 240, HEIGHT))
    
    
    for line in lines:
        pygame.draw.rect(screen, WHITE, (line[0], line[1], 8, 40))
        line[1] += game_speed
        if line[1] > HEIGHT:
            line[1] = -40

   
    if random.randint(1, 40) == 1:
        trees.append([random.choice([10, 40, 330, 360]), -60])
    
    for tree in trees[:]:
        pygame.draw.rect(screen, BROWN, (tree[0]+5, tree[1]+20, 10, 20))
        pygame.draw.circle(screen, (0, 100, 0), (tree[0]+10, tree[1]+20), 20)
        tree[1] += game_speed
        if tree[1] > HEIGHT: 
            trees.remove(tree)

    
    can_spawn = True
    if len(obstacles) > 0:
     
        if obstacles[-1][1] < MIN_DISTANCE_BETWEEN_OBSTACLES:
            can_spawn = False

    if can_spawn and random.randint(1, 50) == 1:
        obstacles.append([random.randint(100, 260), -80])
   

    for obs in obstacles[:]:
        obs[1] += game_speed
        
        # Draw Obstacle
        if obstacle_car_img:
            screen.blit(obstacle_car_img, (obs[0], obs[1]))
        else:
            pygame.draw.rect(screen, RED, (obs[0], obs[1], 40, 70))
        
        # Collision Detection
        car_rect = pygame.Rect(car_x, car_y, car_width, car_height)
        obs_rect = pygame.Rect(obs[0], obs[1], 40, 70)     
        if car_rect.colliderect(obs_rect):
            show_game_over(score) 
            running = False         
        
        # Remove obstacle if off-screen
        if obs[1] > HEIGHT: 
            obstacles.remove(obs)

    # Draw Player
    if player_car_img:
        screen.blit(player_car_img, (car_x, car_y))
    else:
        pygame.draw.rect(screen, BLACK, (car_x, car_y, car_width, car_height))

    # UI
    score += 1
    score_text = font.render(f"Score: {score}", True, WHITE)
    speed_text = font.render(f"Speed: {int(game_speed)}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(speed_text, (10, 40))
    
    pygame.display.update()
    clock.tick(60)

pygame.quit()