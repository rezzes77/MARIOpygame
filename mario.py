import pygame
import random

pygame.init()

W = 800
H = 600
screen = pygame.display.set_mode((W, H))

FPS = 60
clock = pygame.time.Clock()

font_path = 'PressStart2P-Regular.ttf'
font_large = pygame.font.Font(font_path, 48)
font_small = pygame.font.Font(font_path, 24)

ground_image = pygame.image.load('6266232149901312.png')
ground_image = pygame.transform.scale(ground_image, (804, 60))
GROUND_H = ground_image.get_height()

enemy_image = pygame.image.load('pngwing.com (1).png')
enemy_image = pygame.transform.scale(enemy_image, (80, 80))

enemy_dead_image = pygame.image.load('poop.png')
enemy_dead_image = pygame.transform.scale(enemy_dead_image, (80, 80))

player_image = pygame.image.load('pngwing.com (2).png')
player_image = pygame.transform.scale(player_image, (60, 80))

background_image = pygame.image.load('a-0180.jpg')
background_image = pygame.transform.scale(background_image, (W, H))

pygame.mixer.music.load('untitled_3.mp3')
jump_sound = pygame.mixer.Sound('maro-jump-sound-effect_1.mp3')
kill_sound = pygame.mixer.Sound('super-mario-64-yahoo-sound.mp3')
death_sound = pygame.mixer.Sound('super-mario-death-sound-sound-effect.mp3')

pygame.mixer.music.set_volume(0.5)

score = 0
start_time = pygame.time.get_ticks()

class Entity:
    def __init__(self, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.x_speed = 0
        self.y_speed = 0
        self.speed = 5
        self.is_out = False
        self.is_dead = False
        self.jump_speed = -12
        self.gravity = 0.5
        self.is_grounded = False
    
    def handle_input(self):
        pass
    
    def kill(self, dead_image):
        self.image = dead_image  
        self.is_dead = True
        self.x_speed = -self.x_speed
        self.y_speed = self.jump_speed
        kill_sound.play()
        
    def update(self):
        self.rect.x += self.x_speed
        self.y_speed += self.gravity
        self.rect.y += self.y_speed
        if self.rect.bottom >= H - GROUND_H:
            self.is_grounded = True
            self.y_speed = 0
            self.rect.bottom = H - GROUND_H
        else:
            self.is_grounded = False
        if self.is_dead:
            if self.rect.top > H - GROUND_H:
                self.is_out = True
        else:
            self.handle_input()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Player(Entity):
    def __init__(self):
        super().__init__(player_image)
        self.rect.midbottom = (W // 2, H - GROUND_H)

    def handle_input(self):
        self.x_speed = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.x_speed = -self.speed
        elif keys[pygame.K_d]:
            self.x_speed = self.speed
        if keys[pygame.K_SPACE] and self.is_grounded:
            self.jump()

    def jump(self):
        if self.is_grounded:
            self.y_speed = self.jump_speed
            self.is_grounded = False  
            jump_sound.play()

    def respawn(self):
        self.is_out = False
        self.is_dead = False
        self.rect.midbottom = (W // 2, H - GROUND_H)

class Goomba(Entity):
    def __init__(self):
        super().__init__(enemy_image)
        self.is_falling = True  

    def spawn(self):
        if random.choice([True, False]):
            self.rect.midtop = (0, -self.rect.height)
            self.spawn_side = 'left'
        else:
            self.rect.midtop = (W, -self.rect.height)
            self.spawn_side = 'right'

    def update(self):
        if self.is_falling:
            self.y_speed += self.gravity
            self.rect.y += self.y_speed
            if self.rect.bottom >= H - GROUND_H:
                self.rect.bottom = H - GROUND_H
                self.y_speed = 0
                self.is_falling = False
                if self.spawn_side == 'left':
                    self.x_speed = self.speed
                else:
                    self.x_speed = -self.speed
        else:
            self.rect.x += self.x_speed
            if self.rect.left > W or self.rect.right < 0:
                self.is_out = True

player = Player()
goombas = []

INIT_DELAY = 2000
spawn_delay = INIT_DELAY
DECREASE_BASE = 1.01
last_spawn_time = pygame.time.get_ticks()

def show_game_over_screen():
    screen.fill((0, 0, 0))
    game_over_text = font_large.render('GAME OVER', True, (255, 0, 0))
    game_over_rect = game_over_text.get_rect(center=(W // 2, H // 2))
    screen.blit(game_over_text, game_over_rect)
    retry_text = font_small.render('PLAY AGAIN', True, (255, 255, 255))
    retry_text_rect = retry_text.get_rect(midtop=(W // 2, H // 2 + 50))
    screen.blit(retry_text, retry_text_rect)
    pygame.display.flip()
    pygame.time.wait(2000)

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False
                game(difficulty)

def check_out_of_bounds():
    return player.rect.left < 0 or player.rect.right > W

def show_intro_screen():
    pygame.mixer.music.play(-1)
    
    start_button = font_small.render('START', True, (255, 255, 255))
    help_button = font_small.render('HELP', True, (255, 255, 255))
    exit_button = font_small.render('EXIT', True, (255, 255, 255))
    
    start_rect = start_button.get_rect(center=(W // 2, H // 2 - 50))
    help_rect = help_button.get_rect(center=(W // 2, H // 2))
    exit_rect = exit_button.get_rect(center=(W // 2, H // 2 + 50))
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if start_rect.collidepoint(mouse_pos):
                    show_difficulty_screen()
                    waiting = False
                elif help_rect.collidepoint(mouse_pos):
                    show_help_screen()
                elif exit_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    exit()

        screen.fill((0, 0, 0))
        screen.blit(start_button, start_rect)
        screen.blit(help_button, help_rect)
        screen.blit(exit_button, exit_rect)
        pygame.display.flip()

def show_help_screen():
    help_text = font_small.render('Use A/D to move, SPACE to jump. Avoid enemies!', True, (255, 255, 255))
    back_text = font_small.render('BACK', True, (255, 255, 255))
    
    back_rect = back_text.get_rect(center=(W // 2, H // 2 + 50))
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if back_rect.collidepoint(mouse_pos):
                    waiting = False

        screen.fill((0, 0, 0))
        screen.blit(help_text, (W // 2 - help_text.get_width() // 2, H // 2 - 50))
        screen.blit(back_text, back_rect)
        pygame.display.flip()

difficulty = "medium"

def set_difficulty(level):
    global player, spawn_delay
    if level == "easy":
        player.speed = 5
        spawn_delay = 2000
    elif level == "medium":
        player.speed = 7
        spawn_delay = 1500
    elif level == "hard":
        player.speed = 9
        spawn_delay = 1000

def show_difficulty_screen():
    easy_button = font_small.render('EASY', True, (255, 255, 255))
    medium_button = font_small.render('MEDIUM', True, (255, 255, 255))
    hard_button = font_small.render('HARD', True, (255, 255, 255))

    easy_rect = easy_button.get_rect(center=(W // 2, H // 2 - 50))
    medium_rect = medium_button.get_rect(center=(W // 2, H // 2))
    hard_rect = hard_button.get_rect(center=(W // 2, H // 2 + 50))

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if easy_rect.collidepoint(mouse_pos):
                    global difficulty
                    difficulty = "easy"
                    waiting = False
                elif medium_rect.collidepoint(mouse_pos):
                    difficulty = "medium"
                    waiting = False
                elif hard_rect.collidepoint(mouse_pos):
                    difficulty = "hard"
                    waiting = False

        screen.fill((0, 0, 0))
        screen.blit(easy_button, easy_rect)
        screen.blit(medium_button, medium_rect)
        screen.blit(hard_button, hard_rect)
        pygame.display.flip()

def game(difficulty):
    global last_spawn_time, score, goombas, start_time
    goombas.clear()
    player.respawn()
    score = 0
    start_time = pygame.time.get_ticks()
    set_difficulty(difficulty)
    pygame.mixer.music.play(-1)

    while True:
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - start_time) // 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        screen.blit(background_image, (0, 0))
        screen.blit(ground_image, (0, H - GROUND_H))

        player.update()
        player.draw(screen)

        if pygame.time.get_ticks() - last_spawn_time > spawn_delay:
            goomba = Goomba()
            goomba.spawn()
            goombas.append(goomba)
            last_spawn_time = pygame.time.get_ticks()

        for goomba in goombas:
            if not goomba.is_dead:
                if player.rect.colliderect(goomba.rect):
                    if player.rect.bottom - 10 < goomba.rect.top:
                        goomba.kill(enemy_dead_image)
                        player.jump()
                        score += 1
                    else:
                        pygame.mixer.music.stop()
                        death_sound.play()
                        show_game_over_screen()
                        return
            goomba.update()
            goomba.draw(screen)

        goombas = [goomba for goomba in goombas if not goomba.is_out]

        score_text = font_small.render(f'SCORE: {score}', True, (255, 255, 255))
        time_text = font_small.render(f'TIME: {elapsed_time}', True, (255, 255, 255))
        screen.blit(score_text, (20, 20))
        screen.blit(time_text, (20, 60))

        pygame.display.flip()
        clock.tick(FPS)

show_intro_screen()
game(difficulty)
