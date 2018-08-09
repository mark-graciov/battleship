from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from battleship_game.models import Game
from battleship_game.serializers import GameSerializer, AttackCellSerializer


class GameViewSet(viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    @action(detail=True, methods=['post'], url_path='attack', url_name='attack')
    def attack_cell(self, request, pk=None):
        attack_cell = AttackCellSerializer(data=request.data)

        if attack_cell.is_valid():
            game = self.get_object()
            row = attack_cell.validated_data['row']
            col = attack_cell.validated_data['column']
            result = game.attack_cell(row, col)
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(attack_cell.errors, status=status.HTTP_400_BAD_REQUEST)
