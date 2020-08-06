import click
import shutil
import os
import string
import time
import copy

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
bingo_bonus = 35

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

def validateLetters(letters):
    return letters and len(letters)

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
        left_col = possible_cols[prev_col_index]
        return buildPosition(left_col, getPositionRow(position))
    return False

def positionMoveRight(position): # returns next position if valid, else False (assumes position is valid)
    next_col_index = getPositionColIndex(position) + 1
    if next_col_index < len(possible_cols):    
        right_col = possible_cols[next_col_index]
        return buildPosition(right_col, getPositionRow(position))
    return False

def getColumnLetters(board,position):
    column_letters = []
    col = getPositionCol(position)
    for i in range(row_length):
        letter = getLetterOnBoardAtPosition(board, buildPosition(col, i+1))
        if letter is not "":
            column_letters.append(letter)
    return column_letters 

def getRowLetters(board, position):
    row_letters = []
    row = getPositionRow(position)
    for char in possible_cols:
        letter = getLetterOnBoardAtPosition(board, buildPosition(char, row))
        if letter is not "":
            row_letters.append(letter)
    return row_letters 

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

tile_values_dict = readTileValuesAsDict()

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

special_tiles = readSpecialTilesAsDict()

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
    board = readEmptyBoard()
    for pos, char in special_tiles.items():
        setLetterOnBoardAtPosition(char, board, pos)
    printBoard(board)
    

def printTileValues():
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

# Returns True if:
# Word fits on board (meaning spaces don't run out and spaces aren't already taken)
def wordFits(board, letters, position, direction, word): #TODO
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
def wordPlayable(board, letters, position, direction, word): #TODO
    # print("wordPlayable: word {} letters {} position {} direction {}".format(word, letters, position, direction))
    letters_to_use = copy.deepcopy(letters)
    # print("wordPlayable: letters_to_use {}".format(letters_to_use))
    used_letters = {}
    curr_pos = position
    # print("wordPlayable: curr_pos {}".format(curr_pos))
    for letter_in_word in word:
        # print("wordPlayable: for loop letter_in_word {}".format(letter_in_word))
        letter_on_board = getLetterOnBoardAtPosition(board, curr_pos)
        # print("wordPlayable: for loop letter_on_board {}".format(letter_on_board))
        if letter_on_board is not "" and letter_on_board is letter_in_word:
            # print("wordPlayable: letter_on_baard is not empty")
            continue
        elif letter_in_word in letters_to_use:
            # print("wordPlayable: for loop letter_in_word {} letters_to_use {}".format(letter_in_word, letters_to_use))
            used_letters[curr_pos] = letter_in_word
            # print("wordPlayable: for loop used_letters {}".format(used_letters))
            letters_to_use.remove(letter_in_word)
            # print("wordPlayable: for loop letter_in_word {}".format(letter_in_word))
        else:
            # print("wordPlayable: for loop returning false")
            return False
        curr_pos = nextPosition(curr_pos, direction)
        # print("wordPlayable: curr pos nextt pos {}".format(curr_pos))
    return used_letters # empty dict gives bool value of False


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

def lookupLetterScore(letter):
    return tile_values_dict.get(letter,0)

def lookupSpecialTile(position):
    return special_tiles.get(position, False)

def calculateWordScore(clean_board,start_pos, direction, word):
    word_score = 0
    triple_word_count = 0
    double_word_count = 0
    # print("calculateWordScore word: {} start_pos: {} direction: {}".format(word, start_pos, direction))
    curr_pos = start_pos
    # print("calculateWordScore curr_pos: {}".format(curr_pos))
    if len(word) is 1: # not a legit word
        return 0
    for letter in word:
        # print("calculateWordScore for loop letter: {}".format(letter))
        letter_score = int(lookupLetterScore(letter))
        # print("calculateWordScore for loop letter_score: {}".format(letter_score))
        letter_at_curr_pos = getLetterOnBoardAtPosition(clean_board, curr_pos)
        # print("calculateWordScore for loop letter_at_curr_pos: {}".format(letter_at_curr_pos))
        special_tile = lookupSpecialTile(curr_pos)
        # print("calculateWordScore for loop special_tile: {}".format(special_tile))
        if letter_at_curr_pos is not "" or not special_tile:
            word_score = word_score + letter_score
        elif special_tile == "d":
            word_score = word_score +  (2 * letter_score)
        elif special_tile == "t":
            word_score = word_score +  (3 * letter_score)
        elif special_tile == "T":
            triple_word_count = triple_word_count +  1
            word_score = word_score + letter_score
            # print("calculateWordScore for loop triple_word_count: {}".format(str(triple_word_count)))
        elif special_tile == "D":
            double_word_count = double_word_count +  1
            word_score = word_score + letter_score
            # print("calculateWordScore for loop double_word_count: {}".format(str(double_word_count)))
        curr_pos = nextPosition(curr_pos, direction)
        # print("calculateWordScore for loop word_score: {}".format(str(word_score)))
        # print("calculateWordScore for loop curr_pos: {}".format(curr_pos))
    if triple_word_count > 0:
        # print("calculateWordScore triple_word_count: {}".format(str(triple_word_count)))
        word_score = word_score * triple_word_count * 3
    if double_word_count > 0:
        # print("calculateWordScore double_word_count: {}".format(str(double_word_count)))
        word_score = word_score * double_word_count * 2
    # print("calculateWordScore return word_score: {}".format(str(word_score)))
    return word_score
        

# returns dict of {pos: letter} pairs
def getLettersPlayed(board, position, direction, word):
    letters_played = dict()
    curr_pos = position
    for letter in word:
        if getLetterOnBoardAtPosition(board, curr_pos) is "":
            letters_played[curr_pos] = letter
        curr_pos = nextPosition(curr_pos, direction)
    return letters_played

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
def calculatePoints(clean_board, dirty_board, start_position, direction, position_letter_dict, letters):
    total_points = 0
    # print("calculatePoints start_position: {} direction: {} position_letter_dict: {}".format(start_position, direction, str(position_letter_dict)))
    primary_word = getWordOnBoardAtPositionInDirection(dirty_board, start_position, direction)
    # print("calculatePoints primary_word: {}".format(primary_word))
    total_points += calculateWordScore(clean_board,start_position,direction, primary_word)
    # print("calculatePoints total_points after primary word: {}".format(str(total_points)))
    opposite_direction = getOppositeDirection(direction)
    # print("calculatePoints opposite_direction : {}".format(str(opposite_direction)))
    for pos in position_letter_dict:
        # print("calculatePoints in for loop: pos : {}".format(pos))
        first_pos_in_word = getStartPositionOfWordOnBoardAtPositionInDirection(dirty_board, pos, opposite_direction)
        # print("calculatePoints in for loop: first_pos_in_word : {}".format(first_pos_in_word))
        adjacent_word = getWordOnBoardAtPositionInDirection(dirty_board, first_pos_in_word, opposite_direction)
        # print("calculatePoints in for loop: adjacent_word : {}".format(adjacent_word))
        total_points = total_points + calculateWordScore(clean_board, first_pos_in_word, opposite_direction, adjacent_word)
        # print("calculatePoints in for loop: total_points : {}".format(str(total_points)))
    # print("calculatePoints returning total_points: {}".format(str(total_points)))
    if len(position_letter_dict) == len(letters):
        total_points = total_points + bingo_bonus
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
    max_len = max(row_length, len(possible_cols))
    thinned = filter(lambda x: len(x) <= max_len, word_list) # removing words that are too long
    # print("genericWordListThinning end len: {}".format(str(len(thinned))))
    return thinned

def thinWordList(word_list, letters, position, direction):
    # print("thinWordList position: {} direction: {} start len: {}".format(position, direction, str(len(word_list))))
    thinned = filter(lambda x: len(x) <= len(letters), word_list) # r
    # print("thinWordList position: {} direction: {} end len: {}".format(position, direction, str(len(thinned))))
    return thinned

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
    letters = list(letters)
    game_valid = validateGame(game)
    letters_valid = validateLetters(letters)

    if not (game_valid and letters_valid):
        print(" ERROR: Something not valid. Game Valid: {}; Letters Valid: {}".format(game_valid, letters_valid))
        return False

    time_start = time.time()

    best_word=""
    best_word_position=""
    best_word_direction=""
    best_word_score=0
   
    all_positions = getListOfAllPositions()
    all_directions =  ["horizontal", "vertical"]

    count = 0 # Can remove after TODO

    clean_board = readFullBoard(game)

    word_list =  genericWordListThinning(buildWordList())

    col_word_lists = dict()
    row_word_lists = dict()
    for char in possible_cols:
        fake_position = buildPosition(char, 1)
        col_letters= getColumnLetters(clean_board, fake_position)
        col_letters.extend(letters)
        col_word_lists[char] = thinWordList(word_list, col_letters, fake_position, "v")
    for i in range(row_length):
        row_index = str( i + 1 )
        fake_position = buildPosition(possible_cols[0], row_index)
        row_letters = getRowLetters(clean_board, fake_position)
        row_letters.extend(letters)
        row_word_lists[row_index] = thinWordList(word_list, row_letters, fake_position, "h")

    if not validateAllWordsOnBoard(clean_board, True):
        print("Starting with an invalid board!")
        return
    
    for p in all_positions:
        for d in all_directions:
            thinned_word_list = col_word_lists.get(getPositionCol(p))
            if directionIsHorizontal(d):
                thinned_word_list = row_word_lists.get(str(getPositionRow(p)))
            for w in thinned_word_list:
                if w is "":
                    continue
                if wordFits(clean_board, letters, p, d, w):
                    if wordPlayable(clean_board, letters, p, d, w):
                        if wordConnected(clean_board, letters, p, d, w):
                            letters_to_play = getLettersPlayed(clean_board, p, d, w)
                            if not letters_to_play: # no letters to play-- word is complete already
                                continue
                            dirty_board = setWordOnBoard(deepCopyBoard(clean_board), p, w, d)
                            if validateAllWordsOnBoard(dirty_board, False):
                                score = calculatePoints(clean_board, dirty_board, p, d, letters_to_play, letters)
                                # print("word {} at position {} in direction {} would score {} points".format(w, p, d, str(score)))
                                if score > best_word_score or \
                                    score == best_word_score and len(w) > len(best_word):
                                    best_word_score = score
                                    best_word = w
                                    best_word_position = p
                                    best_word_direction = d
                                    print("CURRENT BEST WORD: Word {} Position {} Direction {} Score {}".format(w, p, d, str(score)))
                count += 1
                if count % 1000000 == 0: 
                    print ("count {} time since start {} ".format(str(count), str(time.time()- time_start)))
    print("Best word: " + best_word)
    print("Position: " + best_word_position)
    print("Direction: " + best_word_direction)
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
        print("Say what?")

if __name__ == "__main__":
    main()