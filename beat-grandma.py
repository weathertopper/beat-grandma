import click
import shutil
import os
import string

config_dir = "config"
saved_games_dir="games"
tile_values_file_name="_wwf_tile_values.csv"
special_tiles_file_name="_wwf_special_tiles.csv"
possible_cols = "abcdefghijklmno"

def validateDirection(direction):
    if direction == "vertical" or direction == "v" or direction == "horizontal" or direction == "h":
        return True
    print("The direction {} is invalid. Valid directions are <vertical> <v> <horizontal> <h>".format(direction))
    return False

def validateWord(word):
    return isinstance(word, str) and len(word) > 0

def validateGame(game):
    game_file = getGameFilePath(game)
    if os.path.exists(game_file):
        return True
    print("The game file {} does not exist".format(game_file))
    return False

def validatePositionLength(position):
    return len(position) == 2 or len(position) == 3

def validatePositionRow(row):
    rowAsInt = -1
    try:
        rowAsInt = int(row)
        return 1 <= rowAsInt <= 15
    except:
        return False

def validatePositionCol(col):
    return col in possible_cols

def validatePosition(position):
    col = getPositionCol(position)
    row = getPositionRow(position)
    if row and col:
        return validatePositionCol(col) and validatePositionRow(row)
    return False

def getGameFilePath(game):
    return os.path.join(os.getcwd(), saved_games_dir, "{}.csv".format(game))

def getTemplateFilePath():
    return os.path.join(os.getcwd(), config_dir, "_template.csv")

def getTileValuesFilePath():
    return os.path.join(os.getcwd(), config_dir, tile_values_file_name)

def getSpecialTilesFilePath():
    return os.path.join(os.getcwd(), config_dir, special_tiles_file_name)

def getPositionRow(position): #i.e. the number
    if validatePositionLength(position):
        return position[1:]
    return False

def getPositionCol(position): #i.e. the letter
    if validatePositionLength(position):
        return position[0].lower()
    return False

def getPositionColIndex(position): #i.e. the index of the letter
    return possible_cols.find(getPositionCol(position))

def buildPosition(col, row): # assumes col and row are valid
    return col + str(row)

def directionIsHorizontal(direction): # otherwise it's vertical
    return direction == "horizontal" or direction == "h"

def positionMoveUp(position): # returns next position if valid, else False (assumes position is valid) 
    up_row = int(getPositionRow(position))-1
    if validatePositionRow(up_row):
        return buildPosition(getPositionCol(position), up_row)
    return False

def positionMoveDown(position): # returns next position if valid, else False (assumes position is valid)
    down_row = int(getPositionRow(position))+1
    if validatePositionRow(down_row):
        return buildPosition(getPositionCol(position), down_row)
    return False

def positionMoveLeft(position): # returns next position if valid, else False (assumes position is valid)
    prev_col_index = getPositionColIndex(position) - 1
    if prev_col_index > -1:
        left_col = possible_cols[prev_col_index]
        return buildPosition(left_col, getPositionRow(position))
    return False

def positionMoveRight(position): # returns next position if valid, else False (assumes position is valid)
    next_col_index = getPositionColIndex(position) + 1
    if next_col_index < len(possible_cols):    
        right_col = possible_cols[next_col_index]
        return buildPosition(right_col, getPositionRow(position))
    return False

def testInput(command, game, letters, position, word, direction):
    print(" command: {}\n game: {}\n letters: {}\n position: {}\n word: {}\n direction: {}".format(command, game, letters, position, word, direction))
    board = readFullBoard(game)
    print(getLetterOnBoardAtPosition(board, position))

def createGame(game):
    template_file = getTemplateFilePath()
    copy_file = getGameFilePath(game)
    shutil.copyfile(template_file, copy_file)

def deleteGame(game):
    if validateGame(game):
        game_file = getGameFilePath(game)
        os.remove(game_file)

def readEmptyBoard():
    board=[]
    f = open(getTemplateFilePath(), "r")
    board_as_string = f.read()
    board_by_row = board_as_string.split("\n")
    for r in board_by_row:
        board.append(r.split(","))
    return board

def readFullBoard(game):
    if validateGame(game):
        board=[]
        f = open(getGameFilePath(game), "r")
        board_as_string = f.read()
        board_by_row = board_as_string.split("\n")
        for r in board_by_row:
            board.append(r.split(","))
        return board
    return ""

def readTileValuesAsDict():
    tile_values = dict()
    f = open(getTileValuesFilePath(), "r")
    tile_values_as_string = f.read()
    tile_values_by_row = tile_values_as_string.split("\n")
    for r in tile_values_by_row:
        tile_val = r.split(",")
        tile_values[tile_val[0]] = tile_val[1]
    return tile_values

def specialStringToCharacter(special_string):
    special_characters = { 
        "tw": "T",
        "tl" : "t",
        "dw" : "D",
        "dl" : "d",
        "st" : "S"
    }
    return special_characters[special_string]

def readSpecialTilesAsDict():
    special_tiles = dict()
    f = open(getSpecialTilesFilePath(), "r")
    special_tiles_as_string = f.read()
    special_tiles_by_row = special_tiles_as_string.split("\n")
    for r in special_tiles_by_row:
        position_special = r.split(",")
        position = position_special[0]
        special_char = specialStringToCharacter(position_special[1])
        special_tiles[position] = special_char
    return special_tiles

def boardToPrettyString(board):
    # script kiddie!
    # https://stackoverflow.com/a/13214945
    s = [[str(e) for e in row] for row in board]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in s]
    return '\n'.join(table)

def setLetterOnBoardAtPosition(letter, board, position):
    row_index = int(getPositionRow(position))-1 # row starts at 1, index starts at 0
    col_index = getPositionColIndex(position)
    board[row_index][col_index] = letter
    return board

def getLetterOnBoardAtPosition(board, position): # assumes position valid
    row_index = int(getPositionRow(position))-1 # row starts at 1, index starts at 0
    col_index = getPositionColIndex(position)
    return board[row_index][col_index]

def setWord(game, position, word, direction):
    game_valid = validateGame(game)
    direction_valid = validateDirection(direction)
    position_valid = validatePosition(position)
    word_valid = validateWord(word)
    if not (game_valid and direction_valid and position_valid and word_valid):
        return False
    board = readFullBoard(game)
    curr_pos = position
    for i in range(len(word)):
        board = setLetterOnBoardAtPosition(word[i], board, curr_pos)
        if i != len(word)-1: # don't do math for next position if last letter set
            next_pos = positionMoveRight(curr_pos) if directionIsHorizontal(direction) else positionMoveDown(curr_pos)
            if not (next_pos and validatePosition(next_pos)):
                 print(" ERROR: Failed to set word {} at position {} in direction {} for game {}\n".format(word, position, direction, game))
                 return False
            curr_pos = next_pos
    writeBoardToFile(game, board)
    print(" Set word {} at position {} in direction {} for game {}\n".format(word, position, direction, game))

def writeBoardToFile(game, board):
    board_as_string = ""
    for row in board:
        board_as_string += ",".join(row)
        board_as_string += "\n"
    board_as_string = board_as_string.rstrip()
    f = open(getGameFilePath(game), "w")
    f.write(board_as_string)
    f.close()

def printBoard(board):
    header_row = list(string.ascii_lowercase)[:15]
    header_row.insert(0, "")
    for i in range(len(board)):
        board[i].insert(0, i+1)
    board.insert(0, header_row)
    print(boardToPrettyString(board))

def printGame(game):
    board = readFullBoard(game)
    if board == "":
        return
    printBoard(board)

def printSpecialTiles(): 
    board = readEmptyBoard();
    special_tiles = readSpecialTilesAsDict()
    for pos, char in special_tiles.items():
        setLetterOnBoardAtPosition(char, board, pos)
    printBoard(board)
    

def printTileValues(): #TODO
    tile_values_dict = readTileValuesAsDict()
    print ("TILE VALUES")
    for t, v in tile_values_dict.items():
        print(t + " : " + v)

def bestMove(game, letters): #TODO
    print(" BEST MOVE \n game: {}\n letters: {}".format(game, letters))
    best_word=""
    best_word_position=""
    best_word_score=0

    print("Best word: " + best_word)
    print("Position: " + best_word_position)
    print("Score: " + str(best_word_score))

# CLI INPUTS
@click.command()
@click.argument('command')
@click.option('--game', '-g')
@click.option('--letters', '-l')
@click.option('--position', '-p')
@click.option('--word', '-w')
@click.option('--direction', '-d')

# DRIVER
def main(command, game, letters, position, word, direction):
    if command == "test":
        testInput(command, game, letters, position, word, direction)
    elif command == "new-game":
        createGame(game)
    elif command == "delete-game": 
        deleteGame(game)
    elif command == "print-game":
        printGame(game)
    elif command == "set-word":
        setWord(game, position, word, direction)
    elif command == "print-special-tiles":
        printSpecialTiles()
    elif command == "print-tile-values":
        printTileValues()
    elif command == "best-move":
        bestMove(game, letters)
    else:
        print("default")

if __name__ == "__main__":
    main()