from flask import Flask,  request, jsonify, make_response
from flask_cors import CORS
from minesweeper import Minesweeper, MinesweeperAI
import json
import time

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

HEIGHT = None
WIDTH = None
MINE_COUNT = None
game = None
ai = None
lost = False
revealed = set()
flags = set()

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
        HEIGHT = height
        WIDTH = width
        MINE_COUNT = len(mines)

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
def create_game():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    elif request.method == "GET":
        global flags

        move = request.args.get("move")
        r, c = list(move.split('-'))
        cell = (int(r), int(c))

        if (cell in flags):
            flags.remove(cell)
        else:
            flags.add(cell)

        time.sleep(0.2)
        return _corsify_actual_response(jsonify({ "data": "completed", "status": "success" }))

@app.route('/api/play/ai')
def calculate_ai_move():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    elif request.method == "GET":
        global game
        global ai
        global flags
        global revealed

        move = ai.make_safe_move()
        if move:
            time.sleep(0.2)
            if (game.is_mine(move)):
                return _corsify_actual_response(jsonify({ "data": "lost", "status": "success" }))

            nearby = game.nearby_mines(move)
            revealed.add(move)
            ai.add_knowledge(move, nearby)
            return _corsify_actual_response(jsonify({ "data": "completed", "status": "success" }))

        move = ai.make_random_move()
        if move:
            time.sleep(0.2)
            if (game.is_mine(move)):
                return _corsify_actual_response(jsonify({ "data": "lost", "status": "success" }))

            nearby = game.nearby_mines(move)
            revealed.add(move)
            ai.add_knowledge(move, nearby)
            return _corsify_actual_response(jsonify({ "data": "completed", "status": "success" }))

        flags = ai.mines.copy()
        print("No moves left to make.")
        return _corsify_actual_response(jsonify({ "data": "not completed", "status": "success" }))


@app.route('/api/play/user')
def calculate_user_move():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    elif request.method == "GET":
        cells = eval(request.args.get("cells"))
        adjacent_mines_array = eval(request.args.get("adjacentMines"))

        print("Cells: ", cells)
        print("Adjacent mines: ", adjacent_mines_array)

        for i in range(len(cells)):
            cell = cells[i]
            adjacent_mines = adjacent_mines_array[i]

            if (cell not in flags and cell not in revealed):
                r, c = list(cell.split('-'))
                if (game.is_mine((int(r), int(c)))):
                    time.sleep(0.2)
                    return _corsify_actual_response(jsonify({ "data": "lost", "status": "success" }))

                ai.add_knowledge((int(r), int(c)), adjacent_mines)
                return _corsify_actual_response(jsonify({ "data": "completed", "status": "success" }))

            return _corsify_actual_response(jsonify({ "data": "not completed", "status": "success" }))

            # r, c = list(move.split('-'))
            # cell = (int(r), int(c))
            # if (game.is_mine(cell)):
            #     time.sleep(0.2)
            #     return _corsify_actual_response(jsonify({ "data": "lost", "status": "success" }))

            # ai.add_knowledge(cell, count)
            # return _corsify_actual_response(jsonify({ "data": "completed", "status": "success" }))
        
        return _corsify_actual_response(jsonify({ "data": "not completed", "status": "success" }))


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