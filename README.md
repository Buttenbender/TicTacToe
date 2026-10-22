# Tic Tac Toe (TCP)

A two-player, terminal-based Tic Tac Toe game that runs over the network
using plain **TCP sockets** in Python. One player hosts the match, the
other joins by typing the host's IP address. No external libraries required.

## Author
- João Büttenbender

## ✨ Features
- Peer-to-peer play between two computers on the same network (or two terminals on `127.0.0.1`)
- Text-based interface with a menu: create a match, join a match, or exit
- The host's local IP address is shown on screen, so the opponent knows where to connect
- Move validation on both sides (out-of-bounds, occupied cell, malformed messages)
- Win and tie detection
- Handling of disconnections

## 📋 Requirements
- Python 3.6+ (uses f-strings)
- Only the standard library (`os`, `socket`)
- Both players must be able to reach each other on **TCP port 5000** (check your firewall settings)

## 🚀 How to run
Clone the repository and run the script on both computers
1. Choose **2) Join match**.
2. Enter the host's IP address (or `0` to go back to the menu).
3. Once connected, the game starts.

To test on a single machine, open two terminals and use `127.0.0.1` as the IP address.

## 🎮 How to play
- The host plays as **X** and moves first; the guest plays as **O**.
- The board is a 3x3 grid, with rows and columns numbered from **0 to 2**.
- On your turn, type the row and column separated by a space, for example `1 2`:
```
 X |   |
---+---+---
   | O | 
---+---+---
   |   | X
```
 
| Column →<br>Row ↓ | 0 | 1 | 2 |
|:-:|:-:|:-:|:-:|
| **0** | (0,0) | (0,1) | (0,2) |
| **1** | (1,0) | (1,1) | (1,2) |
| **2** | (2,0) | (2,1) | (2,2) |
 
- The game ends when a player gets three in a row (horizontal, vertical or diagonal), or when the board is full (tie).

## 🛠️ How it works

### Architecture
The game uses a direct **client–server** connection:
 
- The player who creates the match acts as the **server**: it binds to `0.0.0.0:5000`, listens, and accepts a single connection.
- The player who joins acts as the **client**: it connects to the host's IP on port `5000` (5-second connection timeout).
Once connected, both programs run the same game loop (`play()`) and keep their own copy of the board. Each side only needs to send its moves to the other.
 
### Application protocol
 
Each move is sent as a single line of text, encoded in UTF-8 and terminated by a newline character:
 
```
<row>,<column>\n
```
 
Example: `1,2\n`
 
Since TCP is a byte stream and does not preserve message boundaries, the **newline (`\n`) marks the end of each message**. The receiver reads with `socket.makefile()` and `readline()`, which waits until a full line has arrived.
 
### Validation
 
- **Local input:** rejects non-numeric input, values outside 0–2, and occupied cells before sending anything.
- **Received moves:** the opponent's message is validated again (format, bounds and occupied cell). If it is invalid, the match ends.
### Main functions
 
| Function | Description |
|---|---|
| `main()` | Shows the menu and starts a match |
| `create_match()` | Opens the server socket and waits for the opponent |
| `join_match()` | Connects to the host's IP |
| `play()` | Main game loop: alternates turns, sends and receives moves |
| `read_local_play()` | Reads and validates the local player's input |
| `valid_position()` | Converts (row, column) to a board index if the cell is valid and free |
| `Winner()` | Checks all winning combinations |
| `print_board()` | Clears the screen and draws the board |
| `find_local_IP()` | Discovers the machine's local IP address |
 
## Project structure
 
```
.
├── main.py   # Full game (menu, networking and game logic)
└── README.md
```
 
## Troubleshooting
 
- **"Unable to join match"**: check the IP address, make sure the host already created the match, and that both computers are on the same network.
- **Connection refused / timeout**: allow Python through the firewall on the host machine for TCP port `5000`.
- **"Unable to create match: address already in use"**: another program is using port `5000`; close it and try again.
