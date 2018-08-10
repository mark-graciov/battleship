from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from battleship_game.models import Game
from battleship_game.serializers import GameSerializer, AttackCellSerializer, AttackResponseSerializer


class GameViewSet(viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    @action(detail=True, methods=['post'], url_path='attack', url_name='attack')
    def attack_cell(self, request, pk=None):
        attack_cell = AttackCellSerializer(data=request.data)

        if attack_cell.is_valid(raise_exception=True):
            game = self.get_object()
            row = attack_cell.validated_data['row']
            col = attack_cell.validated_data['column']
            response = game.attack_cell(row, col)
            response_serializer = AttackResponseSerializer(response)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
