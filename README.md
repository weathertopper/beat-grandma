# Objective: Beat Grandma Janey at Words with Friends

Her reign of terror has gone on long enough. It's time I put a stop to it.

## Approach

Given a board and a set of in-hand tiles, calculate the word and position of the word that reaps the most points.

## Elevator pitch

- I/O: Python3 CLI
- Board data structure: list of comma separated rows
- Hard-code board size and special tiles
- Dictionary: {ENABLE word list} + {WWF2-added-words} - {WWF2-removed-words}

## Functionality

### Python3 CLI

- `new-game NAME`: Create new board for new game
- `delete-game NAME`: Delete game
- `set-word NAME POSITION WORD`: Update board NAME at POSITION with WORD
- `remove-word NAME POSITION WORD`: Remove word, if it matches
- `best-word NAME LETTERS`: Return best word, word score, and position

---

### Algorithmic Functions and Flow


#### `best-word`

- `best-word NAME LETTERS`: Given game `NAME` and tiles `LETTERS`, scan the board to find the best possible move.
- "Best move" meaning the move that reaps the greatest score.

Algorithm(s)

```
letters = letters in hand
for (each row and column){
    curr= current row or column
    curr_words = collect all words from curr
    possible_words = all words from dictionary made out of curr_words + letters
    for (each possible_word){
        
    }
}
```



- Create new game

while (game)
- Set word played by opponent
  - Should fail if board not valid
- Get best word
- Set best word
end

---

## Edge cases:

- Opening move (empty board) special case?s
- Blank tile
- If board has non-legit word set, `best-word` will always return `invalid board`