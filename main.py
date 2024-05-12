import pygame
import os
import random
import neat
import math
import pickle
import copy

pygame.init()

WIDTH = 800
HEIGHT = 800

class Player():
    PLAYER_UP = pygame.image.load('./assets/player-up.png')
    PLAYER_LEFT = pygame.image.load('./assets/player-left.png')
    PLAYER_RIGHT = pygame.image.load('./assets/player-right.png')
    PLAYER_DOWN = pygame.image.load('./assets/player-down.png')

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = pygame.transform.scale(self.PLAYER_UP, (50, 50))
        self.rect = self.img.get_rect(center=(self.x, self.y))
        self.center = (self.rect.x + (self.img.get_size()[0] / 2), self.rect.y + (self.img.get_size()[1] / 2))
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.hp = 100
        # self.good_food = 0
        self.distances = []
        self.coordinates_food = []
        self.collected = 0
    def update(self):

        self.vel_x = 0
        self.vel_y = 0

        self.center = (self.rect.x + (self.img.get_size()[0] / 2), self.rect.y + (self.img.get_size()[1] / 2))

        if self.hp > 100:
            self.hp = 100

        if self.rect.x > WIDTH:
            self.rect.x = 10
        if self.rect.x < -20:
            self.rect.x = WIDTH
        if self.rect.y > HEIGHT:
            self.rect.y = 10
        if self.rect.y < -20:
            self.rect.y = HEIGHT

        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

    def collide(self, walls, genome):
        # collision
        for wall in walls:
            if wall.colliderect(self.rect.x + self.vel_x, self.rect.y, self.width, self.height):
                self.vel_x = 0
                self.hp -= 100
                genome.fitness -= 10
            if wall.colliderect(self.rect.x, self.rect.y + self.vel_y, self.width, self.height):
                self.vel_y = 0
                self.hp -= 100
                genome.fitness -= 10
    def draw(self, screen):
        screen.blit(self.img, (self.rect.x, self.rect.y))

class Food():

        GOOD_FOOD = pygame.image.load('./assets/good-food.png')
        BAD_FOOD = pygame.image.load('./assets/bad-food.png')

        def __init__(self, x, y, type):
            self.type = type
            self.x = x
            self.y = y
            self.active = True
            if self.type == 1:
                self.img = self.GOOD_FOOD
            if self.type == 2:
                self.img = self.BAD_FOOD

            self.rect = self.img.get_rect(center=(self.x, self.y))
            self.center = (self.rect.x + (self.img.get_size()[0] / 2), self.rect.y + (self.img.get_size()[1] / 2))

        def draw(self, screen):
            self.center = (self.rect.x + (self.img.get_size()[0] / 2), self.rect.y + (self.img.get_size()[1] / 2))
            screen.blit(self.img, (self.rect.x, self.rect.y))

good_food = [Food(random.randint(50, 750), random.randint(50, 750), 1) for i in range(60) ]
bad_food = [Food(random.randint(50, 750), random.randint(50, 750), 2) for i in range(20) ]
saved_food_array = []
saved_parameters = []
for food in good_food:
    saved_food_array.append(food)
    saved_parameters.append((food.rect.x, food.rect.y, food.type))
for food in bad_food:
    saved_food_array.append(food)
    saved_parameters.append((food.rect.x, food.rect.y, food.type))

show_lasers = True
def main(genomes, config):

    global show_lasers
    global saved_parameters
    global good_food

    good_food = [Food(random.randint(50, 750), random.randint(50, 750), 1) for i in range(100)]
    bad_food = [Food(random.randint(50, 750), random.randint(50, 750), 2) for i in range(10)]
    food_array = []
    for food in good_food:
        food_array.append(food)
    for food in bad_food:
        food_array.append(food)

    nets = []
    ge = []
    players = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        players.append(Player(400, 400))
        g.fitness = 0
        ge.append(g)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('timesnewroman', 30)
    timer = 0
    food_timer = 0
    hp_timer = 5
    no_food_timer = 20
    active_food = 0

    walls = [
        pygame.Rect(0, 0, 20, HEIGHT),
        pygame.Rect(0, 0, WIDTH, 20),
        pygame.Rect(780, 0, 20, HEIGHT),
        pygame.Rect(0, 780, WIDTH, 20),
    ]

    run = True
    while run:
        clock.tick(60)
        timer += 1
        food_timer += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        if len(players) <= 0:
            break

        key = pygame.key.get_pressed()
        if key[pygame.K_m]:
            show_lasers = True
        if key[pygame.K_n]:
            show_lasers = False

        screen.fill((255,255,255))
        player_hp = font.render(f"Player hp: {players[0].hp}", True, (0,0,0))
        player_hp_rect = player_hp.get_rect().center = (20, 20)
        player_collected = font.render(f"Collected: {players[0].collected}", True, (0, 0, 0))
        player_collected_rect = player_collected.get_rect().center = (20, 50)

        if timer >= hp_timer:
            timer = 0
            for player in players:
                player.hp -= 1
        if food_timer >= no_food_timer:
            for x, player in enumerate(players):
                ge[x].fitness -= 1

        for food in food_array:
            if food.active:
                for x, player in enumerate(players):
                    if food.rect.colliderect(player.rect):
                        for coord in player.coordinates_food:
                            if coord[0] == food.center and food.type == 1:
                                food_timer = 0
                                player.hp += 10
                                ge[x].fitness += 1*player.collected
                        if food.type == 2:
                            player.hp -= 100
                            ge[x].fitness -= 20
                        food.active = False
                        player.collected += 1

                food.draw(screen)
                # food.rect.x = 100000
                # food.rect.y = 100000
            if show_lasers:
                pygame.draw.rect(screen, 'green', food.rect, 1)

        for wall in walls:
            pygame.draw.rect(screen, (0,0,0,0.2), wall)
            if show_lasers:
                pygame.draw.rect(screen, 'green', wall, 1)

        for x, player in enumerate(players):
            player.coordinates_food = []
            for food in food_array:
                active_food += 1
            if active_food <= 0:
                print("WIN")
            if player.hp > 50:
                ge[x].fitness += .5
            else:
                ge[x].fitness -= .1
            DENSITY = 10
            RADIUS = 1000
            data = []
            for food in food_array:
                if food.type == 1 and food.active:
                    player.coordinates_food.append((food.center, ((player.center[0] - food.center[0])**2 + (player.center[1] - food.center[1])**2)**0.5))
            player.coordinates_food = sorted(player.coordinates_food, key = lambda x: x[1])[:5]
            for distance in player.coordinates_food:
                data.append(distance[1])
                if show_lasers:
                    if x == 0:
                        pygame.draw.line(screen, 'red', player.center, distance[0], 2)
                        pygame.draw.circle(screen, 'red', distance[0], 4)
            for i in range(DENSITY):
                mouse_pos = (player.center[0], player.center[1])
                pos_fin = (RADIUS * math.cos(2 * math.pi / DENSITY * i) + mouse_pos[0],
                           RADIUS * math.sin(2 * math.pi / DENSITY * i) + mouse_pos[1])
                for food in food_array:
                    if food.type == 2 and food.active:
                        rect = food.rect
                        if rect.collidepoint(mouse_pos) == False:
                            for extrem_1, extrem_2 in [(rect.bottomright, rect.topright), (rect.topright, rect.topleft),
                                                       (rect.topleft, rect.bottomleft),
                                                       (rect.bottomleft, rect.bottomright)]:
                                deno = (mouse_pos[0] - pos_fin[0]) * (extrem_1[1] - extrem_2[1]) - (
                                        mouse_pos[1] - pos_fin[1]) * (extrem_1[0] - extrem_2[0])
                                if deno != 0:
                                    param_1 = ((extrem_2[0] - mouse_pos[0]) * (mouse_pos[1] - pos_fin[1]) - (
                                            extrem_2[1] - mouse_pos[1]) * (mouse_pos[0] - pos_fin[0])) / deno
                                    param_2 = ((extrem_2[0] - mouse_pos[0]) * (extrem_2[1] - extrem_1[1]) - (
                                            extrem_2[1] - mouse_pos[1]) * (extrem_2[0] - extrem_1[0])) / deno
                                    if 0 <= param_1 <= 1 and 0 <= param_2 <= 1:
                                        p_x = mouse_pos[0] + param_2 * (pos_fin[0] - mouse_pos[0])
                                        p_y = mouse_pos[1] + param_2 * (pos_fin[1] - mouse_pos[1])
                                        pos_fin = (p_x, p_y)
                for wall in walls:
                    rect = wall
                    if rect.collidepoint(mouse_pos) == False:
                        for extrem_1, extrem_2 in [(rect.bottomright, rect.topright), (rect.topright, rect.topleft),
                                                   (rect.topleft, rect.bottomleft),
                                                   (rect.bottomleft, rect.bottomright)]:
                            deno = (mouse_pos[0] - pos_fin[0]) * (extrem_1[1] - extrem_2[1]) - (
                                    mouse_pos[1] - pos_fin[1]) * (extrem_1[0] - extrem_2[0])
                            if deno != 0:
                                param_1 = ((extrem_2[0] - mouse_pos[0]) * (mouse_pos[1] - pos_fin[1]) - (
                                        extrem_2[1] - mouse_pos[1]) * (mouse_pos[0] - pos_fin[0])) / deno
                                param_2 = ((extrem_2[0] - mouse_pos[0]) * (extrem_2[1] - extrem_1[1]) - (
                                        extrem_2[1] - mouse_pos[1]) * (extrem_2[0] - extrem_1[0])) / deno
                                if 0 <= param_1 <= 1 and 0 <= param_2 <= 1:
                                    p_x = mouse_pos[0] + param_2 * (pos_fin[0] - mouse_pos[0])
                                    p_y = mouse_pos[1] + param_2 * (pos_fin[1] - mouse_pos[1])
                                    pos_fin = (p_x, p_y)
                data.append(((player.center[0] - pos_fin[0]) ** 2 + (player.center[1] - pos_fin[1]) ** 2) ** 0.5)
                if show_lasers:
                    if x == 0:
                        pygame.draw.line(screen, 'green', mouse_pos, pos_fin)
                        pygame.draw.circle(screen, 'green', pos_fin, 4)
            data.append(player.hp)
            data.append(player.center[0])
            data.append(player.center[1])
            data.append(player.collected)
            output = nets[x].activate(data)
            decision = output.index(max(output))

            if decision == 0:

                player.vel_x = 0
                player.vel_y = 0

                player.vel_x -= player.speed
                player.img = pygame.transform.scale(player.PLAYER_LEFT, (50, 50))

                # collision
                player.collide(walls, ge[x])

                player.rect.x += player.vel_x
                player.rect.x += player.vel_y

            if decision == 1:

                player.vel_x = 0
                player.vel_y = 0

                player.vel_x += player.speed
                player.img = pygame.transform.scale(player.PLAYER_RIGHT, (50, 50))

                # collision
                player.collide(walls, ge[x])

                player.rect.x += player.vel_x
                player.rect.x += player.vel_y

            if decision == 2:
                player.vel_x = 0
                player.vel_y = 0

                player.vel_y -= player.speed
                player.img = pygame.transform.scale(player.PLAYER_UP, (50, 50))

                # collision
                player.collide(walls, ge[x])

                player.rect.x += player.vel_x
                player.rect.y += player.vel_y
            if decision == 3:
                player.vel_x = 0
                player.vel_y = 0

                player.vel_y += player.speed
                player.img = pygame.transform.scale(player.PLAYER_DOWN, (50, 50))

                # collision
                player.collide(walls, ge[x])

                player.rect.x += player.vel_x
                player.rect.y += player.vel_y

            if player.hp <= 0:
                ge[x].fitness -= 10
                ge.pop(x)
                players.pop(x)
                nets.pop(x)

            player.update()
            player.draw(screen)
            if show_lasers:
                pygame.draw.rect(screen, 'green', player.rect, 1)
        screen.blit(player_hp, player_hp_rect)
        screen.blit(player_collected, player_collected_rect)

        pygame.display.update()

def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
						neat.DefaultSpeciesSet, neat.DefaultStagnation,
						config_file)

    # p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-339')
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(10))
    winner = p.run(main, 3000)

    with open('best.pickle', 'wb') as f:
        pickle.dump(winner, f)

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
