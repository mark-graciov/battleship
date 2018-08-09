from enum import Enum

from django.contrib.postgres.fields import ArrayField
from django.db import models


class DBEnum(Enum):
    @classmethod
    def choices(cls):
        return [(c, c.value) for c in cls]


class GameStatus(DBEnum):
    IN_PROGRESS = 'IN_PROGRESS'
    FINISHED = 'FINISHED'


class GameCell(DBEnum):
    EMPTY = ' '
    MISSED = '.'
    INJURED = 'i'
    KILLED = 'x'
    SHIP = 'o'


class Game(models.Model):
    GRID_SIZE = 10

    opponent_grid = ArrayField(
        ArrayField(models.CharField(max_length=1, choices=GameCell.choices(), default=GameCell.EMPTY.value),
                   size=GRID_SIZE),
        size=GRID_SIZE)

    game_status = models.CharField(max_length=20, choices=GameStatus.choices(), default=GameStatus.IN_PROGRESS.value)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset_grid()

    def attack_cell(self, row, column):
        pass

    def reset_grid(self):
        self.opponent_grid = [
            [GameCell.EMPTY.value for _ in range(0, Game.GRID_SIZE)] for _ in range(0, Game.GRID_SIZE)
        ]
