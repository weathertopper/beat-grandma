import click
import shutil
import os
import string
import time

dictionary_dir="dictionary"
enable_word_list_file="enable1.txt"
wwf2_added_word_list_file="wwf2_added.txt"
wwf2_removed_word_list_file="wwf2_removed.txt"
config_dir = "config"
tile_values_file_name="_wwf_tile_values.csv"
special_tiles_file_name="_wwf_special_tiles.csv"
saved_games_dir="games"
possible_cols = "abcdefghijklmno"
row_length = 15

def validateDirection(direction):
    if direction == "vertical" or direction == "v" or direction == "horizontal" or direction == "h":
        return True
    print("The direction {} is invalid. Valid directions are <vertical> <v> <horizontal> <h>".format(direction))
    return False

def validateWord(word):
    return len(word) > 0

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
        return 1 <= rowAsInt <= row_length
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

def getEnableWordFilePath():
    return os.path.join(os.getcwd(), dictionary_dir, enable_word_list_file)

def getWWF2AddedWordFilePath():
    return os.path.join(os.getcwd(), dictionary_dir, wwf2_added_word_list_file)

def getWWF2RemovedWordFilePath():
    return os.path.join(os.getcwd(), dictionary_dir, wwf2_removed_word_list_file)

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

def setWordOnBoard(board, position, word, direction):
    curr_pos = position
    for i in range(len(word)):
        board = setLetterOnBoardAtPosition(word[i], board, curr_pos)
        if i != len(word)-1: # don't do math for next position if last letter set
            next_pos = positionMoveRight(curr_pos) if directionIsHorizontal(direction) else positionMoveDown(curr_pos)
            if not (next_pos and validatePosition(next_pos)):
                 print(" ERROR: Failed to set word {} at position {} in direction {} for game {}\n".format(word, position, direction, game))
                 return False
            curr_pos = next_pos
    return board


def setWord(game, position, word, direction):
    game_valid = validateGame(game)
    direction_valid = validateDirection(direction)
    position_valid = validatePosition(position)
    word_valid = validateWord(word)
    if not (game_valid and direction_valid and position_valid and word_valid):
        print(" ERROR: Something not valid. Game Valid: {}; Direction Valid: {}; Position Valid: {}; Word Valid: {}".format(game_valid, direction_valid, position_valid, word_valid))
        return False
    board = setWordOnBoard(readFullBoard(game), position, word, direction)
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
    

def printTileValues():
    tile_values_dict = readTileValuesAsDict()
    print ("TILE VALUES")
    for t, v in tile_values_dict.items():
        print(t + " : " + v)

def getListOfAllPositions(): 
    all_positions = []
    for char in possible_cols:
        for i in range(row_length):
            all_positions.insert(len(all_positions), buildPosition(char, i+1))
    return all_positions


def buildWordList():
    enable_word_list = list(map(str.rstrip, open(getEnableWordFilePath(), "r").read().split("\n")))
    added_word_list = list(map(str.rstrip, open(getWWF2AddedWordFilePath(), "r").read().split("\n")))
    removed_word_list = list(map(str.rstrip, open(getWWF2RemovedWordFilePath(), "r").read().split("\n")))
    full_list = enable_word_list + added_word_list
    for r in removed_word_list:
        full_list.remove(r)
    return full_list

# Returns True if:
# Word fits on board at position
def wordFits(board, letters, position, direction, word): #TODO
    return False

# Returns True if:
# Word can be played with letters on board AND at least one letter from hand
def lettersPlayable(board, letters, position, direction, word): #TODO
    return False

# Returns True if:
# Word connected to other words on board
def wordConnected(board, letters, position, direction, word): #TODO
    return False

# Returns points for given move
# need to know which letters from hand played in which positions
def calculatePoints(): #TODO
    return 0



# Returns True if:
# All words on board exist in dictionary list
def validateAllWordsOnBoard(board):
    words_on_board = getWordsOnBoard(board)
    dictionary = buildWordList();
    for word in words_on_board:
        if word not in dictionary:
            print ("ERROR: Word {} not valid.".format(word))
            return False
    return True


def getWordsOnBoard(board):
    word_candidates= []
    for row in board:
        word = ""
        for i in range(len(possible_cols)):
            col = i + 1
            c = row[i]
            if c == "" or col == len(possible_cols):
                if c != "":
                    word += c
                if word != "":
                    word_candidates.append(word)
                    word = ""
            else:
                word += c

    for col in possible_cols:
        word = ""
        for i in range(row_length):
            row = i + 1
            pos = buildPosition(col, row)
            c = getLetterOnBoardAtPosition(board, pos)
            if c == "" or row == row_length :
                if c != "":
                    word += c
                if word != "":
                    word_candidates.append(word)
                    word = ""
            else:
                word += c

    words = []
    for word in word_candidates:
        if len(word) > 1:
            words.append(word)
    return words

def bestMove(game, letters): #TODO
    print(" BEST MOVE \n game: {}\n letters: {}".format(game, letters))
    validateAllWordsOnBoard(readFullBoard(game))
    time_start = time.time()

    best_word=""
    best_word_position=""
    best_word_direction=""
    best_word_score=0
   
    all_positions = getListOfAllPositions()
    all_directions =  ["horizontal", "vertical"]
    word_list =  buildWordList()

    count = 0 # Can remove after TODO

    clean_board = readFullBoard(game)
    
    for p in all_positions:
        for d in all_directions:
            for w in word_list:
                if wordFits(clean_board, letters, p, d, w) and \
                   lettersPlayable(clean_board, letters, p, d, w) and \
                   wordConnected(clean_board, letters, p, d, w):
                    dirty_board = setWordOnBoard(readFullBoard(game), p, w, d)
                    if validateAllWordsOnBoard(dirty_board):
                        score = calculatePoints()
                        print("Word {} at position {} in direction {} would score {} points".format(w, p, d, str(score)))
                        if score > best_word_score or \
                            score == best_word_score and len(w) > len(best_word):
                            best_word_score = score
                            best_word = w
                            best_word_position = p
                            best_word_direction = d
                            print ("Word {} is currently the best word".format(w))
                count += 1 # Can remove after TODO
                    
    print("Best word: " + best_word)
    print("Position: " + best_word_position)
    print("Score: " + str(best_word_score))
    print("Total Time: " + str(time.time() - time_start))
    print("Total count: " + str(count))


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