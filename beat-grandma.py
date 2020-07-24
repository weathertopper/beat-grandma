import click
import shutil
import os
import string

saved_games_dir="games"
possibleCols = "abcdefghijklmno"

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
    return col in possibleCols

def validatePosition(position):
    col = getPositionCol(position)
    row = getPositionRow(position)
    if row and col:
        return validatePositionCol(col) and validatePositionRow(row)
    return False

def getGameFilePath(game):
    return os.path.join(os.getcwd(), saved_games_dir, "{}.csv".format(game))

def getTemplateFilePath():
    return os.path.join(os.getcwd(), saved_games_dir, "_template.csv")
    
def getPositionRow(position): #i.e. the number
    if validatePositionLength(position):
        return position[1:]
    return False

def getPositionCol(position): #i.e. the letter
    if validatePositionLength(position):
        return position[0]
    return False

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
    prev_col_index = possibleCols.find(col) - 1
    if prev_col_index > -1:
        left_col = possibleCols[prev_col_index]
        return buildPosition(left_col, getPositionRow(position))
    return False

def positionMoveRight(position): # returns next position if valid, else False (assumes position is valid)
    next_col_index = possibleCols.find(getPositionCol(position)) + 1
    if next_col_index < len(possibleCols):    
        right_col = possibleCols[next_col_index]
        return buildPosition(right_col, getPositionRow(position))
    return False

def testInput(command, game, letters, position, word, direction):
    print(" command: {}\n game: {}\n letters: {}\n position: {}\n word: {}\n direction: {}".format(command, game, letters, position, word, direction))

def createGame(game):
    template_file = getTemplateFilePath()
    copy_file = getGameFilePath(game)
    shutil.copyfile(template_file, copy_file)

def deleteGame(game):
    if validateGame(game):
        game_file = getGameFilePath(game)
        os.remove(game_file)

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

def boardToPrettyString(board):
    # script kiddie!
    # https://stackoverflow.com/a/13214945
    s = [[str(e) for e in row] for row in board]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in s]
    return '\n'.join(table)

def printGame(game):
    board = readFullBoard(game)
    if board == "":
        return
    header_row = list(string.ascii_lowercase)[:15]
    header_row.insert(0, "")
    for i in range(len(board)):
        board[i].insert(0, i+1)
    board.insert(0, header_row)
    print(boardToPrettyString(board))

def setLetterOnBoardAtPosition(letter, board, position):
    row_index = int(getPositionRow(position))-1 # row starts at 1, index starts at 0
    col_index = possibleCols.find(getPositionCol(position))
    board[row_index][col_index] = letter
    return board

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

def printSpecials(): #TODO
    print(" PRINT SPECIALS \n")

def bestMove(game, letters, position): #TODO
    print(" BEST MOVE \n game: {}\n letters: {}\n position: {}".format(game, letters, position))


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
    elif command == "print-specials":
        printSpecials()
    elif command == "best-move":
        bestMove(game, letters)
    else:
        print ("default")

if __name__ == "__main__":
    main()