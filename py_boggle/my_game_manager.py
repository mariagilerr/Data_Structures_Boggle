import copy
import random
from typing import List, Optional, Set, Tuple

from py_boggle.boggle_dictionary import BoggleDictionary
from py_boggle.boggle_game import BoggleGame

"""
************** READ THIS ***************
************** READ THIS ***************
************** READ THIS ***************
************** READ THIS ***************
************** READ THIS ***************

If you worked in a group on this project, please type the EIDs of your groupmates below (do not include yourself).
Leave it as TODO otherwise.
Groupmate 1: TODO
Groupmate 2: TODO
"""

SHORT = 3
CUBE_SIDES = 6

class MyGameManager(BoggleGame):
    """Your implementation of `BoggleGame`
    """

    def __init__(self):
        """Constructs an empty Boggle Game.

        A newly-constructed game is unplayable.
        The `new_game` method will be called to initialize a playable game.
        Do not call `new_game` here.

        This method is provided for you, but feel free to change it.
        """

        self.board: List[List[str]] # current game board
        self.size: int # board size
        self.words: List[str] # player's current words
        self.dictionary: BoggleDictionary # the dictionary to use
        self.last_added_word: Optional[List[Tuple[int, int]]] # the position of the last added word, or None

    def new_game(self, size: int, cubefile: str, dictionary: BoggleDictionary) -> None:
        """This method is provided for you, but feel free to change it.
        """
        with open(cubefile, 'r') as infile:
            faces = [line.strip() for line in infile]
        cubes = [f.lower() for f in faces if len(f) == CUBE_SIDES]
        if size < 2 or len(cubes) < size*size:
            raise ValueError('ERROR: Invalid Dimensions (size, cubes)')
        random.shuffle(cubes)
        # Set all of the game parameters
        self.board =[[random.choice(cubes[r*size + c]) 
                    for r in range(size)] for c in range(size)]
        self.size = size
        self.words = []
        self.dictionary = dictionary
        self.last_added_word = None


    def get_board(self) -> List[List[str]]:
        """This method is provided for you, but feel free to change it.
        """
        return self.board

    def find_word_in_board(self, word: str) -> Optional[List[Tuple[int, int]]]:
        """Helper method called by add_word()
        Expected behavior:
        Returns an ordered list of coordinates of a word on the board in the same format as get_last_added_word()
        (see documentation in boggle_game.py).
        If `word` is not present on the board, return None.
        """
        word = word.lower()
        for r in range(len(self.board)):
            for c in range(len(self.board[0])): #checked each row and column index
                if self.board[r][c] == word[0]:
                    result = self.helper(word, 1, r, c, [(r,c)]) #if cell matches first letter of word, will start looking for next letter
                    if result is not None:
                        return result
        return None

    def helper(self,word, i, r, c, path):
        n=len(self.board)
        if i==len(word): #once all letters in word have been found
            return path
        for dr in (-1,0,1):
            for dc in (-1,0,1):
                if dr==0 and dc==0:#current cell
                    continue
                nr,nc = r+dr,c+dc #next cell
                if (0 <= nr < n and 0 <= nc < n and (nr, nc) not in path and self.board[nr][nc] == word[i]): #check cell exists, isn't used, and is needed
                    path.append((nr, nc))
                    result = self.helper(word, i + 1, nr, nc, path) #look for next letter
                    if result is not None:
                        return result
                    path.pop()
        return None

    def add_word(self, word: str) -> int:
        """This method is provided for you, but feel free to change it.
        """
        word = word.lower()
        if (len(word) > SHORT and word not in self.words and self.dictionary.contains(word)):
            location = self.find_word_in_board(word)
            if location is not None:
                self.last_added_word = location
                self.words.append(word)
                return len(word) - SHORT
        return 0

    def get_last_added_word(self) -> Optional[List[Tuple[int, int]]]:
        """This method is provided for you, but feel free to change it.
        """
        return self.last_added_word

    def set_game(self, board: List[List[str]]) -> None:
        """This method is provided for you, but feel free to change it.
        """
        self.board = [[c.lower() for c in row] for row in board]
        self.size = len(self.board)
        self.last_added_word = None
        self.words = []

    def get_score(self) -> int:
        """This method is provided for you, but feel free to change it.
        """
        return sum([len(word) - SHORT for word in self.words])

    def dictionary_driven_search(self) -> Set[str]:
        """Find all words using a dictionary-driven search.

        The dictionary-driven search attempts to find every word in the
        dictionary on the board.

        Returns:
            A set containing all words found on the board.
        """
        found = set()
        letters = {ch for row in self.board for ch in row}
        for word in self.dictionary:
            if len(word) <= SHORT:
                continue
            if not set(word) <= letters:
                continue
            if self.find_word_in_board(word) is not None:
                found.add(word)
        return found


    def board_driven_search(self) -> Set[str]:
        """Find all words using a board-driven search.

        The board-driven search constructs a string using every path on
        the board and checks whether each string is a valid word in the
        dictionary.

        Returns:
            A set containing all words found on the board.
        """
        found = set()
        for r in range(len(self.board)):
            for c in range(len(self.board)):
                self.board_helper(r, c, self.board[r][c], {(r, c)}, found)
        return found

    def board_helper(self, r, c, current, visited, found):
        n = len(self.board)
        if not self.dictionary.is_prefix(current):
            return
        if len(current) > SHORT and self.dictionary.contains(current):
            found.add(current)
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:  # current cell
                    continue
                nr, nc = r + dr, c + dc  # next cell
                if (0 <= nr < n and 0 <= nc < n and (nr, nc) not in visited):
                    visited.add((nr, nc))
                    self.board_helper(nr, nc, current + self.board[nr][nc], visited, found)
                    visited.remove((nr, nc))