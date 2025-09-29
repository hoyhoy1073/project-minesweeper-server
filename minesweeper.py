import itertools
import heapq
import random
import math
import queue
import copy

class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count
        self.mines = set()
        self.safes = set()

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if (self.count == len(self.cells)):
            return self.cells

        return self.mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if (self.count == 0):
            return self.cells

        return self.safes

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if (cell in self.cells):
            self.mines.add(cell)
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if (cell in self.cells):
            self.safes.add(cell)
            self.cells.remove(cell)

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        if (cell in self.mines or cell in self.safes):
            return

        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell) 

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        if (cell in self.safes or cell in self.mines):
            return

        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell) 

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        def handleBaseCases(sentence: Sentence):
            cells, count = sentence.cells, sentence.count

            if (len(cells) == 0):
                return
            # Bases case 1: If the length of cells is 1, then the cell's state is known.
            # We push them onto the queue to update other cells.
            if (len(cells) == 1):
                if (count == 0):
                    self.mark_safe(list(cells)[0])
                elif (count == 1):
                    self.mark_mine(list(cells)[0])
                q.put((list(cells)[0], count))
            # Base case 2: If the count for the new sentence is 0, then all of its neighbor are known safe cells.
            # We push them onto the queue to update other cells.
            elif (count == 0):
                for cell in cells:
                    self.mark_safe(cell)
                    q.put((cell, 0))
            # Base case 3: If the count for the new sentence is equal to the number of cells in the sentence,
            # then all cells in the sentence are mines.
            # We push them onto the queue to update other cells.
            elif (len(cells) == count):
                for cell in cells:
                    self.mark_mine(cell)
                    q.put((cell, 1))
            else:
                self.knowledge.append(sentence)   

        q = queue.Queue()
        processed = set()
        knowledge = self.knowledge.copy()

        # Create a sentence based with the cell's neighbors
        neighbors = self.calculate_neighbors(cell)
        sentence_A = self.create_sentence(neighbors, count)
        handleBaseCases(sentence_A)
        # This cell was clicked on and the game did not end, so it's a known safe cell
        # and we add it to the queue to update other cells.
        q.put((cell, 0))

        # Infer new shorter sentences that is a subset of the new sentence
        for sentence_B in knowledge:
            if sentence_B.cells.issubset(sentence_A.cells):
                cells_C = sentence_A.cells - sentence_B.cells
                count_C = sentence_A.count - sentence_B.count
                sentence_C = self.create_sentence(cells_C, count_C)
                handleBaseCases(sentence_C)
            elif sentence_A.cells.issubset(sentence_B.cells):
                cells_C = sentence_B.cells - sentence_A.cells
                count_C = sentence_B.count - sentence_A.count
                sentence_C = self.create_sentence(cells_C, count_C)
                handleBaseCases(sentence_C)

        # Use the list of cells that we know the state of to update the AI's knowledge
        new_knowledge = []
        if (not q.empty()):
            knowledge_set = set()
            while (not q.empty()):
                cur, count = q.get()
                if (str((cur, count)) not in processed):
                    processed.add(str((cur, count)))
                    for sentence in self.knowledge:
                        if (cur in sentence.cells):
                            if (count == 1):
                                sentence.mark_mine(cur)
                            elif (count == 0):
                                sentence.mark_safe(cur)
                        
                        cells = copy.deepcopy(sentence.cells)
                        if (sentence.count >= len(cells)):
                            for c in cells:
                                self.mark_mine(c)
                                # Since we are retiring the sentence due to all cells' state being known
                                # We don't need to add each cell to the sentence's known mines set
                                q.put((c, 1))
                        elif (sentence.count == 0 and len(cells) > 0):
                            for c in cells:
                                self.mark_safe(c)
                                # Since we are retiring the sentence due to all cells' state being known
                                # We don't need to add each cell to the sentence's known safe set
                                q.put((c, 0))
                        elif (len(cells) > 0):
                            knowledge_set.add((repr(cells), sentence.count))

            # Rebuilding the Ai's knowledge
            for cell_strs, count in knowledge_set:
                new_knowledge.append(Sentence(eval(cell_strs), count))

            self.knowledge = new_knowledge

        sentence_A.mark_safe(cell)
        self.mark_safe(cell)
        self.moves_made.add(cell)

    def calculate_neighbors(self, cell):
        neighbors = []
        i, j = cell
        for k in [-1, 0, 1]:
            if (i + k <= self.height - 1 and i + k >= 0):
                for l in [-1, 0, 1]:
                    # We need to include the clicked cell to inference knowledge about other sentences
                    # via the subset operation
                    # if (k == 0 and l == 0):
                    #     continue
                    if (j + l <= self.width - 1 and j + l >= 0):
                        neighbors.append((i + k, j + l))

        return neighbors

    # Create a new sentence with the cell's neighbors, and how many of them are mines
    def create_sentence(self, cells, count):
        newCells = set()
        for cell in cells:
            if (cell in self.mines or cell in self.safes):
                if (cell in self.mines):
                    count -= 1
            else:
                newCells.add(cell)

        return Sentence(newCells, count)

    def make_safe_move(self, mines):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        available_moves = []
        for safe_move in self.safes:
            if (safe_move not in self.moves_made):
                available_moves.append(safe_move)
        
        if (len(available_moves) > 0):
            random_move = random.sample(available_moves, 1)
            if (len(random_move) > 0):
                return random_move[0]
        
        return None
     
    def make_random_move(self, mines):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        Return a cell with the largest Manhattan distance from cells that are known mines and are already clicked on
        """
        def calculate_manhattan_distances():
            distances = []
            heapq.heapify(distances)
            centroids = mines.union(self.mines).union(self.moves_made)
            for i in range(self.height):
                for j in range(self.width):
                    if ((i, j) not in mines and (i, j) not in self.mines and (i, j) not in self.moves_made):
                        for source in centroids:
                            distance = abs(i - source[0]) + abs(j - source[1])
                            heapq.heappush(distances, ((-1) * distance, (i, j)))

            return distances

        distances = calculate_manhattan_distances()
        if (len(distances) > 0):
            move = heapq.heappop(distances)[1]
            self.moves_made.add(move)
            return move
        
        available_moves = []
        for i in range(self.height):
            for j in range(self.width):
                move = (i, j)
                if (move not in self.moves_made and move not in self.mines):
                    available_moves.append(move)

        random_move = random.sample(available_moves, 1)
        if (len(random_move) > 0):
            move = random_move[0]
            self.moves_made.add(move)
            return move
        
        return None