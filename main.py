import pygame
import os
import random
import time

pygame.init()
from pygame.locals import *

Height = 800
Width = 600
Lives = 1
Score = 0
FPS = 120
rows = 1
cols = 1
Enemy_shot = pygame.time.get_ticks()
Cd = 1000
Lost = False
Level = 1
Level_up = False
Lost_count = 0
Delay = 0.005
clock = pygame.time.Clock()

# Creating the game screen

screen = pygame.display.set_mode((Width, Height))
pygame.display.set_caption('Chicken Invaders')

# Set the fonts

menu_font = pygame.font.SysFont("comicsans", 70)
game_font = pygame.font.SysFont("comicsans", 50)
gameover_font = pygame.font.SysFont("comicsans", 60)
play_again_font = pygame.font.SysFont("comicsans", 25)

# Set and scale the images

Background_img = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "Background.jpg")), (Width, Height))
Enemy_img = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "Chicken.png")), (50, 50))
projectile_img = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "Egg.png")), (20, 20))
Laser_img = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "Laser.png")), (20, 20))
ship_img = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "Spaceship.png")), (150, 150))


class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, ):
        pygame.sprite.Sprite.__init__(self)
        self.image = ship_img
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        speed = 2.5
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left - speed >= 0:
            self.rect.x -= speed
        if key[pygame.K_RIGHT] and self.rect.right + speed <= Width:
            self.rect.x += speed
        if key[pygame.K_UP] and self.rect.top - speed >= Height / 2:
            self.rect.y -= speed
        if key[pygame.K_DOWN] and self.rect.top + speed < Height - Height / 7:
            self.rect.y += speed
        if key[pygame.K_SPACE]:
            laser = Laser(self.rect.centerx, self.rect.top)
            if len(Laser_group) < 1:
                Laser_group.add(laser)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for i in range(10, 20):
            img = pygame.transform.scale(pygame.image.load(f"Assets/tile0{i}.png"), (100, 100))
            self.images.append(img)

        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        Speed = 10
        self.counter += 1
        if self.counter >= Speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]
        if self.index >= len(self.images) - 1 and self.counter >= Speed:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = Enemy_img
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.move_direction = 1

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 85:
            self.move_direction *= -1
            self.move_counter *= self.move_direction


class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y, ):
        pygame.sprite.Sprite.__init__(self)
        self.image = Laser_img
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        global Score
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, Enemy_group, True, pygame.sprite.collide_mask):
            Score += 1
            self.kill()
            explosion = Explosion(self.rect.centerx, self.rect.centery)
            Explosion_group.add(explosion)


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, ):
        pygame.sprite.Sprite.__init__(self)
        self.image = projectile_img
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        global Lives
        self.rect.y += 2
        if self.rect.top > Height:
            self.kill()
        if pygame.sprite.spritecollide(self, Spaceship_group, False, pygame.sprite.collide_mask):
            Lives -= 1
            self.kill()
            explosion = Explosion(self.rect.centerx, self.rect.centery)
            Explosion_group.add(explosion)


Spaceship_group = pygame.sprite.Group()
Enemy_group = pygame.sprite.Group()
Laser_group = pygame.sprite.Group()
projectile_group = pygame.sprite.Group()
Explosion_group = pygame.sprite.Group()


# Create the group of enemies, with spacing between them
def create_Enemy():
    for row in range(rows):
        for item in range(cols):
            enemy = Enemy(100 + item * 125, 100 + row * 90)
            Enemy_group.add(enemy)


def menu():
    active = True
    while active:
        screen.blit(Background_img, (0, 0))
        message = menu_font.render("Press any key to start", 1, (255, 255, 255))
        screen.blit(message, (Width / 2 - message.get_width() / 2, Height / 2 - message.get_height() / 2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                active = False
            if event.type == pygame.KEYDOWN:
                main()

    pygame.quit()


def empty_groups(spaceship, laser, explosion, projectile, enemy):
    spaceship.empty()
    laser.empty()
    explosion.empty()
    projectile.empty()
    enemy.empty()


def main():
    global Lives, Score, Enemy_shot, Cd, Delay, Level
    active = True
    Lives = 1
    Score = 0
    clock.tick(FPS)
    empty_groups(Spaceship_group, Laser_group, Explosion_group, projectile_group, Enemy_group)
    player = Spaceship(Width / 2, Height - 50)
    Spaceship_group.add(player)
    create_Enemy()
    while active:
        time.sleep(Delay)
        screen.blit(Background_img, (0, 0))
        Lives_text = game_font.render(f"Lives:{Lives}", 1, (255, 255, 255))
        Score_text = game_font.render(f"Score:{Score}", 1, (255, 255, 255))
        Level_text = game_font.render(f"Level:{Level}", 1, (255, 255, 255))

        screen.blit(Lives_text, (10, 10))
        screen.blit(Score_text, (Width / 2 - Score_text.get_width() / 2, 10))
        screen.blit(Level_text, (Width / 2 + Score_text.get_width() / 2 + Level_text.get_width() / 2, 10))
        curr_time = pygame.time.get_ticks()

        if curr_time - Enemy_shot > Cd and len(projectile_group) < 5 and len(Enemy_group) > 0:
            Attacking_enemy = random.choice(Enemy_group.sprites())
            projectile = Projectile(Attacking_enemy.rect.centerx, Attacking_enemy.rect.bottom)
            projectile_group.add(projectile)
            Enemy_shot = curr_time

        # Game over
        if Lives <= 0:
            global Lost, Lost_count
            Lost = True
            Lost_count += 1
            empty_groups(Spaceship_group, Laser_group, Explosion_group, projectile_group, Enemy_group)
            Gameover = gameover_font.render("You Got Chickened", 1, (255, 255, 255))
            Play_again = play_again_font.render("-press spacebar to play again-", 1, (255, 255, 255))
            screen.blit(Gameover, (Width / 2 - Gameover.get_width() / 2, Height / 2 - Gameover.get_height() / 2))
            screen.blit(Play_again, (
                Width / 2 - Play_again.get_width() / 2,
                Height / 2 + Gameover.get_height() / 2 + Play_again.get_height()))
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE]:
                Lost = False
                # Reset the values
                Level = 1
                Delay = 0.005
                main()

        # Level Up
        if len(Enemy_group) == 0 and Lives:
            global Level_up

            empty_groups(Spaceship_group, Laser_group, Explosion_group, projectile_group, Enemy_group)
            LevelUP = gameover_font.render(f"Level {Level} Complete", 1, (255, 255, 255))
            Next_level = game_font.render("Press space to advance", 1, (255, 255, 255))
            screen.blit(LevelUP, (Width / 2 - LevelUP.get_width() / 2, Height / 2 - LevelUP.get_height() / 2))
            screen.blit(Next_level, (Width / 2 - Next_level.get_width() / 2,
                                     Height / 2 + LevelUP.get_height() / 2 + Next_level.get_height() / 2))


            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE]:
                Level += 1
                Delay *= 0.8
                main()

        if not Lost and not Level_up:
            player.update()
            Enemy_group.update()
            Laser_group.update()
            projectile_group.update()
            Explosion_group.update()

            Enemy_group.draw(screen)
            Spaceship_group.draw(screen)
            Laser_group.draw(screen)
            projectile_group.draw(screen)
            Explosion_group.draw(screen)

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                active = False
    pygame.quit()


menu()
