import os
import pygame
import screens
import time
import sqlite3
import functions


pygame.init()
pygame.key.set_repeat(200, 70)
pygame.display.set_caption('Тачки')
FPS = 50
WIDTH = 600
HEIGHT = 600
STEP = 10
count_score = 0
mode = 1
bad = 0
is_paused = False

pygame.font.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
start_sound = pygame.mixer.Sound('music/startraces.mp3')
score_sound = pygame.mixer.music
play_sound = pygame.mixer.music
score_sound = pygame.mixer.Sound("music/get score.mp3")
lose_sound = pygame.mixer.Sound("music/lose.mp3")
help_sound = pygame.mixer.Sound("music/get help.mp3")
win_sound = pygame.mixer.Sound("music/champions.mp3")
play_sound.load("music/play.mp3")

player = None
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
walls = pygame.sprite.Group()
scores = pygame.sprite.Group()
helps = pygame.sprite.Group()
bads = pygame.sprite.Group()
help_time = 0
con = sqlite3.connect('records_db.db')
cur = con.cursor()
t = functions.MyTimer()


class Camera:
    #  начальный сдвиг камеры и размер поля для реализации циклического сдвига
    def __init__(self, field_size):
        self.dx = 0
        self.dy = 0
        self.field_size = field_size

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        # координаты клетки, если она слева за границей экрана
        if obj.rect.x < -obj.rect.width:
            obj.rect.x += (self.field_size[0] + 1) * obj.rect.width
        # координаты клетки, если она справа за границей экрана
        if obj.rect.x >= (self.field_size[0]) * obj.rect.width:
            obj.rect.x += -obj.rect.width * (1 + self.field_size[0])
        obj.rect.y += self.dy
        # координаты клетки, если она вверху за границей экрана
        if obj.rect.y < -obj.rect.height:
            obj.rect.y += (self.field_size[1] + 1) * obj.rect.height
        # вычислим координаты клетки, если она внизу за границей экрана
        if obj.rect.y >= (self.field_size[1]) * obj.rect.height:
            obj.rect.y += -obj.rect.height * (1 + self.field_size[1])

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


# Класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.score: int = 0
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


# Класс плитки
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        if tile_type == 'score':
            scores.add(self)
        if tile_type == 'box':
            walls.add(self)
        if tile_type == 'help':
            helps.add(self)
        if tile_type == 'bad':
            bads.add(self)


# возвращает надпись, содержащую счет игры
def print_score():
    line = f'Игрок: {screens.input_text}  Счет {player.score}'
    font = pygame.font.Font(None, 30)
    return font.render(line, True, pygame.Color('white'))


def write_db(cur2):
    name = screens.input_text
    if name == '':
        name = "unknown"
    # print((str(t.get())[:7]).split(':'))
    minute = (str(t.get())[:7]).split(':')[1]
    second = str(t.get())[:7].split(':')[2]
    total = int(minute) * 60 + int(second) - help_time
    minute = total // 60
    second = total % 60
    cur2.execute(
        "INSERT INTO records "
        f"VALUES (NULL, '{name}','{mode}', '{minute}', {second}, {total})"
    )
    cur2.connection.commit()


# собрать приз
def get_scores(pl, scs):
    # print(functions.read_db(cur))
    player.score += 1
    # print(count_score)
    # print(player.score)
    for sc in scs:
        if pygame.sprite.collide_rect(pl, sc):
            sc.kill()
            score_sound.play()
        if player.score == count_score:
            play_sound.stop()
            win_sound.play()
            vol = 0.8
            win_sound.set_volume(vol)
            write_db(cur)
            screens.end_happy_screen(screen)


# получить помощь Мэтра для уменьшения потраченного времени
def get_help(pl, hs):
    global help_time
    help_time += 5
    # print("help", help)
    for hl in hs:
        if pygame.sprite.collide_rect(pl, hl):
            hl.kill()
            help_sound.play()


# столкновение с противником
def get_bad(pl, bds):
    global bad
    bad += 1
    play_sound.stop()
    lose_sound.play()
    screens.end_screen(screen)
    # print(bad)
    for bd in bds:
        if pygame.sprite.collide_rect(pl, bd):
            bd.kill()


# возвращает надпись, содержащую время игры
def time_to_end(minute):
    line = f'Прошло:{str(minute)[:7]}'
    # line = str(line)[:7]
    font = pygame.font.Font(None, 30)
    return font.render(line, True, pygame.Color('white'))


def generate_level(level):
    global count_score
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('box', x, y)
            elif level[y][x] == 's':
                count_score += 1
                Tile('empty', x, y)
                Tile('score', x, y)
            elif level[y][x] == 'm':
                Tile('empty', x, y)
                Tile('help', x, y)
            elif level[y][x] == 'b':
                Tile('empty', x, y)
                Tile('bad', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                functions.terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


# Функция загрузки изображения
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print(f"Файл с изображением '{name}' не найден")
        raise SystemExit(message)
    image = image.convert_alpha()
    if colorkey is None:
        # if colorkey == -1:
        colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
        # image.set_colorkey((63, 72, 204))
    return image


# Словарь для выбора изображений клеток
tile_images = \
    {
        'box': load_image('box.png'),
        'empty': load_image('grass.png'),
        'score': load_image('bomb1.png'),
        'help': load_image('cars.jpg'),
        'bad': load_image('bad.png'),
    }

player_image = load_image('mcqueen.png')
tile_width = tile_height = 50

# Запуск музыки на стартовый экран
start_sound.play()


but = screens.start_screen(screen)
# Запуск музыки на игровое поле
mode = but
play_sound.play(-1)
# Музыка стартового экрана останавливается
start_sound.stop()
# выбор сложности игры на стартовом  экране
if but == 1:
    player, level_x, level_y = generate_level(functions.load_level("map.txt"))
elif but == 2:
    player, level_x, level_y = generate_level(functions.load_level("map2.txt"))
elif but == 3:
    player, level_x, level_y = generate_level(functions.load_level("map3.txt"))


camera = Camera((level_x, level_y))

running = True
t.start()
while running:
    t2 = time.time()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and not t.paused:
                t.pause()
                # print(t.paused)
                play_sound.pause()
                screens.pause_screen(screen)
            if event.key == pygame.K_ESCAPE and t.paused:
                t.resume()
                # print(t.paused)
                play_sound.unpause()
            if event.key == pygame.K_LEFT and not t.paused:
                player.rect.x -= STEP
                if pygame.sprite.spritecollideany(player, walls):
                    player.rect.x += STEP
            if event.key == pygame.K_RIGHT and not t.paused:
                player.rect.x += STEP
                if pygame.sprite.spritecollideany(player, walls):
                    player.rect.x -= STEP
            if event.key == pygame.K_UP and not t.paused:
                player.rect.y -= STEP
                if pygame.sprite.spritecollideany(player, walls):
                    player.rect.y += STEP
            if event.key == pygame.K_DOWN and not t.paused:
                player.rect.y += STEP
                if pygame.sprite.spritecollideany(player, walls):
                    player.rect.y -= STEP
            if pygame.sprite.spritecollideany(player, scores):
                get_scores(player, scores)
            if pygame.sprite.spritecollideany(player, helps):
                get_help(player, helps)
            if pygame.sprite.spritecollideany(player, bads):
                get_bad(player, bads)

    camera.update(player)

    for sprite in all_sprites:
        camera.apply(sprite)

    screen.fill(pygame.Color(0, 0, 0))
    tiles_group.draw(screen)
    player_group.draw(screen)
    screen.blit(print_score(), (50, 10))
    screen.blit(time_to_end(t.get()), (350, 10))
    pygame.display.flip()
    clock.tick(FPS)

functions.terminate()
