# ♟️ Chess Gaming Platform

### 📊 About

**Chess gaming platform** has been developed with the following features:

- **All rules implemented**, including _castling_, _en passant_, _pawn promotion_, _check_, _checkmate_, and
  **highlighting of possible moves**.
- **A user-friendly interface** with _draggable pieces_, _customizable textures_, _clickable player clocks_, and
  _a move list (history)_.
- **Keyboard control** supported by _a custom SAN notation parser_.
- **Saving and loading capabilities** for _game history_ and _configuration_, including initial game settings and
  textures.
- Ability to **play against a bot** or **connect with another player over a network**.

> **Environment:** PyCharm 2023.1 (Professional Edition) | Python 3.10.9 (WinPython 3.10 Release 2022-04).
> **Naming convention**: camelCase (to ensure consistency with Qt methods).

#### Main Window

<img src="data/_readme-img/1.png?raw=true" width="500" alt="Main Window">

#### New Game Configuration Window

<img src="data/_readme-img/2.png?raw=true" width="200" alt="Start Window">

#### Game Modes

|     Mode      |                                                                                                                                                                          Description                                                                                                                                                                           |
|:-------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| **1 player**  |                                                                                                                                            One user can play with himself or two users can play using one computer.                                                                                                                                            |
| **2 players** | Two users can engage in a game on separate computers by _connecting to the same network_. The first user initiates server by entering their computer's IP address (_IPv4 or IPv6_) and port, and is assigned the white pieces. The second user can then join the game by entering the same IP address and port number, taking on the role of the black pieces. |
|    **AI**     |                                                                                                                                Playing against a bot, which utilizes _minimax alpha-beta pruning algorithm_ with a depth of 3.                                                                                                                                 |

### 🎮 Gameplay

#### Making a Move

To make a move, **left-click and hold** the desired piece, which will then _highlight possible moves_. If piece is not
placed on a valid square, it will return to its original position. To complete the move, **click on the corresponding
player clock**. Note that you cannot finish a move without moving the selected piece to a valid position.

<img src="data/_readme-img/3.png?raw=true" width="500" alt="Move">

#### Keyboard Control

The **Input | Player №X** text field supports **Short Algebraic Notation (SAN)** for chess moves (based on:
[Wiki](https://en.wikipedia.org/wiki/Algebraic_notation_(chess))). Since it is unnecessary to include `+`, `#`, `e.p.`
in this field, they have not been implemented (they are automatically added to history block).
Example moves are: `e3`, `Nc6`, `Qh4e1` (if ambiguity), `O-O` (castling), `exd5` (capture), `e8=Q` (promotion).
Press `Enter` and click clock to confirm the move.

#### Special Movements: En passant | Castling | Pawn promotion

In the case of en passant captures and castling, _additional squares will be highlighted_ during the pawn and
king moves. When a pawn reaches the end of the chessboard, _promotion window will appear_, allowing the player to choose
a new piece.

<img src="data/_readme-img/4.png?raw=true" width="500" alt="Promotion Window">

#### Check | Checkmate

When the king is in check, _the square beneath it will be highlighted in red_. The checked king can only make moves to
escape the threat.

<img src="data/_readme-img/5.png?raw=true" width="500" alt="Check">

If checkmate occurs, _game over message will be displayed_, the clocks will be stopped, and
further moves will be disabled.

<img src="data/_readme-img/6.png?raw=true" width="200" alt="Checkmate">

### 🕹 Additional Features

#### Change textures

Players have option to **change the textures of the chessboard and pieces** by right-clicking. If one player attempts to
change their piece color to the same as their opponent have - an appropriate message will be displayed. **Note**:
Texture changes will be reset upon selecting "Game → Start new game."

<img src="data/_readme-img/7.png?raw=true" width="500" alt="Textures">

#### Write and load configurations to/from JSON

During gameplay, players have the ability to **save configuration settings** (_textures, time, mode, and network
parameters_) to a **JSON** file, as well as load board and piece textures. Before starting a game, players can **load**
all configurations (not just textures) in "New Game" window.

**Example of JSON file**

```json
{
  "style": {
    "board": {
      "boardStyle": "rock"
    },
    "pieces": {
      "lightSideStyle": "light",
      "darkSideStyle": "blue"
    }
  },
  "initial": {
    "time": {
      "hour": 0,
      "minute": 15,
      "second": 30
    },
    "mode": "1 player",
    "network": {
      "ip": "127.0.0.0",
      "port": "5000"
    }
  }
}
```

#### Write and playback history to/from XML or SQLite database

During gameplay, players can **save the game history**, including move completion times, to **XML** file or **SQLite**
database. In the "New Game" window, players have the option to **load** the game history and initiate **playback**, 
either by manually advancing through moves or enabling auto playback to watch the game progress.

<img src="data/_readme-img/8.png?raw=true" width="500" alt="Playback">
