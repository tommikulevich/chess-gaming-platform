# ♟️ Chess Gaming Platform

### 📊 About

Fully implemented **chess gaming platform** has been developed, complete with a fully functional implementation of the
rules such as castling, en passant, pawn promotion, check, checkmate, and the highlighting of possible moves. The user
interface features draggable pieces and customizable textures, as well as clickable player clocks, a move list (history), 
and keyboard control through a custom SAN notation parser. Additionally, application allows for the saving and loading 
of game history and configuration, which includes initial game settings and textures. Players can also test their skills 
by playing against a bot or connecting with another player over a network.

> This application is written in **Python 3.10.9**, using the Qt Framework (PySide2), in PyCharm 2023.1 (Professional
> Edition).

#### Main Window 

<img src="data/_readme-img/1.png?raw=true" width="500" alt="Main Window">

#### New Game Configuration Window

<img src="data/_readme-img/2.png?raw=true" width="200" alt="Start Window">

#### Game Modes

- **1 player** - ...
- **2 players** - ...
- **AI** - ...

### 🎮 Gameplay

#### Making a Move

...

<img src="data/_readme-img/3.png?raw=true" width="500" alt="Move">

#### Keyboard Control

...

#### Special Movements: Pawn promotion | En passant | Castling

...

<img src="data/_readme-img/4.png?raw=true" width="500" alt="Promotion Window">

#### Check | Checkmate

...

<img src="data/_readme-img/5.png?raw=true" width="500" alt="Check">

<img src="data/_readme-img/6.png?raw=true" width="200" alt="Checkmate">


### 🕹 Additional Features

#### Change textures

...

<img src="data/_readme-img/7.png?raw=true" alt="Textures">

#### Write and load configurations to/from JSON

... (load config in start window or load styles during game)

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

...

<img src="data/_readme-img/8.png?raw=true" alt="Playback">
