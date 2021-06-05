import pygame
import os
import random
import time
from pygame import mixer

pygame.init()

Height = 800
Width = 600
Lives = 1
Score = 0
FPS = 120
rows = 4
cols = 4
Enemy_shot = pygame.time.get_ticks()
Shield_shot = pygame.time.get_ticks()
Shield_counter = 0
egg_cd = 2000
shield_cd = 10000
shield_duration = 7000
Lost = False
Level = 1
Level_up = True
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
Lives_img = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "hearth.png")), (45, 45))
Enemy_img = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "Chicken.png")), (50, 50))
Strong_Enemy_img = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "ToughChicken.png")), (50, 50))
projectile_img = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "Egg.png")), (20, 20))
Laser_img = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "Laser.png")), (20, 20))
ship_img = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "Spaceship.png")), (150, 150))
shield_img = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "Shield.png")), (100, 100))
powerup_shield_img = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "powerup_shield.png")), (30, 30))


class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y):
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


class Shield(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = shield_img
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self, spaceship):
        self.rect.x = spaceship.rect.x + 23
        self.rect.y = spaceship.rect.y + 22


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
    def __init__(self, x, y, hit):
        pygame.sprite.Sprite.__init__(self)
        if hit < 2:
            self.image = Enemy_img
        else:
            self.image = Strong_Enemy_img
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.move_direction = 1
        self.hit_points = hit

    def update(self):
        global Score
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 65:
            self.move_direction *= -1
            self.move_counter *= self.move_direction
        if self.hit_points<2:
            dead = True
        else:
            dead = False
        if pygame.sprite.spritecollide(self, Laser_group, False, pygame.sprite.collide_mask):
            Score += 10

            if not dead:
                self.hit_points -= 1
            else:
                self.kill()
                explosion_sound = mixer.Sound("Assets\Explosion.wav")
                explosion_sound.play()
                explosion = Explosion(self.rect.centerx, self.rect.centery)
                Explosion_group.add(explosion)
            Laser_group.empty()


class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = Laser_img
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        laser_sound = mixer.Sound("Assets\Laser.wav")
        laser_sound.play()


    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()



class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, tip):
        pygame.sprite.Sprite.__init__(self)
        if tip == "egg":
            self.image = projectile_img
        elif tip == "shield":
            self.image = powerup_shield_img

        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.tip = tip

    def update(self):
        global Lives, Score, Shield_counter
        if self.rect.top > Height:
            self.kill()

        if self.tip == "egg":
            self.rect.y += 2

            # checking for collision with the spaceship
            if pygame.sprite.spritecollide(self, Spaceship_group, False, pygame.sprite.collide_mask):
                Lives -= 1
                if Score >= 100:
                    Score -= 100
                else:
                    Score = 0
                self.kill()
                explosion = Explosion(self.rect.centerx, self.rect.centery)
                Explosion_group.add(explosion)
                if len(Shield_group) > 0:
                    Shield_group.empty()
                else:
                    shield = Shield(Width / 2, Height - 50)
                    Shield_group.add(shield)
                    Shield_counter = pygame.time.get_ticks()

            # checking for collision with the shield
            if pygame.sprite.spritecollide(self, Shield_group, False, pygame.sprite.collide_mask):
                self.kill()
                if len(Shield_group) > 0:
                    Shield_group.empty()

        if self.tip == "shield":
            self.rect.y += 1
            if pygame.sprite.spritecollide(self, Spaceship_group, False, pygame.sprite.collide_mask):
                shield = Shield(Width / 2, Height - 50)
                Shield_group.add(shield)
                Shield_counter = pygame.time.get_ticks()
                self.kill()


Spaceship_group = pygame.sprite.Group()
Enemy_group = pygame.sprite.Group()
Laser_group = pygame.sprite.Group()
projectile_group = pygame.sprite.Group()
Explosion_group = pygame.sprite.Group()
Shield_group = pygame.sprite.Group()


# Create the group of enemies, with spacing between them
def create_Enemy(level):
    hits = 1
    if level >= 5:
        hits = 2
    for row in range(rows):
        for item in range(cols):
            enemy = Enemy(100 + item * 125, 100 + row * 90, hits)
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


def pause():
    paused = True
    while paused:
        screen.blit(Background_img, (0, 0))
        message = menu_font.render("Game paused", 1, (255, 255, 255))
        screen.blit(message, (Width / 2 - message.get_width() / 2, Height / 2 - message.get_height() / 2))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                paused = False
            if event.type == pygame.KEYDOWN:
                main()


def empty_groups(spaceship, laser, explosion, projectile, enemy, shield):
    spaceship.empty()
    laser.empty()
    explosion.empty()
    projectile.empty()
    enemy.empty()
    shield.empty()


# def spawn_projectile(shot_time, cooldown, projectile_type):
#     global Enemy_shot, Shield_shot
#     curr_time = pygame.time.get_ticks()
#     if curr_time - shot_time > cooldown and len(projectile_group) < 5 and len(Enemy_group) > 0:
#         Attacking_enemy = random.choice(Enemy_group.sprites())
#         projectile = Projectile(Attacking_enemy.rect.centerx, Attacking_enemy.rect.bottom, projectile_type)
#         projectile_group.add(projectile)
#     if projectile_type == "egg":
#         Enemy_shot=curr_time
#     elif projectile_type == "shield":
#         Shield_shot = curr_time


def main():
    global Lives, Score, Enemy_shot, Shield_shot, egg_cd, Delay, Level, Level_up, Shield_counter
    Level_up = True
    active = True
    clock.tick(FPS)
    empty_groups(Spaceship_group, Laser_group, Explosion_group, projectile_group, Enemy_group, Shield_group)
    player = Spaceship(Width / 2, Height - 50)
    Spaceship_group.add(player)
    create_Enemy(Level)
    while active:
        time.sleep(Delay)
        screen.blit(Background_img, (0, 0))
        screen.blit(Lives_img, (7, 3))
        Lives_text = game_font.render(f" x {Lives}", 1, (255, 255, 255))
        Score_text = game_font.render(f"Score:{Score}", 1, (255, 255, 255))
        Level_text = game_font.render(f"Level:{Level}", 1, (255, 255, 255))

        screen.blit(Lives_text, (Lives_img.get_width(), 10))
        screen.blit(Score_text, (Width / 2 - Score_text.get_width() / 2, 10))
        screen.blit(Level_text, (Width / 2 + Score_text.get_width() / 2 + Level_text.get_width() / 2, 10))
        curr_time = pygame.time.get_ticks()

        key = pygame.key.get_pressed()
        if key[pygame.K_p]:
            pause()

        if curr_time - Enemy_shot > egg_cd and len(projectile_group) < 5 and len(Enemy_group) > 0:
            Attacking_enemy = random.choice(Enemy_group.sprites())
            projectile = Projectile(Attacking_enemy.rect.centerx, Attacking_enemy.rect.bottom, "egg")
            projectile_group.add(projectile)
            Enemy_shot = curr_time

        if curr_time - Shield_shot > shield_cd and len(projectile_group) < 5 and len(Enemy_group) > 0:
            Attacking_enemy = random.choice(Enemy_group.sprites())
            projectile = Projectile(Attacking_enemy.rect.centerx, Attacking_enemy.rect.bottom, "shield")
            projectile_group.add(projectile)
            Shield_shot = curr_time

        if curr_time - Shield_counter > shield_duration and len(Shield_group) > 0:
            Shield_group.empty()
            Shield_counter = curr_time

        # Enemy_shot=spawn_projectile(Enemy_shot, egg_cd, "egg")
        # Shield_shot=spawn_projectile(Shield_shot, shield_cd, "shield")

        # Game over
        if Lives <= 0:
            global Lost
            Lost = True

            empty_groups(Spaceship_group, Laser_group, Explosion_group, projectile_group, Enemy_group, Shield_group)
            Gameover = gameover_font.render("You Got Chickened", 1, (255, 255, 255))
            Play_again = play_again_font.render("-press spacebar to play again-", 1, (255, 255, 255))
            screen.blit(Gameover, (Width / 2 - Gameover.get_width() / 2, Height / 2 - Gameover.get_height() / 2))
            screen.blit(Play_again, (
                Width / 2 - Play_again.get_width() / 2,
                Height / 2 + Gameover.get_height() / 2 + Play_again.get_height()))
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE]:
                print("PLAY AGAIN PRESSED")
                Lost = False
                # Reset the values
                Level = 1
                Lives = 1
                Delay = 0.005
                Score = 0
                main()

        # Level Up
        if len(Enemy_group) == 0 and Lives:

            if Level_up:
                Score += 100
                Level_up = False

            empty_groups(Spaceship_group, Laser_group, Explosion_group, projectile_group, Enemy_group, Shield_group)
            LevelUP = gameover_font.render(f"Level {Level} Complete", 1, (255, 255, 255))
            Next_level = game_font.render("Press space to advance", 1, (255, 255, 255))
            screen.blit(LevelUP, (Width / 2 - LevelUP.get_width() / 2, Height / 2 - LevelUP.get_height() / 2))
            screen.blit(Next_level, (Width / 2 - Next_level.get_width() / 2,
                                     Height / 2 + LevelUP.get_height() / 2 + Next_level.get_height() / 2))

            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE]:
                Level += 1

                if Level % 3 == 0:
                    Lives += 1
                Delay *= 0.8
                main()

        if not Lost:
            player.update()
            Enemy_group.update()
            Laser_group.update()
            projectile_group.update()
            Explosion_group.update()
            Shield_group.update(player)

            Enemy_group.draw(screen)
            Spaceship_group.draw(screen)
            Laser_group.draw(screen)
            projectile_group.draw(screen)
            Explosion_group.draw(screen)
            Shield_group.draw(screen)

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                active = False
    pygame.quit()


menu()
