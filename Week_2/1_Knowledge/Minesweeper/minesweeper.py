import itertools
import random


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

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # If len(set) == count, then all cells must be mines
        # And self.count > 0
        if len(self.cells) == self.count and self.count > 0:
            return set(self.cells)
        else:
            # Otherwise return blank set
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # If count == 0, then all cells in sentence must be safe
        if self.count == 0 and len(self.cells) > 0:
            # Thus return all cells
            return set(self.cells)
        else:
            # Otherwise return blank set
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # Check that cell is in the sentence
        if cell in self.cells:
            # If yes then update the sentence to remove the cell
            self.cells.remove(cell)
            # Also drop count of mines in sentence by 1, to reflect removal of mine
            self.count -= 1
        # Otherwise do nothing
        if cell not in self.cells:
            pass

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # Check if cell is in sentence
        if cell in self.cells:
             # If yes, then update sentence to remove cell
             self.cells.remove(cell)
            # Otherwise do nothing
        if cell not in self.cells:
            pass


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
        # Add the cell to the list of known mines
        self.mines.add(cell)
        # Iterate through each sentence
        for sentence in self.knowledge:
            # For each setence mark this mine (thus removing it from sentence)
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        # Add the cell to the list of known safes
        self.safes.add(cell)
        # Iterate through each sentence
        for sentence in self.knowledge:
            # For each sentence mark this mine as safe (thus removing it from sentence)
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
        # 1) Mark cell as move that has been made
        self.moves_made.add(cell)

        # 2) Mark cell as a safe cell
        self.mark_safe(cell)

        # 3)
        # Establish coordinates of cell
        i0 = cell[0]
        j0 = cell[1]

        # Establish coordinates of all surrounding cells
        i_surrounding = [i0 - 1, i0, i0 + 1]
        j_surrounding = [j0 - 1, j0, j0 + 1]

        # Create list of all surrounding cells
        surrounding_cells = set()
        # Iterate through the cells (first through row then col)
        for ii in i_surrounding:
            for jj in j_surrounding:
                # Skip the cell itself
                if (ii, jj) == (i0, j0):
                    continue
                # If the location of the cell is within the bounds of the board
                if 0 <= ii < self.height and 0 <= jj < self.width:
                    # Then add the cell to a list of possible surrounding cells
                    surrounding_cells.add((ii, jj))

        # Create a set to place all uncategorised cells
        unknown_cells = set()
        # Create a proxy for count of cell (number of mines in vecinity)
        adjusted_count = count
        # Iterate through each cell in the surrounding cells
        for c in surrounding_cells:
            if c not in self.moves_made and c not in self.mines and c not in self.safes:
                unknown_cells.add(c)
            elif c in self.mines:
                adjusted_count -= 1

        # Only add a sentence if there are unknown cells remaining
        if unknown_cells:
            # Create logic sentence of remaining unknown cells and the (adjusted) count
            sentence = Sentence(cells = unknown_cells, count = adjusted_count)
            # Add logic sentence to knowledge base
            self.knowledge.append(sentence)

        # From the added safe cell, are any sentences now different
        # Initialise a while loop
        updated = True
        while updated:
            updated = False
            # Iterate through each sentence in the knowledge base
            for sentence in self.knowledge[:]:
                # Check through the sentence and test for known mines
                for mine in sentence.known_mines():
                    # If the known mine is not already in the list of known mines then:
                    if mine not in self.mines:
                        # Add to the list of known mines
                        self.mark_mine(mine)
                        # Restart while loop
                        updated = True
                # Check through the sentence and test for safes
                for safe in sentence.known_safes():
                    # If the safe is not yet known then:
                    if safe not in self.safes:
                        # Add to the list of known safes
                        self.mark_safe(safe)
                        # Restart while loop as new change added
                        updated = True

                # If the sentence contains no data (no cells or count) then remove from knowledge base
                if len(sentence.cells) == 0:
                    if sentence.count == 0:
                        # If no count then remove sentence from knowledge base
                        self.knowledge.remove(sentence)
                        # Restart while loop as there has been an update
                        updated = True
                    else:
                        # Otherwise raise a value error, since the sentence was not logically sound
                        raise ValueError ("Inconsistent sentence: no cells but a nonzero count")
                    continue

                # All cells must be mines if number of cells == count
                if len(sentence.cells) == sentence.count:
                    # Mark all cells in sentence as mines
                    for cell in set(sentence.cells):
                        # Use self. because then global state is updated
                        self.mark_mine(cell)
                    # Restart while loop as there has been an update
                    updated = True
                    continue

                # If the count of the cells is 0, then all cells are safe
                if sentence.count == 0:
                    # Mark all cells as safe
                    for cell in set(sentence.cells):
                        # Use self. because then global state is updated
                        self.mark_safe(cell)
                    # Restart while loop as there has been an update
                    updated = True
                    continue

            # Find if another sentence is a subset of current sentence
            new_knowledge = []
            # Iterate through sentences in the knowledge base
            for sentence in self.knowledge:
                # Iterate through other sentences in knowledge base
                for comparative_sentence in self.knowledge:
                    # If the cells of the comparative sentence are a subset of the sentence cells then:
                    if comparative_sentence.cells < sentence.cells:
                        # Find the difference in cells
                        cell_difference = sentence.cells - comparative_sentence.cells
                        # Find the differences in count
                        count_difference = sentence.count - comparative_sentence.count

                        # Create new sentence from combination of the two
                        new_sentence = Sentence(cells = cell_difference, count = count_difference)
                        # Check that it will not be a duplicate
                        if new_sentence not in self.knowledge and new_sentence not in new_knowledge:
                            # Add the sentence to the new_knowledge
                            new_knowledge.append(new_sentence)
                            # Restart while loop
                            updated = True

            # Add new sentences to knowledge base
            self.knowledge.extend(new_knowledge)


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # Return a safe move, that has not been made yet
        # Compare the lists of safe moves with moves made, remove duplicates
        safe_moves = list(self.safes - self.moves_made)
        # If no items in safe_moves variable then return none
        if not safe_moves:
            return None
        # Otherwise return a random choice of the possible safe moves
        return random.choice(safe_moves)

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # Establish known dimensions of the board
        rows = self.height
        cols = self.width
        # Create empty list for possible moves
        possible_moves = []
        # Iterate over the rows
        for i in range(rows):
            # Iterate over the columns in row
            for j in range(cols):
                # Move is the current cell
                move = (i, j)
                # If the move is already done, or in the list of known mines then skip to next cell
                if move in self.moves_made or move in self.mines:
                    continue
                # Otherwise add the cell to a list of potential moves that can be made
                else:
                    possible_moves.append(move)

        # If there are no possible moves then return None
        if not possible_moves:
            return None
        # Otherwise return a random selection of a move from the list
        return random.choice(possible_moves)

