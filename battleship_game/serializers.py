from rest_framework import serializers

from battleship_game.factories import create_random_game
from battleship_game.models import Game


class GameSerializer(serializers.ModelSerializer):
    opponentGrid = serializers.ListField(
        child=serializers.ListField(
            child=serializers.CharField()
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
    row = serializers.IntegerField(required=True, min_value=0, max_value=Game.GRID_SIZE - 1)
    column = serializers.IntegerField(required=True, min_value=0, max_value=Game.GRID_SIZE - 1)


class AttackResponseSerializer(serializers.Serializer):
    attackStatus = serializers.CharField(source='attack_status.value', read_only=True)
    game = GameSerializer(read_only=True)
