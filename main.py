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

# def revealCell(cell):
#     if (cell in revealed or cell in flags):
#         return
         
#     if (game.is_mine(cell)):
#         for row in game.board:
#             for c in row:
#                 if (game.is_mine(c)):
#                     revealed.add(c)
#         return

#     def revealCells(r, c):
#         if (r < 0 or r >= game.height or c < 0 or c >= game.width or (r, c) in revealed):
#             return

#         revealed.add((r, c))

#         if ()


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
def flag():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    elif request.method == "GET":
        global flags

        cell = request.args.get("cell")
        r, c = list(move.split('-'))
        flagged_cell = (int(r), int(c))

        if (flagged_cell in flags):
            flags.remove(flagged_cell)
        else:
            flags.add(flagged_cell)

        time.sleep(0.2)
        return _corsify_actual_response(jsonify({ "data": None, "status": "success" }))

# @app.route('/api/add-knowledge')
# def add_knowledge():
#     if request.method == "OPTIONS":
#         return _build_cors_preflight_response()
#     elif request.method == "GET":
#         cells = eval(request.args.get("cells"))
#         for cell in cells:
#             r, c = list(cell.split('-'))
#             cell = (int(r), int(c))
#             nearby = game.nearby_mines(cell)
#             revealed.add(cell)
#             ai.add_knowledge(cell, nearby)
#         return _corsify_actual_response(jsonify({ "data": "completed", "status": "success" }))

@app.route('/api/play/ai')
def calculate_ai_move():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    elif request.method == "GET":
        global game
        global ai
        global flags
        global revealed

        def process_move(move):
            if (game.is_mine(move)):
                time.sleep(0.2)
                return _corsify_actual_response(jsonify({ "data": None, "status": "failed" }))

            nearby = game.nearby_mines(move)
            revealed.add(move)
            ai.add_knowledge(move, nearby)

            print("Safe cells: ", ai.safes)

            for cell in ai.safes:
                if (cell not in revealed):
                    revealed.add(cell)

            time.sleep(0.2)
            # return _corsify_actual_response(jsonify({ "data": str(move[0]) + "-" + str(move[1]), "status": "success" }))
            return _corsify_actual_response(jsonify({ "data": list(revealed), "status": "success" }))

        move = ai.make_safe_move()
        if move:
            return process_move(move)

        move = ai.make_random_move()
        if move:
            return process_move(move)

        # The AI couldn't make a safe move nor a random move
        flags = ai.mines.copy()
        # print("No moves left to make.")
        time.sleep(0.2)
        return _corsify_actual_response(jsonify({ "data": None, "status": "failed" }))


@app.route('/api/play/user')
def calculate_user_move():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    elif request.method == "GET":
        move = request.args.get("move")
        r, c = list(move.split('-'))
        cell = (int(r), int(c))
        if (game.is_mine(cell)):
            time.sleep(0.2)
            return _corsify_actual_response(jsonify({ "data": None, "status": "failed" }))

        nearby = game.nearby_mines(cell)
        revealed.add(cell)
        ai.add_knowledge(cell, nearby)
        for cell in ai.safes:
            if (cell not in revealed):
                revealed.add(cell)
        time.sleep(0.2)
        return _corsify_actual_response(jsonify({ "data": list(revealed), "status": "success" }))

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