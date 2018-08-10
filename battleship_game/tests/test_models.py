from django.test import TestCase

from battleship_game.models import Game, GameStatus, GameCell, AttackStatus


class GameTestCase(TestCase):

    def setUp(self):
        Game.objects.all().delete()

    def test_new_game_defaults(self):
        game = Game()

        self.assertEqual(GameStatus.IN_PROGRESS.value, game.game_status)
        self.assertEqual(Game.GRID_SIZE, len(game.opponent_grid))

    def test_reset_grid(self):
        game = Game()
        game.opponent_grid[1][1] = GameCell.SHIP.value

        game.reset_grid()

        self.assertEqual(Game.GRID_SIZE, len(game.opponent_grid))
        self.assertEqual(GameCell.EMPTY.value, game.opponent_grid[1][1])

    def test_attack_invalid_cell(self):
        game = Game()
        game.opponent_grid[2][3] = GameCell.MISSED.value
        game.save()

        result = game.attack_cell(2, 3)
        self.assertEqual(AttackStatus.INVALID, result.attack_status)

    def test_attack_cell_in_finished_game(self):
        game = Game(game_status=GameStatus.FINISHED.value)
        game.save()

        result = game.attack_cell(2, 3)
        self.assertEqual(AttackStatus.INVALID, result.attack_status)

    def test_attack_empty_cell(self):
        game = Game()
        game.save()

        result = game.attack_cell(2, 3)
        self.assertEqual(AttackStatus.MISSED, result.attack_status)
        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[2][3])

    def test_attack_cell_kill_center_ship(self):
        game = Game()
        game.opponent_grid[5][5] = GameCell.SHIP.value
        game.save()

        result = game.attack_cell(5, 5)
        self.assertEqual(AttackStatus.KILLED, result.attack_status)
        self.assertEqual(GameStatus.FINISHED.value, game.game_status)
        self.assertEqual(GameCell.KILLED.value, game.opponent_grid[5][5])

        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[5][6])
        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[5][4])
        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[6][5])
        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[4][5])

        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[6][6])
        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[4][4])
        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[6][4])
        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[4][6])

    def test_attack_cell_kill_top_left_ship(self):
        game = Game()
        game.opponent_grid[0][0] = GameCell.SHIP.value
        game.save()

        result = game.attack_cell(0, 0)
        self.assertEqual(AttackStatus.KILLED, result.attack_status)
        self.assertEqual(GameStatus.FINISHED.value, game.game_status)
        self.assertEqual(GameCell.KILLED.value, game.opponent_grid[0][0])

        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[0][1])
        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[1][0])
        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[1][1])

    def test_attack_cell_kill_bottom_right_ship(self):
        game = Game()
        game.opponent_grid[9][9] = GameCell.SHIP.value
        game.save()

        result = game.attack_cell(9, 9)
        self.assertEqual(AttackStatus.KILLED, result.attack_status)
        self.assertEqual(GameStatus.FINISHED.value, game.game_status)
        self.assertEqual(GameCell.KILLED.value, game.opponent_grid[9][9])

        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[8][9])
        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[9][8])
        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[8][8])

    def test_attack_cell_kill_one_of_two_ships(self):
        game = Game()
        game.opponent_grid[5][5] = GameCell.SHIP.value
        game.opponent_grid[3][3] = GameCell.SHIP.value
        game.save()

        result = game.attack_cell(5, 5)
        self.assertEqual(AttackStatus.KILLED, result.attack_status)
        self.assertEqual(GameStatus.IN_PROGRESS.value, game.game_status)
        self.assertEqual(GameCell.KILLED.value, game.opponent_grid[5][5])

        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[5][6])
        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[5][4])
        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[6][5])
        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[4][5])

        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[6][6])
        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[4][4])
        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[6][4])
        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[4][6])

    def test_attack_cell_injure_ship(self):
        game = Game()
        game.opponent_grid[2][2] = GameCell.SHIP.value
        game.opponent_grid[2][3] = GameCell.SHIP.value
        game.save()

        result = game.attack_cell(2, 2)
        self.assertEqual(AttackStatus.INJURED, result.attack_status)
        self.assertEqual(GameStatus.IN_PROGRESS.value, game.game_status)
        self.assertEqual(GameCell.INJURED.value, game.opponent_grid[2][2])
        self.assertEqual(GameCell.SHIP.value, game.opponent_grid[2][3])

        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[3][3])
        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[1][1])
        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[1][3])
        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[3][1])

    def test_attack_cell_injure_large_ship(self):
        game = Game()
        game.opponent_grid[0][0] = GameCell.SHIP.value
        game.opponent_grid[1][0] = GameCell.INJURED.value
        game.opponent_grid[2][0] = GameCell.INJURED.value
        game.opponent_grid[3][0] = GameCell.SHIP.value
        game.save()

        result = game.attack_cell(3, 0)
        self.assertEqual(AttackStatus.INJURED, result.attack_status)
        self.assertEqual(GameStatus.IN_PROGRESS.value, game.game_status)
        self.assertEqual(GameCell.INJURED.value, game.opponent_grid[3][0])
        self.assertEqual(GameCell.SHIP.value, game.opponent_grid[0][0])

        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[4][1])
        self.assertEqual(GameCell.MISSED.value, game.opponent_grid[2][1])

