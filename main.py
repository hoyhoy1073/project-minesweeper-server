from flask import Flask,  request, jsonify, make_response
from flask_cors import CORS
from minesweeper import Minesweeper, MinesweeperAI
import json
import time

app = Flask(__name__)
# CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})
# CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app, resources={r"/api/*": {"origins": "*"}})

HEIGHT = 5
WIDTH = 5
game = 3
ai = None
revealed = set()
flags = set()
lost = False

@app.route('/api/setup-board')
def setup_board():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    elif request.method == "GET":
        global game
        global ai
        global HEIGHT
        global WIDTH
        height = int(request.args.get("height"))
        width = int(request.args.get("width"))
        mines = eval(request.args.get("mines"))

        # print("Height: ", height)
        # print("Width: ", width)
        # print("Mines: ", mines)

        game = Minesweeper(height, width, 0)
        ai = MinesweeperAI(height, width)

        for mine in mines:
            r, c = list(mine.split('-'))
            game.mines.add((int(r), int(c)))

        time.sleep(0.2)
        return _corsify_actual_response(jsonify({ "data": None, "status": "success" })) 

@app.route('/api/reset')
def reset():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    elif request.method == "GET":
        global game
        global ai
        global revealed
        global flags
        global lost

        game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES)
        ai = MinesweeperAI(height=HEIGHT, width=WIDTH)
        revealed = set()
        flags = set()
        lost = False
        time.sleep(0.2)
        return _corsify_actual_response(jsonify({ "data": None, "status": "success" }))

@app.route('/api/flag')
def create_game(cell):
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    elif request.method == "GET":
        global flags
        if (cell in flags):
            flags.remove(cell)
        else:
            flags.add(cell)

        time.sleep(0.2)
        return _corsify_actual_response(jsonify({ "data": None, "status": "success" }))

@app.route('/api/play/ai')
def calculate_ai_move():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    elif request.method == "GET":
        global game
        global ai
        global flags

        move = ai.make_safe_move()
        if move is None:
            move = ai.make_random_move()
            if move is None:
                flags = ai.mines.copy()
                print("No moves left to make.")
            else:
                print("No known safe moves, AI making random move.")
        else:
            print("AI making safe move.")

        if (game.is_mine(move)):
            time.sleep(0.2)
            return _corsify_actual_response(jsonify({ "data": None, "status": "success" }))
        
        nearby = game.nearby_mines(move)
        revealed.add(move)
        ai.add_knowledge(move, nearby)
        time.sleep(0.2)

        # print("The optimal action for player: ", starting_player, " is: ", action)
        return _corsify_actual_response(jsonify({ "data": move, "status": "success" }))

@app.route('/api/play/user')
def calculate_user_move(cell):
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    elif request.method == "GET":
        if (cell not in flags and cell not in revealed):
            move = (i, j)
            return _corsify_actual_response(jsonify({ "data": move, "status": "success" }))
        
        return _corsify_actual_response(jsonify({ "data": None, "status": "success" }))


def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')