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
- `best-move NAME LETTERS`: Return best word, word score, and position

---

### Algorithmic Functions and Flow


#### `best-move`

- `best-word NAME LETTERS`: Given game `NAME` and tiles `LETTERS`, scan the board to find the best possible move.
- "Best move" meaning the move that reaps the greatest score.

Algorithm(s)


`best-move`

```
1:  letters = letters in hand
2:  best_word = nil
3:  best_word_position = nil
4:  best_word_score = 0
5:  for (each row and column){
6:      curr= current row or column
7:      curr_words = collect all words from curr
8:      possible_words = all words from dictionary made out of curr_words + letters
9:      for (each possible_word){
10:         position = position of this possible_word
11:         if (boardValid){ // if curr and all perpendicular rows/columns are still valid when possible_word applied
12:             points = points awarded for word, including special tile scores and perpendicular word scores
13:             if ( points > best_word_score ){
14:                 best_word_score = points
15:                 best_word_position = position
16:                 best_word = possible_word
17:             }
18:         }
19:     }
20: }
21: return best_word, best_word_position, best_word_score
```

---

## Edge cases

- Opening move (empty board) special case?s
- Blank tile
- If board has non-legit word set, `best-word` will always return `invalid board`