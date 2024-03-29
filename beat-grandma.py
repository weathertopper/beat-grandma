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
        if letter != "":
            column_letters.append(letter)
    return column_letters 

def getRowLetters(board, position):
    row_letters = []
    row = getPositionRow(position)
    for char in os.environ[POSSIBLE_COLS_KEY]:
        letter = getLetterOnBoardAtPosition(board, buildPosition(char, row))
        if letter != "":
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
    if directionIsHorizontal(direction):
        return positionMoveRight(position)
    else:
        return positionMoveDown(position)

def previousPosition(position, direction):
    if directionIsHorizontal(direction):
        return positionMoveLeft(position)
    else:
        return positionMoveUp(position)  

# Returns True if:
# Word fits on board (meaning spaces don't run out and spaces aren't already taken)
def wordFits(board, position, direction, word):
    curr_pos = position
    for letter_in_word in word:
        if not curr_pos:
            return False
        letter_on_board = getLetterOnBoardAtPosition(board, curr_pos)
        if letter_on_board == letter_in_word or letter_on_board == "":
            curr_pos = nextPosition(curr_pos, direction)
        else:
            return False
    return True

# Returns True if:
# Word can be played with letters on board AND at least one letter from hand
def wordPlayable(board, letters, position, direction, word, blank_tile_count): #TODO
    letters_to_use = copy.deepcopy(letters)
    blanks_available_count = copy.deepcopy(blank_tile_count)
    used_letters = {}
    blanks_used_count = 0
    curr_pos = position
    for letter_in_word in word:
        letter_on_board = getLetterOnBoardAtPosition(board, curr_pos)
        if letter_on_board != "" and letter_on_board is letter_in_word:
            unused = 0
        elif letter_in_word in letters_to_use:
            used_letters[curr_pos] = letter_in_word
            letters_to_use.remove(letter_in_word)
        else:
            if blanks_available_count > 0:
                blanks_available_count = blanks_available_count -1
                blanks_used_count = blanks_used_count + 1
            else:
                return False
        curr_pos = nextPosition(curr_pos, direction)
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
        if getLetterOnBoardAtPosition(board, pos) != "":
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
    curr_pos = start_pos
    if len(word) == 1: # not a legit word
        return 0
    for letter in word:
        letter_score = int(lookupLetterScore(letter, tile_values_dict))
        letter_at_curr_pos = getLetterOnBoardAtPosition(clean_board, curr_pos)
        special_tile = lookupSpecialTile(special_tiles, curr_pos)
        if curr_pos in all_blank_positions:
            letter_score=0

        if letter_at_curr_pos != "" or special_tile == "S" or not special_tile:
            word_score = word_score + letter_score
        elif special_tile == "d":
            word_score = word_score +  (2 * letter_score)
        elif special_tile == "t":
            word_score = word_score +  (3 * letter_score)
        elif special_tile == "T":
            triple_word_count = triple_word_count +  1
            word_score = word_score + letter_score
        elif special_tile == "D":
            double_word_count = double_word_count +  1
            word_score = word_score + letter_score
        curr_pos = nextPosition(curr_pos, direction)
    if triple_word_count > 0:
        word_score = word_score * triple_word_count * 3
    if double_word_count > 0:
        word_score = word_score * double_word_count * 2

    return word_score
        

# returns dict of {pos: letter} pairs
def getLettersPlayed(board, position, direction, word):
    letters_played = dict()
    curr_pos = position
    for letter in word:
        if getLetterOnBoardAtPosition(board, curr_pos) == "":
            letters_played[curr_pos] = letter
        curr_pos = nextPosition(curr_pos, direction)
    return letters_played

def getBlanksToPlay(letters_to_play, letters_in_hand):
    blanks_to_play = []
    letters_in_hand_copy = copy.deepcopy(letters_in_hand)
    for curr_pos in letters_to_play:
        if letters_to_play[curr_pos] in letters_in_hand_copy:
            letters_in_hand_copy.remove(letters_to_play[curr_pos])
        else:
            blanks_to_play.append(curr_pos)
    return blanks_to_play

# Returns a list of letters that will be filled by blanks
def getBlankLettersToPlay(letters_to_play, letters_in_hand):
    blanks_letters_to_play = []
    letters_in_hand_copy = copy.deepcopy(letters_in_hand)
    for curr_pos in letters_to_play:
        if letters_to_play[curr_pos] in letters_in_hand_copy:
            letters_in_hand_copy.remove(letters_to_play[curr_pos])
        else:
            blanks_letters_to_play.append(letters_to_play[curr_pos])
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
        if getLetterOnBoardAtPosition(dirty_board, prev_pos) != "":
            start_position = prev_pos
        else:
            return start_position
    return start_position

def getWordOnBoardAtPositionInDirection(dirty_board, start_position, direction):
    word = ""
    curr_pos = start_position
    while curr_pos: 
        if getLetterOnBoardAtPosition(dirty_board, curr_pos) == "":
            break
        word += getLetterOnBoardAtPosition(dirty_board, curr_pos)
        curr_pos = nextPosition(curr_pos, direction)
    return word

# Returns points for given move
# need to know which letters from hand played in which positions

def calculatePoints(clean_board, dirty_board, start_position, direction, position_letter_dict, letters, special_tiles, tile_values_dict, all_blank_positions):
    total_points = 0
    primary_word = getWordOnBoardAtPositionInDirection(dirty_board, start_position, direction)
    total_points += calculateWordScore(clean_board,start_position,direction, primary_word, special_tiles, tile_values_dict, all_blank_positions)
    opposite_direction = getOppositeDirection(direction)
    for pos in position_letter_dict:
        first_pos_in_word = getStartPositionOfWordOnBoardAtPositionInDirection(dirty_board, pos, opposite_direction)
        adjacent_word = getWordOnBoardAtPositionInDirection(dirty_board, first_pos_in_word, opposite_direction)
        total_points = total_points + calculateWordScore(clean_board, first_pos_in_word, opposite_direction, adjacent_word, special_tiles, tile_values_dict, all_blank_positions)
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
    max_len = max(int(os.environ[ROW_LENGTH_KEY]), len(os.environ[POSSIBLE_COLS_KEY]))
    thinned = filter(lambda x: len(x) <= max_len, word_list) # removing words that are too long
    return thinned

def thinWordList(word_list, letters, blank_count):
    local_word_list = copy.deepcopy(word_list)
    possible_len = len(letters) + blank_count
    thinned_by_len = filter(lambda x: len(x) <= possible_len, local_word_list) 
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
    if not blank_letter_positions:
        return []
    keys = blank_letter_positions.keys()
    iterations = getBlankIterationsRecursive(keys, blank_letter_positions)
    # more math?
    return iterations

def getBlankIterationsRecursive(keys, blank_letter_positions):
    keys_copy = copy.deepcopy(list(keys))
    iterations = []
    if not keys:
        return iterations
    curr_key = keys_copy[0]
    curr_vals = blank_letter_positions[curr_key]
    keys_copy.remove(curr_key)
    remaining_keys = copy.deepcopy(keys_copy)
    # exit case.. this seems redundant
    if not remaining_keys:
        for val in curr_vals:
            iterations.append(val)
        return iterations

    for val in curr_vals:
        next_iterations = getBlankIterationsRecursive(remaining_keys, blank_letter_positions)
        next_iterations = list(map(lambda x : val+","+ x , next_iterations))
        iterations.extend(next_iterations)
    
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

    special_tiles=readSpecialTilesAsDict()

    all_positions = getListOfAllPositions()

    all_directions =  ["horizontal", "vertical"]

    tile_values_dict=readTileValuesAsDict()

    count = 0

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
        col_word_lists[char] = thinWordList(word_list, col_letters, blank_tile_count)
    for i in range(int(os.environ[ROW_LENGTH_KEY])):
        row_index = str( i + 1 )
        fake_position = buildPosition(os.environ[POSSIBLE_COLS_KEY][0], row_index)
        row_letters = getRowLetters(clean_board, fake_position)
        row_letters.extend(letters)
        row_word_lists[row_index] = thinWordList(word_list, row_letters, blank_tile_count)

    if not validateAllWordsOnBoard(clean_board, True):
        print("Starting with an invalid board!")
        return

    for p in all_positions:
        for d in all_directions:
            thinned_word_list = col_word_lists.get(getPositionCol(p))
            if directionIsHorizontal(d):
                thinned_word_list = row_word_lists.get(str(getPositionRow(p)))
            for w in thinned_word_list:
                if w == "":
                    continue
                if wordFits(clean_board, p, d, w):
                    if wordPlayable(clean_board, letters, p, d, w, blank_tile_count):
                        if first_move or wordConnected(clean_board, letters, p, d, w):
                            letters_to_play = getLettersPlayed(clean_board, p, d, w)
                            if not letters_to_play: # no letters to play-- word is complete already
                                continue

                            dirty_board = setWordOnBoard(deepCopyBoard(clean_board), p, w, d, game)
                            if validateAllWordsOnBoard(dirty_board, False):

                                blank_letters_to_play = getBlankLettersToPlay(letters_to_play, letters)
                                blank_letter_positions = getBlankLetterPositions(blank_letters_to_play, letters_to_play) # for each letter replaced by blank, all of the positions where that blank can be played
                                iterations = getBlankIterations(blank_letter_positions)
                    
                                if not iterations: #no blanks to play this word
                                    score = calculatePoints(clean_board, dirty_board, p, d, letters_to_play, letters, special_tiles, tile_values_dict, blanks_already_played)
                                    decideBestMove(score,w,p,d,[])
                                
                                for blank_iter_string in iterations:
                                    blank_positions_to_play = blank_iter_string.split(",")
                                    all_blanks_in_play = blank_positions_to_play + blanks_already_played
                                    score = calculatePoints(clean_board, dirty_board, p, d, letters_to_play, letters, special_tiles, tile_values_dict, all_blanks_in_play)
                                    decideBestMove(score,w,p,d,blank_positions_to_play)
                count += 1
    printBestMove(time_start, time.time(), count, first_move)

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