# Battleship

A (very) simplified game of Battleship.

Exposes a list of games and the possibility to create a new random game.
The game is unidirectional - only the player attacks the opponent's board until all ships are killed

## URLS
- `GET games/` - get all games (in progress and finished)
- `POST games/` - create a new random game
- `GET games/<id>/` - get a game with the given <id>
- `POST games/<id>/attack` - attack a cell in the game. 
Requires a payload of row and column. e.g. `{"row": 3, "column": 4}`

## Installation

1. Install PostgreSQL
2. create a user. Default: `bs_admin`
2. `createdb battleship` - create the default database
3. Create a virtual env for the project
4. `pip install -r requirements.txt` - install project dependencies
5. `python manage.py test` - run the tests to confirm everything is ok
6. `python manage.py runserver` - run the server and enjoy :)
