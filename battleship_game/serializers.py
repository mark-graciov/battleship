from rest_framework import serializers

from battleship_game.factories import create_random_game
from battleship_game.models import Game, GameCell


class GameCellField(serializers.CharField):
    """
    Field that hides the Exiting ship cells
    """

    def to_representation(self, value):
        if GameCell(value) in GameCell.hidden_cells():
            value = GameCell.EMPTY.value

        return super().to_representation(value)


class GameSerializer(serializers.ModelSerializer):
    """
    Main game serializer
    """
    opponentGrid = serializers.ListField(
        child=serializers.ListField(
            child=GameCellField()
        ),
        source='opponent_grid', read_only=True)
    status = serializers.CharField(source='game_status', read_only=True)

    class Meta:
        model = Game
        fields = ('id', 'opponentGrid', 'status')

    def create(self, validated_data):
        instance = create_random_game()

        return instance


class AttackCellSerializer(serializers.Serializer):
    """
    Write only serializer for attack cell calls
    """
    row = serializers.IntegerField(required=True, min_value=0, max_value=Game.GRID_SIZE - 1)
    column = serializers.IntegerField(required=True, min_value=0, max_value=Game.GRID_SIZE - 1)


class AttackResponseSerializer(serializers.Serializer):
    """
    Read only serializer for attack cell response
    """
    attackStatus = serializers.CharField(source='attack_status.value', read_only=True)
    game = GameSerializer(read_only=True)
