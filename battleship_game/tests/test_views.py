from unittest.mock import patch, Mock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from battleship_game.models import Game


class GameViewSetTestCase(APITestCase):

    @patch('battleship_game.views.GameViewSet.get_object')
    def test_attack_cell_valid(self, view_set_object):
        game = Game(pk=1)
        game.attack_cell = Mock(return_value='TEST_RESPONSE')
        view_set_object.return_value = game

        response = self.client.post(reverse('game-attack', args=[2]), data={'row': 3, 'column': 4}, )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('TEST_RESPONSE', response.data)
        game.attack_cell.assert_called_once_with(3, 4)

    def test_attack_cell_invalid(self):
        response = self.client.post(reverse('game-attack', args=[2]), data={'row': 3}, )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
