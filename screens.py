import pygame
import sqlite3
from functions import load_image, terminate, read_db

FPS = 50
WIDTH = 600
HEIGHT = 600
need_input = False
input_text = ""
con = sqlite3.connect('records_db.db')
cur = con.cursor()


class Buttons(pygame.sprite.Sprite):
    def __init__(self, btn, x, y, size=(WIDTH, HEIGHT), name=None, group=None):
        # Кнопка с изображением и надписью
        # btn - файл изорбражения
        # txt -  файл надписи
        # x -  координата размещения x
        # y -  координаты размещения y
        # size -  размер экрана
        # proc -  размер кнопки в процентах от экрана по высоте
        # name -  внутренее имя

        super().__init__()
        self.txt = load_image(btn)
        self.size = self.txt.get_rect().size
        if size is not None:
            ratio = self.size[0] / self.size[1]
            self.size = (int(size[1] // 10 * ratio), size[1] // 10)

        self.btn = load_image(btn, self.size)
        # 2 возможных состояния кнопки - не нажата и нажата
        self.normal_btn = self.btn
        self.check_btn = load_image('Button01.png', self.size)

        self.rect = pygame.Rect((x, y), self.size)
        self.resize(self.size)
        self.name = name
        if group is not None:
            group.add(self)

    def update(self, screen):
        # Обновление кнопки в кадре
        # screen - на какой поверхности размещается
        screen.blit(self.btn, self.rect)
        screen.blit(self.txt, self.rect)
        self.screen = screen

    def resize(self, size):
        # Изменение размеров кнопки
        # size: кортеж (ширина, высота)
        self.btn = pygame.transform.scale(self.btn, size)
        self.txt = pygame.transform.scale(self.txt, size)

    def choose_button(self):
        # Смена изображения кнопки при выборе
        self.btn = self.check_btn
        self.update(self.screen)

    # def un_choose_button(self):
    #     # Смена изображения кнопки при выборе другой кнопки
    #     self.btn = self.normal_btn
    #     self.update(self.screen)


def pause_screen(screen):
    size = screen.get_size()
    intro_text = ["ПАУЗА"]
    font = pygame.font.Font(None, 100)
    text_coord = size[0] // 3
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('grey'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = size[1] // 3
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # print('pause')
                return


def start_screen(screen):
    # Стартовый экран
    global need_input, input_text
    size = screen.get_size()
    # print('start_screen')
    intro_text = ["Правила игры:",
                  "Собрать все призы,",
                  "избегая противника",
                  '', '', '', '', '', '',
                  '                 Введите имя:']

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    level_buttons = pygame.sprite.Group()
    easy = Buttons('Button01.png', 400, size[1] * 4 // 7, name='easy', size=size, group=level_buttons)
    normal = Buttons('Button02.png', 400, size[1] * 5 // 7, name='normal', size=size, group=level_buttons)
    hard = Buttons('Button03.png', 400, size[1] * 6 // 7, name='hard', size=size, group=level_buttons)
    level_buttons.update(screen)
    font = pygame.font.Font(None, 30)
    text_coord = 10
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('White'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    pygame.display.flip()
    need_input = True
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if need_input and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    need_input = False
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    if len(input_text) < 10:
                        input_text += event.unicode
                        font = pygame.font.Font(None, 30)
                        text_coord = 10
                        string_rendered = font.render(input_text, True, pygame.Color('White'))
                        intro_rect = string_rendered.get_rect()
                        text_coord += size[1] // 2.14
                        intro_rect.top = text_coord
                        intro_rect.x = 260
                        text_coord += intro_rect.height
                        screen.blit(string_rendered, intro_rect)
                        pygame.display.flip()
                        # print(input_text)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Создаем микро-кнопку для отслеживания нажатия кнопок
                mouse = Buttons('Button01.png', x, y)
                mouse.resize((1, 1))
                if easy.rect.colliderect(mouse.rect):
                    # начинаем игру легкой сложности
                    return 1
                elif normal.rect.colliderect(mouse.rect):
                    # начинаем игру средней сложности
                    return 2
                elif hard.rect.colliderect(mouse.rect):
                    # начинаем игру высокой сложности
                    return 3


def end_happy_screen(screen):
    # Заставка, если игра выиграна
    intro_text = ["YOU WIN!"]
    list_result = read_db(cur)
    size = screen.get_size()
    fon = pygame.transform.scale(load_image('gamewin.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    finish_buttons = pygame.sprite.Group()
    exit_bt = Buttons('Button_exit.png', 400, size[1] * 4 // 7, name='exit_bt', size=size, group=finish_buttons)
    records_bt = Buttons('Button_res.png', 400, size[1] * 5 // 7, name='res_bt', size=size, group=finish_buttons)
    finish_buttons.update(screen)
    font = pygame.font.Font(None, 50)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('White'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 60
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Создаем микро-кнопку для отслеживания нажатия кнопок
                mouse = Buttons('Button01.png', x, y)
                mouse.resize((1, 1))
                if exit_bt.rect.colliderect(mouse.rect):
                    # выходим
                    terminate()
                elif records_bt.rect.colliderect(mouse.rect):
                    # font = pygame.font.Font(None, 30)
                    font = pygame.font.SysFont('arial', 25)
                    text_coord = 100
                    l_result = ['Игрок     Уровень   Минуты     Секунды    Итого']
                    l_result += [
                        ''.join([str(x).ljust(15, ' ') for x in difficult_name[1:]]) for
                        difficult_name in list_result]
                    for line in l_result:
                        string_rendered = font.render(line, True, pygame.Color('White'))
                        intro_rect = string_rendered.get_rect()
                        text_coord += 10
                        intro_rect.top = text_coord
                        intro_rect.x = 60
                        text_coord += intro_rect.height
                        screen.blit(string_rendered, intro_rect)
                    pygame.display.flip()
                    # return 2


def end_screen(screen):
    # Заставка, если игра проиграна
    intro_text = ["GAME OVER", str()]
    size = screen.get_size()

    fon = pygame.transform.scale(load_image('gameover.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    finish_buttons = pygame.sprite.Group()
    exit_bt = Buttons('Button_exit.png', 400, size[1] * 1 // 7, name='exit_bt', size=size, group=finish_buttons)
    font = pygame.font.Font(None, 100)
    finish_buttons.update(screen)
    text_coord = 250
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 90
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Создаем микро-кнопку для отслеживания нажатия кнопок
                mouse = Buttons('Button01.png', x, y)
                mouse.resize((1, 1))
                if exit_bt.rect.colliderect(mouse.rect):
                    # выходим
                    terminate()