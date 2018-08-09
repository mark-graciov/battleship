from rest_framework import routers

from battleship_game.views import GameViewSet

router = routers.SimpleRouter()
router.register(r'games', GameViewSet)
