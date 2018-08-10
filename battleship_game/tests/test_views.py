from unittest.mock import patch, Mock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from battleship_game.factories import create_random_game
from battleship_game.models import Game, AttackCellResponse, AttackStatus


class GameViewSetTestCase(APITestCase):

    def test_games_list(self):
        Game.objects.all().delete()
        game1 = create_random_game()
        game2 = create_random_game()

        response = self.client.get(reverse('game-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(response.data))

        self.assertEqual(2, len(response.data[0]))
        self.assertEqual(game1.pk, response.data[0]['id'])
        self.assertEqual(game2.game_status, response.data[1]['status'])

    def test_game_detail(self):
        Game.objects.all().delete()
        game = create_random_game()

        response = self.client.get(reverse('game-detail', args=[game.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(3, len(response.data))
        self.assertEqual(game.pk, response.data['id'])
        self.assertEqual(game.game_status, response.data['status'])
        self.assertEqual(Game.GRID_SIZE, len(response.data['opponentGrid']))

    @patch('battleship_game.views.GameViewSet.get_object')
    def test_attack_cell_valid(self, view_set_object):
        game = Game(pk=1)
        game.attack_cell = Mock(return_value=AttackCellResponse(AttackStatus.MISSED, game))
        view_set_object.return_value = game

        response = self.client.post(reverse('game-attack', args=[2]), data={'row': 3, 'column': 4}, )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(AttackStatus.MISSED.value, response.data['attackStatus'])
        game.attack_cell.assert_called_once_with(3, 4)

    def test_attack_cell_invalid(self):
        response = self.client.post(reverse('game-attack', args=[2]), data={'row': 3}, )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
