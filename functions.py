# Модуль вспомогательных функций
import sys
import os
import pygame
from datetime import datetime


class MyTimer():
    # timer.start() запуск таймера
    # timer.pause() пауза таймера
    # timer.resume() возобновление таймера после паузы
    # timer.get() получение времени таймера

    def __init__(self):
        # print('Initializing timer')
        self.timestarted = None
        self.timepaused = None
        self.paused = False

    def start(self):
        # Старт таймер, запись текущего времени
        self.timestarted = datetime.now()

    def pause(self):
        # Пайза таймера
        if self.timestarted is None:
            raise ValueError("Timer not started")
        if self.paused:
            raise ValueError("Timer is already paused")
        # print('Pausing timer')
        self.timepaused = datetime.now()
        self.paused = True

    def resume(self):
        # возобновление таймера после паузы
        if self.timestarted is None:
            raise ValueError("Timer not started")
        if not self.paused:
            raise ValueError("Timer is not paused")
        # print('Resuming timer')
        pausetime = datetime.now() - self.timepaused
        self.timestarted = self.timestarted + pausetime
        self.paused = False

    def get(self):
        # Возвращает результирующее время работы таймер за вычетом паузы
        if self.timestarted is None:
            raise ValueError("Timer not started")
        if self.paused:
            return self.timepaused - self.timestarted
        else:
            return datetime.now() - self.timestarted


def read_db(cur1):
    return cur1.execute(
        'SELECT * '
        'FROM records'
        ' ORDER BY total'
        # ' id'
        ' ASC '
        # ' DESC '
        'LIMIT 5'
    ).fetchall()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print(f"Файл с изображением '{name}' не найден")
        raise SystemExit(message)
    image = image.convert_alpha()
    if colorkey is None:
        colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))
    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def terminate():
    # Корректное завершение программы
    pygame.quit()
    sys.exit()
