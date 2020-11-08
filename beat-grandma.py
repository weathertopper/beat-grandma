import click
import shutil
import os
import string
import time
import copy

# GLOBALS
ALIAS_SHORTHAND="bg"
LETTER_COUNT_FOR_BINGO=7
BLANK_FILE_TEMPLATE_FILE_NAME="_blank_tiles_template.csv"

# GLOBALS ONLY USED IN BEST MOVE
BEST_WORD=""
BEST_WORD_POSITION=""
BEST_WORD_DIRECTION=""
BEST_WORD_BLANK_POSITIONS=[]
BEST_WORD_SCORE=0


# ENVIRONMENT VARIABLE KEYS
DICTIONARY_DIR_KEY="dictionary_dir"
ENABLED_WORD_LIST_KEY="enable_word_list_file"
ADDED_WORDS_KEY="wwf2_added_word_list_file"
REMOVED_WORDS_KEY="wwf2_removed_word_list_file"
CONFIG_DIR_KEY="config_dir"
TILE_VALUES_FILE_KEY="tile_values_file_name"
BINGO_BONUS_KEY="bingo_bonus"
SOLO_STRING_KEY="solo_string"
SPECIAL_TILES_FILE_KEY="special_tiles_file_name"
SAVED_GAME_DIR_KEY="game_dir"
POSSIBLE_COLS_KEY="possible_cols"
ROW_LENGTH_KEY="row_length"
TEMPLATE_FILE_KEY="template_file"

def setEnvironmentVariables(game_mode):
    os.environ[DICTIONARY_DIR_KEY]="dictionary"
    os.environ[ENABLED_WORD_LIST_KEY]="enable1.txt"
    os.environ[ADDED_WORDS_KEY]="wwf2_added.txt"
    os.environ[REMOVED_WORDS_KEY]="wwf2_removed.txt"
    os.environ[CONFIG_DIR_KEY]="config"
    os.environ[TILE_VALUES_FILE_KEY]="_wwf_tile_values.csv"
    os.environ[BINGO_BONUS_KEY]="35"
    os.environ[SOLO_STRING_KEY]="solo"
    if game_mode == os.environ[SOLO_STRING_KEY]:
        os.environ[SPECIAL_TILES_FILE_KEY]="_solo_wwf_special_tiles.csv"
        os.environ[SAVED_GAME_DIR_KEY]="solo_games"
        os.environ[POSSIBLE_COLS_KEY]="abcdefghijk"
        os.environ[ROW_LENGTH_KEY]="11"
        os.environ[TEMPLATE_FILE_KEY]="_solo_template.csv"
    else:
        os.environ[SPECIAL_TILES_FILE_KEY]="_wwf_special_tiles.csv"
        os.environ[SAVED_GAME_DIR_KEY]="games"
        os.environ[POSSIBLE_COLS_KEY]="abcdefghijklmno"
        os.environ[ROW_LENGTH_KEY]="15"
        os.environ[TEMPLATE_FILE_KEY]="_template.csv"

def validateDirection(direction):
    if direction == "vertical" or direction == "v" or direction == "horizontal" or direction == "h":
        return True
    print("The direction {} is invalid. Valid directions are <vertical> <v> <horizontal> <h>".format(direction))
    return False

def validateWord(word):
    if word:
        return len(word) > 0
    return False

def validateGame(game):
    game_file = getGameFilePath(game)
    if os.path.exists(game_file):
        return True
    print("The game file {} does not exist".format(game_file))
    return False

def validateLetters(letters):
    return letters and len(letters)

def validatePositionLength(position):
    return len(position) == 2 or len(position) == 3

def validatePositionRow(row):
    rowAsInt = -1
    try:
        rowAsInt = int(row)
        return 1 <= rowAsInt <= int(os.environ[ROW_LENGTH_KEY])
    except:
        return False

def validatePositionCol(col):
    return col in os.environ[POSSIBLE_COLS_KEY]

def validatePosition(position):
    col = getPositionCol(position)
    row = getPositionRow(position)
    if row and col:
        return validatePositionCol(col) and validatePositionRow(row)
    return False

def getGameFilePath(game):
    return os.path.join(os.getcwd(), os.environ[SAVED_GAME_DIR_KEY], "{}.csv".format(game))

def getGameBlankTileFilePath(game):
    return os.path.join(os.getcwd(), os.environ[SAVED_GAME_DIR_KEY], "{}-blank-tiles.csv".format(game))

def getEnableWordFilePath():
    return os.path.join(os.getcwd(), os.environ[DICTIONARY_DIR_KEY], os.environ[ENABLED_WORD_LIST_KEY])

def getWWF2AddedWordFilePath():
    return os.path.join(os.getcwd(), os.environ[DICTIONARY_DIR_KEY], os.environ[ADDED_WORDS_KEY])

def getWWF2RemovedWordFilePath():
    return os.path.join(os.getcwd(), os.environ[DICTIONARY_DIR_KEY], os.environ[REMOVED_WORDS_KEY])

def getTemplateFilePath():
    return os.path.join(os.getcwd(), os.environ[CONFIG_DIR_KEY], os.environ[TEMPLATE_FILE_KEY])

def getBlankTilesTemplateFilePath():
    return os.path.join(os.getcwd(), os.environ[CONFIG_DIR_KEY], BLANK_FILE_TEMPLATE_FILE_NAME)

def getTileValuesFilePath():
    return os.path.join(os.getcwd(), os.environ[CONFIG_DIR_KEY], os.environ[TILE_VALUES_FILE_KEY])

def getSpecialTilesFilePath():
    return os.path.join(os.getcwd(), os.environ[CONFIG_DIR_KEY], os.environ[SPECIAL_TILES_FILE_KEY])

def getPositionRow(position): #i.e. the number
    if validatePositionLength(position):
        return position[1:]
    return False

def getPositionCol(position): #i.e. the letter
    if validatePositionLength(position):
        return position[0].lower()
    return False

def getPositionColIndex(position): #i.e. the index of the letter
    return os.environ[POSSIBLE_COLS_KEY].find(getPositionCol(position))

def buildPosition(col, row): # assumes col and row are valid
    return col + str(row)

def directionIsHorizontal(direction): # otherwise it's vertical
    return direction == "horizontal" or direction == "h"

def getOppositeDirection(direction):
    if directionIsHorizontal(direction):
        return "vertical"
    return "horizontal"

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
        left_col = os.environ[POSSIBLE_COLS_KEY][prev_col_index]
        return buildPosition(left_col, getPositionRow(position))
    return False

def positionMoveRight(position): # returns next position if valid, else False (assumes position is valid)
    next_col_index = getPositionColIndex(position) + 1
    if next_col_index < len(os.environ[POSSIBLE_COLS_KEY]):    
        right_col = os.environ[POSSIBLE_COLS_KEY][next_col_index]
        return buildPosition(right_col, getPositionRow(position))
    return False

def getColumnLetters(board,position):
    column_letters = []
    col = getPositionCol(position)
    for i in range(int(os.environ[ROW_LENGTH_KEY])):
        letter = getLetterOnBoardAtPosition(board, buildPosition(col, i+1))
        if letter is not "":
            column_letters.append(letter)
    return column_letters 

def getRowLetters(board, position):
    row_letters = []
    row = getPositionRow(position)
    for char in os.environ[POSSIBLE_COLS_KEY]:
        letter = getLetterOnBoardAtPosition(board, buildPosition(char, row))
        if letter is not "":
            row_letters.append(letter)
    return row_letters 

def testInput(command, game, letters, position, word, direction, game_mode, blank_tiles):
    print(" command: {}\n game: {}\n letters: {}\n position: {}\n word: {}\n direction: {}\n game_mode: {}\n blank_tiles: {}\n".format(command, game, letters, position, word, direction, game_mode, blank_tiles))

def createGame(game):
    template_file = getTemplateFilePath()
    copy_file = getGameFilePath(game)
    shutil.copyfile(template_file, copy_file)
    blank_tiles_template_file = getBlankTilesTemplateFilePath()
    blank_tiles_file = getGameBlankTileFilePath(game)
    shutil.copyfile(blank_tiles_template_file, blank_tiles_file)
    printGame(game)

def deleteGame(game):
    if validateGame(game):
        game_file = getGameFilePath(game)
        os.remove(game_file)
        blank_tiles_file = getGameBlankTileFilePath(game)
        os.remove(blank_tiles_file)

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

def deepCopyBoard(board):
    return copy.deepcopy(board)

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

def readBlankTilesAsList(game):
    f = open(getGameBlankTileFilePath(game), "r")
    blank_tiles_as_string = f.read()
    if len(blank_tiles_as_string) == 0:
        return []
    return blank_tiles_as_string.split(",")


def setBlankTile(game, position):
    if not validatePosition(position):
        return
    blank_tiles_as_list = readBlankTilesAsList(game)
    f = open(getGameBlankTileFilePath(game), "w")
    if not blank_tiles_as_list:
        f.write(position)
    else:
        blank_tiles_as_list.append(position)
        f.write(",".join(blank_tiles_as_list))
    f.close()

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

def setWordOnBoard(board, position, word, direction, game):
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
    board = setWordOnBoard(readFullBoard(game), position, word, direction, game)
    writeBoardToFile(game, board)
    print(" Set word {} at position {} in direction {} for game {}\n".format(word, position, direction, game))
    printGame(game)

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
    header_row = list(string.ascii_lowercase)[:int(os.environ[ROW_LENGTH_KEY])]
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
    board = readEmptyBoard()
    special_tiles=readSpecialTilesAsDict()
    for pos, char in special_tiles.items():
        setLetterOnBoardAtPosition(char, board, pos)
    printBoard(board)
    

def printTileValues():
    # print ("TILE VALUES")
    tile_values_dict=readTileValuesAsDict()
    for t, v in tile_values_dict.items():
        print(t + " : " + v)

def getListOfAllPositions(): 
    all_positions = []
    for char in os.environ[POSSIBLE_COLS_KEY]:
        for i in range(int(os.environ[ROW_LENGTH_KEY])):
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

def nextPosition(position, direction):
    # print("in nextPosition: "+ "position: "+position+ " direction "+direction)
    if directionIsHorizontal(direction):
        # print("IS HORIZONTAL")
        # print("positionMoveRight: " + positionMoveRight(position))
        return positionMoveRight(position)
    else:
        # print("IS VERTICAL")
        # print("positionMoveDown: " + positionMoveDown(position))
        return positionMoveDown(position)

def previousPosition(position, direction):
    if directionIsHorizontal(direction):
        return positionMoveLeft(position)
    else:
        return positionMoveUp(position)  

# NW TAKE OUT THIS UPDATED DEF IT EVERYTHING ENDS UP WORKING
# Returns True if:
# Word fits on board (meaning spaces don't run out and spaces aren't already taken)
# def wordFits(board, letters, position, direction, word, blank_tile_count):
#     blank_count_copy = copy.deepcopy(blank_tile_count)
#     curr_pos = position
#     print("wordFits: {} {} {} {}".format(word, position, direction, blank_count_copy ))
#     for letter_in_word in word:
#         print("wordFits: {}".format(curr_pos))
#         print("letter_in_word: {}".format(letter_in_word))
#         if not curr_pos:
#             print("wordFits curr_pos {} DNE".format(curr_pos))
#             return False
#         letter_on_board = getLetterOnBoardAtPosition(board, curr_pos)
#         if letter_on_board == letter_in_word:
#             print("wordFits letter_on_board {} == letter_in_word {}".format(letter_on_board, letter_in_word ))
#             curr_pos = nextPosition(curr_pos, direction)
#         elif letter_on_board == "":
#             print("wordFits letter_on_board {} is empty".format(letter_on_board, letter_in_word ))
#             curr_pos = nextPosition(curr_pos, direction)
#         else:
#             print("wordFits letter_on_board {} == letter_in_word {} or is empty".format(letter_on_board, letter_in_word ))
#             if blank_count_copy > 0:
#                 blank_count_copy = blank_count_copy - 1
#                 curr_pos = nextPosition(curr_pos, direction)
#             else:
#                 return False
#     return True

# Returns True if:
# Word fits on board (meaning spaces don't run out and spaces aren't already taken)
def wordFits(board, position, direction, word):
    curr_pos = position
    # print("wordFits: {} {} {}".format(word, position, direction ))
    for letter_in_word in word:
        # print ("wordFits: letter_in_word {} curr_pos {}".format(letter_in_word, curr_pos))
        if not curr_pos:
            # print("wordFits curr_pos {} DNE".format(curr_pos))
            return False
        letter_on_board = getLetterOnBoardAtPosition(board, curr_pos)
        # print("wordFits letter_on_board {} ".format(letter_on_board))
        if letter_on_board == letter_in_word or letter_on_board == "":
            # print("wordFits LETTER FITS! NEXT POS!")
            curr_pos = nextPosition(curr_pos, direction)
        else:
            # print("wordFits DOESNT FIT! DANGER DANGER!")
            return False
    # print("wordFits FITS! HURRAY!: {} {} {}".format(word, position, direction ))
    return True

# Returns True if:
# Word can be played with letters on board AND at least one letter from hand
def wordPlayable(board, letters, position, direction, word, blank_tile_count): #TODO
    # print("LOG wordPlayable: word {} letters {} position {} direction {}".format(word, letters, position, direction))
    letters_to_use = copy.deepcopy(letters)
    blanks_available_count = copy.deepcopy(blank_tile_count)
    # print("LOG wordPlayable: letters_to_use {}".format(letters_to_use))
    used_letters = {}
    blanks_used_count = 0
    curr_pos = position
    # print("LOG wordPlayable: curr_pos {}".format(curr_pos))
    for letter_in_word in word:
        # print("LOG wordPlayable: for loop letter_in_word {}".format(letter_in_word))
        letter_on_board = getLetterOnBoardAtPosition(board, curr_pos)
        # print("LOG wordPlayable: for loop letter_on_board {}".format(letter_on_board))
        if letter_on_board is not "" and letter_on_board is letter_in_word:
            unused = 0
            # print("LOG wordPlayable: letter_on_baard is not empty")
            # continue
        elif letter_in_word in letters_to_use:
            # print("LOG wordPlayable: for loop letter_in_word {} letters_to_use {}".format(letter_in_word, letters_to_use))
            used_letters[curr_pos] = letter_in_word
            # print("LOG wordPlayable: for loop used_letters {}".format(used_letters))
            letters_to_use.remove(letter_in_word)
            # print("LOG wordPlayable: for loop letter_in_word {}".format(letter_in_word))
        else:
            if blanks_available_count > 0:
                blanks_available_count = blanks_available_count -1
                blanks_used_count = blanks_used_count + 1
            else:
                # print("LOG wordPlayable: for loop returning false")
                return False
        curr_pos = nextPosition(curr_pos, direction)
        # print("LOG wordPlayable: curr pos next pos {}".format(curr_pos))
    return bool(used_letters) or bool(blanks_used_count) # empty dict or 0 gives bool value of False


def getAdjacentPositions(position,direction):
    adj_pos = []
    if directionIsHorizontal(direction):
        up_one = positionMoveUp(position)
        if up_one:
            adj_pos.append(up_one)
        down_one = positionMoveDown(position)
        if down_one:
            adj_pos.append(down_one)
    else:
        left_one = positionMoveLeft(position)
        if left_one:
            adj_pos.append(left_one)
        right_one = positionMoveRight(position)
        if right_one:
            adj_pos.append(right_one)
    return adj_pos

# Returns all positions surrounding the given word
# Assumes word fits
def buildBoundingBox(board, position, direction, word):
    positions_to_check = []
    pre_pos = previousPosition(position, direction)
    if pre_pos:
        positions_to_check.append(pre_pos)
    curr_pos = position
    for i in range(len(word)):
        positions_to_check.append(curr_pos)
        positions_to_check.extend(getAdjacentPositions(curr_pos, direction))
        curr_pos = nextPosition(curr_pos, direction)
    if curr_pos: # this is now post_position, if it exists
        positions_to_check.append(curr_pos)
    return positions_to_check


# Returns True if:
# Word connected to other words on board
def wordConnected(board, letters, position, direction, word): #TODO
    connected_positions = buildBoundingBox(board, position, direction, word)
    for pos in connected_positions:
        if getLetterOnBoardAtPosition(board, pos) is not "":
            return True
    return False

def lookupLetterScore(letter, tile_values_dict):
    return tile_values_dict.get(letter,0)

def lookupSpecialTile(special_tiles, position):
    return special_tiles.get(position, False)

def calculateWordScore(clean_board,start_pos, direction, word, special_tiles, tile_values_dict, all_blank_positions):
    word_score = 0
    triple_word_count = 0
    double_word_count = 0
    # print("LOG calculateWordScore word: {} start_pos: {} direction: {}".format(word, start_pos, direction))
    curr_pos = start_pos
    # print("LOG calculateWordScore curr_pos: {}".format(curr_pos))
    if len(word) is 1: # not a legit word
        return 0
    for letter in word:
        # print("LOG calculateWordScore for loop letter: {}".format(letter))
        letter_score = int(lookupLetterScore(letter, tile_values_dict))
        # print("LOG calculateWordScore for loop letter_score: {}".format(letter_score))
        letter_at_curr_pos = getLetterOnBoardAtPosition(clean_board, curr_pos)
        # print("LOG calculateWordScore for loop letter_at_curr_pos: {}".format(letter_at_curr_pos))
        special_tile = lookupSpecialTile(special_tiles, curr_pos)
        # print("LOG calculateWordScore for loop special_tile: {}".format(special_tile))
        # print("LOG all_blank_positions: {}".format(all_blank_positions))
        # print("LOG curr_pos: {}".format(curr_pos))
        if curr_pos in all_blank_positions:
            letter_score=0

        if letter_at_curr_pos is not "" or special_tile == "S" or not special_tile:
            word_score = word_score + letter_score
        elif special_tile == "d":
            word_score = word_score +  (2 * letter_score)
        elif special_tile == "t":
            word_score = word_score +  (3 * letter_score)
        elif special_tile == "T":
            triple_word_count = triple_word_count +  1
            word_score = word_score + letter_score
            # print("LOG calculateWordScore for loop triple_word_count: {}".format(str(triple_word_count)))
        elif special_tile == "D":
            double_word_count = double_word_count +  1
            word_score = word_score + letter_score
            # print("LOG calculateWordScore for loop double_word_count: {}".format(str(double_word_count)))
        curr_pos = nextPosition(curr_pos, direction)
        # print("LOG calculateWordScore for loop word_score: {}".format(str(word_score)))
        # print("LOG calculateWordScore for loop curr_pos: {}".format(curr_pos))
    if triple_word_count > 0:
        # print("LOG calculateWordScore triple_word_count: {}".format(str(triple_word_count)))
        word_score = word_score * triple_word_count * 3
    if double_word_count > 0:
        # print("LOG calculateWordScore double_word_count: {} default word score: {}".format(str(double_word_count), str(word_score)))
        word_score = word_score * double_word_count * 2
        # print("LOG calculateWordScore double_word_count: {} doubled word score: {}".format(str(double_word_count), str(word_score)))

    # print("LOG calculateWordScore return word_score: {}".format(str(word_score)))
    return word_score
        

# returns dict of {pos: letter} pairs
def getLettersPlayed(board, position, direction, word):
    letters_played = dict()
    # print("Word: {}".format(word))
    curr_pos = position
    for letter in word:
        # print("Letter: {}".format(letter))
        # print("curr_pos: {}".format(curr_pos))
        if getLetterOnBoardAtPosition(board, curr_pos) is "":
            letters_played[curr_pos] = letter
            # print("Playing Letter {} at position {}".format(letter, curr_pos))
        curr_pos = nextPosition(curr_pos, direction)
    return letters_played

def getBlanksToPlay(letters_to_play, letters_in_hand):
    blanks_to_play = []
    letters_in_hand_copy = copy.deepcopy(letters_in_hand)
    # print ("letters in hand copy: {}".format(letters_in_hand_copy))
    # print ("letters letters_to_play hand: {}".format(letters_to_play))
    for curr_pos in letters_to_play:
        # print("curr_pos: {}".format(curr_pos))
        # print("letters_to_play[curr_pos]: {}".format(letters_to_play[curr_pos]))
        if letters_to_play[curr_pos] in letters_in_hand_copy:
            letters_in_hand_copy.remove(letters_to_play[curr_pos])
        else:
            # print("APPENDING TO BLANKS TO PLAY")
            blanks_to_play.append(curr_pos)
    # print ("blanks_to_play: {}".format(blanks_to_play))
    return blanks_to_play

# Returns a list of letters that will be filled by blanks
def getBlankLettersToPlay(letters_to_play, letters_in_hand):
    blanks_letters_to_play = []
    letters_in_hand_copy = copy.deepcopy(letters_in_hand)
    # print ("letters in hand copy: {}".format(letters_in_hand_copy))
    # print ("letters letters_to_play hand: {}".format(letters_to_play))
    for curr_pos in letters_to_play:
        # print("curr_pos: {}".format(curr_pos))
        # print("letters_to_play[curr_pos]: {}".format(letters_to_play[curr_pos]))
        if letters_to_play[curr_pos] in letters_in_hand_copy:
            letters_in_hand_copy.remove(letters_to_play[curr_pos])
        else:
            # print("APPENDING TO BLANKS TO PLAY")
            blanks_letters_to_play.append(letters_to_play[curr_pos])
    # print ("blanks_letters_to_play: {}".format(blanks_letters_to_play))
    return blanks_letters_to_play

def getBlankLetterPositions(blank_letters_to_play, letters_to_play):
    blank_letter_positions  = dict()
    for blank_letter in blank_letters_to_play:
        blank_letter_positions[blank_letter] = []
        for curr_pos in letters_to_play:
            if letters_to_play[curr_pos] == blank_letter:
                blank_letter_positions[blank_letter].append(curr_pos)
    return blank_letter_positions



def getStartPositionOfWordOnBoardAtPositionInDirection(dirty_board, position, direction):
    start_position = position
    while previousPosition(start_position, direction):
        prev_pos = previousPosition(start_position, direction)
        if getLetterOnBoardAtPosition(dirty_board, prev_pos) is not "":
            start_position = prev_pos
        else:
            return start_position
    return start_position

def getWordOnBoardAtPositionInDirection(dirty_board, start_position, direction):
    word = ""
    curr_pos = start_position
    while curr_pos: 
        if getLetterOnBoardAtPosition(dirty_board, curr_pos) is "":
            break
        word += getLetterOnBoardAtPosition(dirty_board, curr_pos)
        curr_pos = nextPosition(curr_pos, direction)
    return word

# Returns points for given move
# need to know which letters from hand played in which positions

def calculatePoints(clean_board, dirty_board, start_position, direction, position_letter_dict, letters, special_tiles, tile_values_dict, all_blank_positions):
    total_points = 0
    # print("LOG calculatePoints start_position: {} direction: {} position_letter_dict: {}".format(start_position, direction, str(position_letter_dict)))
    primary_word = getWordOnBoardAtPositionInDirection(dirty_board, start_position, direction)
    # print("LOG calculatePoints primary_word: {}".format(primary_word))
    total_points += calculateWordScore(clean_board,start_position,direction, primary_word, special_tiles, tile_values_dict, all_blank_positions)
    # print("LOG calculatePoints total_points after primary word: {}".format(str(total_points)))
    opposite_direction = getOppositeDirection(direction)
    # print("LOG calculatePoints opposite_direction : {}".format(str(opposite_direction)))
    for pos in position_letter_dict:
        # print("LOG calculatePoints in for loop: pos : {}".format(pos))
        first_pos_in_word = getStartPositionOfWordOnBoardAtPositionInDirection(dirty_board, pos, opposite_direction)
        # print("LOG calculatePoints in for loop: first_pos_in_word : {}".format(first_pos_in_word))
        adjacent_word = getWordOnBoardAtPositionInDirection(dirty_board, first_pos_in_word, opposite_direction)
        # print("LOG calculatePoints in for loop: adjacent_word : {}".format(adjacent_word))
        total_points = total_points + calculateWordScore(clean_board, first_pos_in_word, opposite_direction, adjacent_word, special_tiles, tile_values_dict, all_blank_positions)
        # print("LOG calculatePoints in for loop: total_points : {}".format(str(total_points)))
    # print("LOG calculatePoints returning total_points: {}".format(str(total_points)))
    if len(position_letter_dict) == LETTER_COUNT_FOR_BINGO:
        total_points = total_points + int(os.environ[BINGO_BONUS_KEY])
    return total_points

# Returns True if:
# All words on board exist in dictionary list
def validateAllWordsOnBoard(board, print_errors):
    words_on_board = getWordsOnBoard(board)
    dictionary = buildWordList();
    for word in words_on_board:
        if word not in dictionary:
            if print_errors:
                print ("Invalid board! Word {} not in dictionary!".format(word))
            return False
    return True

def genericWordListThinning(word_list):
    # print("genericWordListThinning start len: {}".format(str(len(word_list))))
    max_len = max(int(os.environ[ROW_LENGTH_KEY]), len(os.environ[POSSIBLE_COLS_KEY]))
    thinned = filter(lambda x: len(x) <= max_len, word_list) # removing words that are too long
    # print("genericWordListThinning end len: {}".format(str(len(thinned))))
    return thinned


# NW PROBLEM HERE__ NOT RETURNING CORRECT SHORTENED LISTS WHEN BLANKS INVOLVED
def thinWordList(word_list, letters, blank_count):
    # print("thinWordList:\n word_list: {}\n letters: {}\n blank_count: {}".format(word_list, letters, str(blank_count)))
    possible_len = len(letters) + blank_count
    thinned_by_len = filter(lambda x: len(x) <= possible_len, word_list) 
    # print( "thinned_by_len: {}".format(thinned_by_len))
    thinned = []
    for word in thinned_by_len:
        letters_copy=copy.deepcopy(letters)
        blank_count_copy=copy.deepcopy(blank_count)
        word_possible=True
        for char in word:
            if char in letters_copy:
               letters_copy.remove(char)
            else:
                if blank_count_copy > 0:
                    blank_count_copy = blank_count_copy - 1
                else:
                    word_possible=False
                    break
        if word_possible:
            thinned.append(word)
    # print("thinWordList: END COUNT {}\n".format(thinned))
    return thinned
            

def getWordsOnBoard(board):
    word_candidates= []
    for row in board:
        word = ""
        for i in range(len(os.environ[POSSIBLE_COLS_KEY])):
            col = i + 1
            c = row[i]
            if c == "" or col == len(os.environ[POSSIBLE_COLS_KEY]):
                if c != "":
                    word += c
                if word != "":
                    word_candidates.append(word)
                    word = ""
            else:
                word += c

    for col in os.environ[POSSIBLE_COLS_KEY]:
        word = ""
        for i in range(int(os.environ[ROW_LENGTH_KEY])):
            row = i + 1
            pos = buildPosition(col, row)
            c = getLetterOnBoardAtPosition(board, pos)
            if c == "" or row == int(os.environ[ROW_LENGTH_KEY]) :
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


# returns array of comma-separated string positions
def getBlankIterations(blank_letter_positions):
    # print ("getBlankIterations blank_letter_positions: {}".format(blank_letter_positions))
    if not blank_letter_positions:
        return []
    keys = blank_letter_positions.keys()
    # print ("getBlankIterations keys: {}".format(keys))
    iterations = getBlankIterationsRecursive(keys, blank_letter_positions)
    # more math?
    return iterations

def getBlankIterationsRecursive(keys, blank_letter_positions):
    # print ("getBlankIterationsRecursive keys: {} blank_letter_positions: {}".format(keys,blank_letter_positions))
    keys_copy = copy.deepcopy(keys)
    iterations = []
    if not keys:
        # print ("getBlankIterationsRecursive NO KEYS, RETURNING EMPTY LIST")
        return iterations
    curr_key = keys_copy[0]
    curr_vals = blank_letter_positions[curr_key]
    # print ("getBlankIterationsRecursive curr_vals: {} ".format(curr_vals))
    keys_copy.remove(curr_key)
    remaining_keys = copy.deepcopy(keys_copy)
    # exit case.. this seems redundant
    if not remaining_keys:
        # print("getBlankIterationsRecursive EXIT CASE")
        for val in curr_vals:
            iterations.append(val)
        # print("getBlankIterationsRecursive EXIT CASE iterations: {}".format(iterations))
        return iterations

    for val in curr_vals:
        # print ("IN CURR_VAL FOR LOOP")
        # print ("RECUSIVELY CALLING getBlankIterationsRecursive remaining_keys {}".format(remaining_keys))
        next_iterations = getBlankIterationsRecursive(remaining_keys, blank_letter_positions)
        # print ("next_iterations: {}".format(next_iterations))
        next_iterations = list(map(lambda x : val+","+ x , next_iterations))
        # print ("next_iterations after lambert: {}".format(next_iterations))
        iterations.extend(next_iterations)
        # print ("iterations after extending: {}".format(iterations))
    
    # print ("returning iterations: {}".format(iterations))
    return iterations

def getStartingPosition(special_tiles):
    keys = special_tiles.keys()
    for k in keys:
        if special_tiles[k] == "S":
            return k
    return None


def isFirstMove(board, special_tiles):
    start_pos = getLetterOnBoardAtPosition(board, getStartingPosition(special_tiles))
    return start_pos == ""

def decideBestMove(score, word, position, direction, blanks_to_play):
    global BEST_WORD
    global BEST_WORD_POSITION
    global BEST_WORD_DIRECTION
    global BEST_WORD_BLANK_POSITIONS
    global BEST_WORD_SCORE
    if score > BEST_WORD_SCORE or \
        score == BEST_WORD_SCORE and len(word) > len(BEST_WORD):
        BEST_WORD_SCORE = score
        BEST_WORD = word
        BEST_WORD_POSITION = position
        BEST_WORD_DIRECTION = direction
        BEST_WORD_BLANK_POSITIONS = blanks_to_play
        print("CURRENT BEST WORD: Word {} Score {} Blanks: {} Position {} Direction {}".format(BEST_WORD, str(BEST_WORD_SCORE), BEST_WORD_BLANK_POSITIONS, BEST_WORD_POSITION, BEST_WORD_DIRECTION))

def printBestMove(start_time, end_time, count, first_move):
    global BEST_WORD
    global BEST_WORD_POSITION
    global BEST_WORD_DIRECTION
    global BEST_WORD_BLANK_POSITIONS
    global BEST_WORD_SCORE

    if first_move: # shift positions up
        for _ in range(len(BEST_WORD)):
            BEST_WORD_POSITION = positionMoveUp(BEST_WORD_POSITION)
            shifted_blank_positions = []
            for bpi in range(len(BEST_WORD_BLANK_POSITIONS)):
                shifted_blank_positions.append(positionMoveUp(BEST_WORD_BLANK_POSITIONS[bpi]))
            BEST_WORD_BLANK_POSITIONS = shifted_blank_positions

    print("Best word: " + BEST_WORD)
    print("Blanks to play: " + str(BEST_WORD_BLANK_POSITIONS))
    print("Position: " + BEST_WORD_POSITION)
    print("Direction: " + BEST_WORD_DIRECTION)
    print("Score: " + str(BEST_WORD_SCORE))
    print("Total Time: " + str(end_time - start_time))
    print("Total count: " + str(count))

    command_string = "{} set-word -p {} -d {} -w {}".format(ALIAS_SHORTHAND, BEST_WORD_POSITION, BEST_WORD_DIRECTION, BEST_WORD)

    for blank_pos in BEST_WORD_BLANK_POSITIONS:
        blank_pos_command = "\n{} set-blank-tile -p {}".format(ALIAS_SHORTHAND, blank_pos)
        command_string += blank_pos_command

    print (command_string)

# def initGlobals():

#     BEST_WORD=""
#     BEST_WORD_POSITION=""
#     BEST_WORD_DIRECTION=""
#     BEST_WORD_BLANK_POSITIONS=[]
#     BEST_WORD_SCORE=0


def bestMove(game, letters, blank_tiles): 

    # initGlobals()

    letters = list(letters)
    game_valid = validateGame(game)
    letters_valid = validateLetters(letters)

    blank_tile_count = 0
    if blank_tiles:
        blank_tile_count = int(blank_tiles)

    if not (game_valid and letters_valid):
        print(" ERROR: Something not valid. Game Valid: {}; Letters Valid: {}".format(game_valid, letters_valid))
        return False

    time_start = time.time()

    clean_board = readFullBoard(game)

    # best_word=""
    # best_word_position=""
    # best_word_direction=""
    # best_word_blank_positions=[]
    # best_word_score=0

    special_tiles=readSpecialTilesAsDict()

    all_positions = getListOfAllPositions()

    all_directions =  ["horizontal", "vertical"]

    tile_values_dict=readTileValuesAsDict()

    count = 0 # Can remove after TODO

    first_move = isFirstMove(clean_board, special_tiles)
    if first_move:
        all_positions = [getStartingPosition(special_tiles)]
        all_directions = [all_directions[1]]
    
    blanks_already_played = readBlankTilesAsList(game)

    word_list =  genericWordListThinning(buildWordList())

    col_word_lists = dict()
    row_word_lists = dict()
    for char in os.environ[POSSIBLE_COLS_KEY]:
        fake_position = buildPosition(char, 1)
        col_letters= getColumnLetters(clean_board, fake_position)
        col_letters.extend(letters)
        # print("fake_position {} direction {}".format(fake_position, "column" ))
        col_word_lists[char] = thinWordList(word_list, col_letters, blank_tile_count)
    for i in range(int(os.environ[ROW_LENGTH_KEY])):
        row_index = str( i + 1 )
        fake_position = buildPosition(os.environ[POSSIBLE_COLS_KEY][0], row_index)
        row_letters = getRowLetters(clean_board, fake_position)
        row_letters.extend(letters)
        # print("fake_position {} direction {}".format(fake_position, "row" ))
        row_word_lists[row_index] = thinWordList(word_list, row_letters, blank_tile_count)

    # print ("col_word_lists {}".format(col_word_lists))
    # print ("row_word_lists {}".format(row_word_lists))
    if not validateAllWordsOnBoard(clean_board, True):
        print("Starting with an invalid board!")
        return

    for p in all_positions:
        for d in all_directions:
            # print ("BEST MOVE: position {} direction {}".format(p,d))
            thinned_word_list = col_word_lists.get(getPositionCol(p))
            if directionIsHorizontal(d):
                thinned_word_list = row_word_lists.get(str(getPositionRow(p)))
            # print ("BEST MOVE: thinned_word_list {}".format(thinned_word_list)) 
            for w in thinned_word_list:
                if w is "":
                    continue
                if wordFits(clean_board, p, d, w):
                    if wordPlayable(clean_board, letters, p, d, w, blank_tile_count):
                        if first_move or wordConnected(clean_board, letters, p, d, w):
                            # figure out where to play blank tiles here?
                            letters_to_play = getLettersPlayed(clean_board, p, d, w)
                            if not letters_to_play: # no letters to play-- word is complete already
                                continue

                            dirty_board = setWordOnBoard(deepCopyBoard(clean_board), p, w, d, game)
                            if validateAllWordsOnBoard(dirty_board, False):

                                blank_letters_to_play = getBlankLettersToPlay(letters_to_play, letters)
                                # print("blank_letters_to_play: {}".format(blank_letters_to_play))
                                blank_letter_positions = getBlankLetterPositions(blank_letters_to_play, letters_to_play) # for each letter replaced by blank, all of the positions where that blank can be played
                                # print("blank_letter_positions: {}".format(blank_letter_positions))
                                iterations = getBlankIterations(blank_letter_positions)
                                # print ("iterations: {}".format(iterations))
                                # print("letters_to_play: {}".format(letters_to_play))
                    
                                if not iterations: #no blanks to play this word
                                    score = calculatePoints(clean_board, dirty_board, p, d, letters_to_play, letters, special_tiles, tile_values_dict, blanks_already_played)
                                    decideBestMove(score,w,p,d,[])
                                
                                for blank_iter_string in iterations:
                                    blank_positions_to_play = blank_iter_string.split(",")
                                    all_blanks_in_play = blank_positions_to_play + blanks_already_played
                                    score = calculatePoints(clean_board, dirty_board, p, d, letters_to_play, letters, special_tiles, tile_values_dict, all_blanks_in_play)
                                    decideBestMove(score,w,p,d,blank_positions_to_play)
                            
                                # if score > best_word_score or \
                                #     score == best_word_score and len(w) > len(best_word):
                                #     best_word_score = score
                                #     best_word = w
                                #     best_word_position = p
                                #     best_word_direction = d
                                #     best_word_blank_positions = blanks_to_play
                                #     print("CURRENT BEST WORD: Word {} Position {} Direction {} Score {}".format(w, p, d, str(score)))
                count += 1
                # if count % 1000000 == 0: 
                #     print ("count {} time since start {} ".format(str(count), str(time.time()- time_start)))
    printBestMove(time_start, time.time(), count, first_move)
    
    # print("Best word: " + best_word)
    # print("Blanks to play: " + str(best_word_blank_positions))
    # print("Position: " + best_word_position)
    # print("Direction: " + best_word_direction)
    # print("Score: " + str(best_word_score))
    # print("Total Time: " + str(time.time() - time_start))
    # print("Total count: " + str(count))

    # command_string = "{} set-word -p {} -d {} -w {}".format(ALIAS_SHORTHAND, best_word_position, best_word_direction, best_word)

    # for blank_pos in best_word_blank_positions:
    #     blank_pos_command = "\n{} set-blank-tile -p {}".format(ALIAS_SHORTHAND, blank_pos)
    #     command_string += blank_pos_command

    # print (command_string)


# CLI INPUTS
@click.command()
@click.argument('command')
@click.option('--game', '-g')
@click.option('--letters', '-l')
@click.option('--position', '-p')
@click.option('--word', '-w')
@click.option('--direction', '-d')
@click.option('--game-mode', '-m')
@click.option('--blank-tiles', '-b')

# DRIVER
def main(command, game, letters, position, word, direction, game_mode, blank_tiles):
    setEnvironmentVariables(game_mode)
    if command == "test":
        testInput(command, game, letters, position, word, direction, game_mode, blank_tiles)
    elif command == "new-game":
        createGame(game)
    elif command == "delete-game": 
        deleteGame(game)
    elif command == "print-game":
        printGame(game)
    elif command == "set-word":
        setWord(game, position, word, direction)
    elif command == "set-blank-tile":
        setBlankTile(game, position)
    elif command == "print-special-tiles":
        printSpecialTiles()
    elif command == "print-tile-values":
        printTileValues()
    elif command == "best-move":
        bestMove(game, letters, blank_tiles)
    else:
        print("Say what?")

if __name__ == "__main__":
    main()