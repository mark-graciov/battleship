import random

from battleship_game.models import Game, GameCell


def create_random_game():
    """
    Small utility factory function to create a random game
    :return: A new game with randomly placed ships
    """

    game = Game()

    ships = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
    for ship_size in ships:
        _create_random_ship(game.opponent_grid, ship_size)

    game.save()
    return game


def _create_random_ship(grid, ship_size):
    """
    Try to place randomly a ship until succeeded. This is just a small utility, so no fallback is included.
    Placing from the biggest to smallest ships in order will help reduce the overhead of retries.
    A full implementation would try a specific number of times (e.g. 10) then default to the first available spot.
    """
    while True:
        orientation = random.choice(('row', 'col'))

        start_row = random.randrange(10)
        start_col = random.randrange(10)

        if _space_is_available(grid, ship_size, orientation, start_row, start_col):
            _insert_ship(grid, ship_size, orientation, start_row, start_col)
            return


def _space_is_available(grid, ship_size, orientation, start_row, start_col):
    for row, col in _ship_cells(ship_size, orientation, start_row, start_col):
        if row < 0 or row >= Game.GRID_SIZE or col < 0 or col >= Game.GRID_SIZE:
            return False

        if not (_is_empty(grid, row, col)
                and _is_empty(grid, row - 1, col) and _is_empty(grid, row + 1, col)
                and _is_empty(grid, row, col - 1) and _is_empty(grid, row, col + 1)
                and _is_empty(grid, row + 1, col + 1) and _is_empty(grid, row - 1, col - 1)
                and _is_empty(grid, row + 1, col - 1) and _is_empty(grid, row - 1, col + 1)):
            return False

    return True


def _is_empty(grid, row, col):
    if row < 0 or row >= Game.GRID_SIZE or col < 0 or col >= Game.GRID_SIZE:
        return True

    return grid[row][col] == GameCell.EMPTY.value


def _insert_ship(grid, ship_size, orientation, start_row, start_col):
    for row, col in _ship_cells(ship_size, orientation, start_row, start_col):
        grid[row][col] = GameCell.SHIP.value


def _ship_cells(ship_size, orientation, start_row, start_col):
    row = start_row
    col = start_col

    row_increment = 1 if orientation == 'row' else 0
    col_increment = 1 if orientation == 'col' else 0

    for _ in range(ship_size):
        yield (row, col)

        row += row_increment
        col += col_increment
