from django.test import TestCase

from battleship_game.models import Game, GameStatus, GameCell
from battleship_game.serializers import GameSerializer, AttackCellSerializer


class GameSerializerTestCase(TestCase):

    def setUp(self):
        Game.objects.all().delete()

    def test_game_serialization(self):
        game = Game(id=1, game_status=GameStatus.FINISHED.value)
        game.opponent_grid[1][1] = GameCell.SHIP.value

        serializer = GameSerializer(game)
        data = serializer.data
        self.assertEqual(1, data['id'])
        self.assertEqual(GameStatus.FINISHED.value, data['status'])
        self.assertEqual(10, len(data['opponentGrid']))
        self.assertEqual(GameCell.SHIP.value, data['opponentGrid'][1][1])

    def test_create_new_game(self):
        serializer = GameSerializer(data={})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        db_objects = Game.objects.all()

        self.assertEqual(1, db_objects.count())
        self.assertEqual(GameStatus.IN_PROGRESS.value, db_objects[0].game_status)


class AttackCellSerializerTestCase(TestCase):

    def test_valid_data_serialization(self):
        data = {
            'row': 1,
            'column': 2
        }

        serializer = AttackCellSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_missing_row_serialization(self):
        data = {
        }

        serializer = AttackCellSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual('required', serializer.errors['row'][0].code)
        self.assertEqual('required', serializer.errors['column'][0].code)

    def test_invalid_min_value_serialization(self):
        data = {
            'row': -1,
            'column': -1
        }

        serializer = AttackCellSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual('min_value', serializer.errors['row'][0].code)
        self.assertEqual('min_value', serializer.errors['column'][0].code)

    def test_invalid_max_value_serialization(self):
        data = {
            'row': 10,
            'column': 11
        }

        serializer = AttackCellSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual('max_value', serializer.errors['row'][0].code)
        self.assertEqual('max_value', serializer.errors['column'][0].code)