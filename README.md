# WayChess

![demo](img/demo/general_screen.png)

## Installation

There should be a Windows installer available, if you don't use Windows, install from scratch.

### Binary From Scratch

```
git clone https://github.com/r2dev2bb8/WayChess.git
cd WayChess
make
```

### Linux

You may need to install the following extra dependencies

```
sudo apt install mercurial python3-dev libjpeg-dev libportmidi-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsdl1.2-dev libsmpeg-dev libx11-dev libavformat-dev libswscale-dev python3-tk
chmod +x cleartype-install-linux.bash
./cleartype-install-linux.bash
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
| ``ctrl+e`` | Configure engine |
| ``o``      | Load a pgn       |
| ``x``      | Toggle explorer  |
| ``q``      | Quit application |


## Tests
```
make test
```


## Goals

  - [x] Open source chess gui
  - [ ] Fully-featured
      - [x] Comments
      - [ ] Variations
      - [ ] Annotations
      - [ ] Engine matches
      - [x] Engine options
  - [ ] Easy to install
  - [ ] Fluid design
  - [x] Cross-platform
  - [ ] Ease of use
  - [x] Modularity
  - [x] Database

## Progress

Navigation is controlled by keybindings instead of button right now. Comments, variations, and annotations have yet to be added. The chess.com database explorer (doesn't need to login) and the engine have been stably implemented. School and CollegeBoard tests are ramping up for me so I can't work on this for much time as of now.

