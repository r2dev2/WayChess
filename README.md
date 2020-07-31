# WayChess

![demo](img/demo/general_screen.png)

## Installation

There should be a Windows installer available, if you don't use Windows, install from scratch.

### From Scratch

```
git clone https://github.com/r2dev2bb8/WayChess.git
cd WayChess
python3 -m pip install -r requirements.txt
python3 installer.py
python3 gui.py
```

## Usage

Keybindings:

|    Key     |     Function     |
| ---------- | ---------------- |
| ``<-``     | Move back        |
| ``->``     | Move forward     |
| ``f``      | Flip board       |
| ``s``      | Save database    |
| ``ctrl+n`` | Create game      |
| ``n``      | Next game        |
| ``b``      | Previous game    |
| ``e``      | Toggle engine    |
| ``o``      | Load a pgn       |
| ``x``      | Toggle explorer  |
| ``q``      | Quit application |



## Goals

  - [x] Open source chess gui
  - [ ] Fully-featured (comments, variations, annotations, etc.)
  - [ ] Easy to install
  - [ ] Fluid design
  - [x] Cross-platform
  - [ ] Ease of use
  - [x] Modularity
  - [x] Database

## Progress

Navigation is controlled by keybindings instead of button right now. Comments, variations, and annotations have yet to be added. The chess.com database explorer (doesn't need to login) and the engine have been somewhat stably implemented.

