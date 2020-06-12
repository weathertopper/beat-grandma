import click
import shutil
import os
import string

saved_games_dir="games"

def getGameFilePath(game):
    return os.path.join(os.getcwd(), saved_games_dir, "{}.csv".format(game))

def getTemplateFilePath():
    return os.path.join(os.getcwd(), saved_games_dir, "_template.csv")

def validateDirection(direction):
    if direction == "vertical" or direction == "v" or direction == "horizontal" or direction == "h":
        return True
    print("The direction {} is invalid. Valid directions are <vertical> <v> <horizontal> <h>".format(direction))
    return False

def validateGame(game):
    game_file = getGameFilePath(game)
    if os.path.exists(game_file):
        return True
    print("The game file {} does not exist".format(game_file))
    return False

def validatePositionLength(position):
    return len(position) == 2 or len(position) == 3

def getPositionRow(position): #i.e. the number
    if validatePositionLength(position):
        return position[1:]
    return False

def getPositionCol(position): #i.e. the letter
    if validatePositionLength(position):
        return position[0]
    return False

def validatePositionRow(row):
    rowAsInt = -1
    try:
        rowAsInt = int(row)
        return 0 <= rowAsInt <= 14
    except:
        return False

def validatePositionCol(col):
    possibleCols = "abcdefghijklmno"
    return col in possibleCols

def validatePosition(position):
    col = getPositionCol(position)
    row = getPositionRow(position)
    if row and col:
        return validatePositionCol(col) and validatePositionRow(row)
    return False

def readGameAtPosition(game, position):
    return False

def validateWordPosition(game, position, word, direction):
    gameValid = validateGame(game)
    directionValid = validateDirection(direction)
    return False

def testInput(command, game, letters, position, word, direction):
    click.echo(" command: {}\n game: {}\n letters: {}\n position: {}\n word: {}\n direction: {}".format(command, game, letters, position, word, direction))

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
        board[i].insert(0, i)
    board.insert(0, header_row)
    print(boardToPrettyString(board))

def setWord(game, letters, position, word, direction):
    dv = validateDirection(direction)
    click.echo(" SET WORD \n game: {}\n letters: {}\n position: {}\n word: {}\n direction: {}".format(game, letters, position, word, direction))

def removeWord(game, letters, position, word, direction):
    dv = validateDirection(direction)
    click.echo(" REMOVE WORD \n game: {}\n letters: {}\n position: {}\n word: {}\n direction: {}".format(game, letters, position, word, direction))

def bestMove(game, letters, position):
    click.echo(" BEST MOVE \n game: {}\n letters: {}\n position: {}".format(game, letters, position))


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
    elif command == "create-game":
        createGame(game)
    elif command == "delete-game": 
        deleteGame(game)
    elif command == "print-game":
        printGame(game)
    elif command == "set-word":
        setWord(game, letters, position, word, direction)
    elif command == "remove-word":
        removeWord(game, letters, position, word, direction)
    elif command == "best-move":
        bestMove(game, letters)
    else:
        print ("default")

if __name__ == "__main__":
    main()