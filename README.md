# Objective: Beat Grandma Janey at Words with Friends

Her reign of terror has gone on long enough. It's time I put a stop to it.

Run `make how-to` before doing anything else.

## Approach

Given a board and a set of in-hand tiles, calculate the word and position of the word that reaps the most points.

## Elevator pitch

- I/O: Python3 CLI
- Board data structure: list of comma separated rows
- Hard-code board size and special tiles
- Dictionary: {ENABLE word list} + {WWF2-added-words} - {WWF2-removed-words}

## Functionality

### Python3 CLI

- `new-game -g NAME`: Create new board for new game
- `delete-game -g NAME`: Delete game
- `set-word -g NAME -p POSITION -d DIRECTION -w WORD`: Update board NAME at POSITION with WORD
- `best-move -g NAME -l LETTERS`: Return best word, word score, and position
- `print-game -g NAME`: Print active board game (pretty)

---

### Algorithmic Functions and Flow

#### `best-move`

- `best-word NAME LETTERS`: Given game `NAME` and tiles `LETTERS`, scan the board to find the best possible move.
- "Best move" meaning the move that reaps the greatest score.

---

## Unsupported cases

- If board has non-legit word set, `best-word` will always return `invalid board` until new word added to list

---

### How to run

`py beat-grandma.py <command> --game <game> --letters <letters> --position <position> --word <word> --direction <direction>`

^^ these are all of the flags

---
