from collections import namedtuple
from enum import Enum

from django.contrib.postgres.fields import ArrayField
from django.db import models

AttackCellResponse = namedtuple('AttackCellResponse', ('attack_status', 'game'))


class AttackStatus(Enum):
    INVALID = 'INVALID'
    MISSED = 'MISSED'
    INJURED = 'INJURED'
    KILLED = 'KILLED'


class DBEnum(Enum):
    @classmethod
    def choices(cls):
        return [(c.value, c.value) for c in cls]


class GameStatus(DBEnum):
    IN_PROGRESS = 'IN_PROGRESS'
    FINISHED = 'FINISHED'


class GameCell(DBEnum):
    EMPTY = ' '
    MISSED = '.'
    INJURED = 'i'
    KILLED = 'x'
    SHIP = 'o'

    @classmethod
    def opened_cells(cls):
        return [cls.MISSED, cls.INJURED, cls.KILLED]

    @classmethod
    def alive_cells(cls):
        return [cls.SHIP, cls.INJURED]

    @classmethod
    def hidden_cells(cls):
        return [cls.SHIP]


class Game(models.Model):
    GRID_SIZE = 10

    opponent_grid = ArrayField(
        ArrayField(models.CharField(max_length=1, choices=GameCell.choices(), default=GameCell.EMPTY.value),
                   size=GRID_SIZE),
        size=GRID_SIZE)

    game_status = models.CharField(max_length=50, choices=GameStatus.choices(), default=GameStatus.IN_PROGRESS.value)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset_grid()

    def reset_grid(self):
        """
        Reset the grid to all EMPTY
        """
        self.opponent_grid = [
            [GameCell.EMPTY.value for _ in range(0, Game.GRID_SIZE)] for _ in range(0, Game.GRID_SIZE)
        ]

    def attack_cell(self, row, column) -> AttackCellResponse:
        """
        Attack a cell on the opponent grid.
        Returns the attack result and updates the board and game status according to the ships left
        :param row: attack row
        :param column: attack column
        :return: AttackCellResponse
        """
        cell_value = self.opponent_grid[row][column]

        if GameStatus(self.game_status) is GameStatus.FINISHED or GameCell(cell_value) in GameCell.opened_cells():
            return AttackCellResponse(AttackStatus.INVALID, self)

        if GameCell(cell_value) is GameCell.EMPTY:
            self.opponent_grid[row][column] = GameCell.MISSED.value
            self.save()
            return AttackCellResponse(AttackStatus.MISSED, self)

        if GameCell(cell_value) is GameCell.SHIP:
            if self._is_last_ship_cell(row, column):
                # kill
                self._kill_ship(row, column)
                if self._opponent_ship_cells_left() == 0:
                    self.game_status = GameStatus.FINISHED.value

                self.save()
                return AttackCellResponse(AttackStatus.KILLED, self)
            else:
                # injure
                self.opponent_grid[row][column] = GameCell.INJURED.value
                self._mark_corners_missed(row, column)
                self.save()
                return AttackCellResponse(AttackStatus.INJURED, self)

    def _is_last_ship_cell(self, origin_row, origin_col):
        increments = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for row_increment, col_increment in increments:
            row = origin_row
            col = origin_col
            while True:
                row += row_increment
                col += col_increment
                if self._over_board(row, col) or GameCell(self.opponent_grid[row][col]) not in GameCell.alive_cells():
                    break

                if GameCell(self.opponent_grid[row][col]) is GameCell.SHIP:
                    return False

        return True

    def _kill_ship(self, origin_row, origin_col):
        increments = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for row_increment, col_increment in increments:
            row = origin_row
            col = origin_col
            while True:
                row += row_increment
                col += col_increment
                if self._over_board(row, col):
                    break

                if GameCell(self.opponent_grid[row][col]) in GameCell.alive_cells():
                    self.opponent_grid[row][col] = GameCell.KILLED.value
                    self._mark_corners_missed(row, col)
                elif GameCell(self.opponent_grid[row][col]) is GameCell.EMPTY:
                    self.opponent_grid[row][col] = GameCell.MISSED.value
                else:
                    break

        self.opponent_grid[origin_row][origin_col] = GameCell.KILLED.value
        self._mark_corners_missed(origin_row, origin_col)

    def _mark_corners_missed(self, origin_row, origin_col):
        increments = [(1, 1), (-1, -1), (1, -1), (-1, 1)]
        for row_increment, col_increment in increments:
            row = origin_row + row_increment
            col = origin_col + col_increment
            if not self._over_board(row, col):
                self.opponent_grid[row][col] = GameCell.MISSED.value

    def _opponent_ship_cells_left(self):
        return sum([
            sum([1 for cell in row if GameCell(cell) is GameCell.SHIP])
            for row in self.opponent_grid
        ])

    @staticmethod
    def _over_board(row, col):
        if row < 0 or row >= Game.GRID_SIZE or col < 0 or col >= Game.GRID_SIZE:
            return True
