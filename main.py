from flask import Flask,  request, jsonify, make_response
from minesweeper import Minesweeper, MinesweeperAI
from flask_cors import CORS
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
        global lost
        global revealed
        global flags
        global HEIGHT
        global WIDTH

        lost = False
        revealed = set()
        flags = set()
        height = int(request.args.get("height"))
        width = int(request.args.get("width"))
        mines = eval(request.args.get("mines"))
        HEIGHT = height
        WIDTH = width

        game = Minesweeper(height, width, 0)
        ai = MinesweeperAI(height, width)

        for mine in mines:
            r, c = list(mine.split('-'))
            game.mines.add((int(r), int(c)))
            game.board[int(r)][int(c)] = True

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
        r, c = list(cell.split('-'))
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
        global lost
        
        def reveal_cell(cell):
            global lost

            if (cell in revealed or cell in flags):
                return
            
            if (game.is_mine(cell)):
                for i in range(game.height):
                    for j in range(game.width):
                        if (game.is_mine):
                            revealed.add((i, j))
                lost = True
                return
            
            def reveal_cells(r: int, c: int):
                if (r < 0 or r >= game.height or c < 0 or c >= game.width or (r, c) in revealed):
                    return
                
                revealed.add((r, c))
                ai.moves_made.add((r, c))
                if (game.nearby_mines((r, c)) == 0):
                    for i in [-1, 0, 1]:
                        for j in [-1, 0, 1]:
                            reveal_cells(r + i, c + j)

            reveal_cells(cell[0], cell[1])

        move_type = None
        move = ai.make_safe_move(game.mines)
        if move == None:
            move = ai.make_random_move(game.mines)
            if move == None:
                # The AI couldn't make a safe move nor a random move
                print("No moves left to make.")
                flags = ai.mines.copy()
            else:
                # The AI has made a random move
                print("Ai making random move: ", move)
                ai.add_knowledge(move, game.nearby_mines(move))
                reveal_cell(move)
                move_type = "random"
        else:
            # The AI has made a random move
            print("Ai making safe move: ", move)
            ai.add_knowledge(move, game.nearby_mines(move))
            reveal_cell(move)
            move_type = "safe"

        time.sleep(0.2)
        if (move_type == None):
            return _corsify_actual_response(jsonify({ "data": None, "status": "failed" }))
        
        print("These cells are revealed: ", list(revealed))
        return _corsify_actual_response(jsonify({ "data": list(revealed), "status": "success" }))


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
        adjacent_cells = ai.calculate_neighbors(move)
        for cell in adjacent_cells:
            nearby = game.nearby_mines(cell)
            if (nearby == 0 and cell not in revealed and cell not in ai.moves_made):
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