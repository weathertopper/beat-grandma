import click
import shutil
import os
import string
import pprint

saved_games_dir="games"

def testInput(command, game, letters, position, word):
    click.echo(" command: {}\n game: {}\n letters: {}\n position: {}\n word: {}".format(command, game, letters, position, word))

def createGame(game):
    template_file = os.path.join(os.getcwd(), saved_games_dir, "_template.csv")
    copy_file = os.path.join(os.getcwd(), saved_games_dir, "{}.csv".format(game))
    shutil.copyfile(template_file, copy_file)

def deleteGame(game):
    game_file = os.path.join(os.getcwd(), saved_games_dir, "{}.csv".format(game))
    if os.path.exists(game_file):
        os.remove(game_file)
    else:
        print("The file {} does not exist".format(game_file))

def readBoard(game):
    game_file = os.path.join(os.getcwd(), saved_games_dir, "{}.csv".format(game))
    board=[]
    if os.path.exists(game_file):
        f = open(game_file, "r")
        board_as_string = f.read()
        board_by_row = board_as_string.split("\n")
        for r in board_by_row:
            board.append(r.split(","))
        return board
    print("The file {} does not exist".format(game_file))
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
    board = readBoard(game)
    if board == "":
        return
    header_row = list(string.ascii_lowercase)[:15]
    header_row.insert(0, "")
    for i in range(len(board)):
        board[i].insert(0, i)
    board.insert(0, header_row)
    print(boardToPrettyString(board))


# CLI INPUTS
@click.command()
@click.argument('command')
@click.option('--game', '-g')
@click.option('--letters', '-l')
@click.option('--position', '-p')
@click.option('--word', '-w')

# DRIVER
def main(command, game, letters, position, word):
    if command == "test":
        testInput(command, game, letters, position, word)
    elif command == "create":
        createGame(game)
    elif command == "delete": 
        deleteGame(game)
    elif command == "print":
        printGame(game)
    else:
        print ("default")
        # click.echo(" command: {}\n game: {}\n letters: {}\n position: {}\n word: {}".format(command, game, letters, position, word))

if __name__ == "__main__":
    main()