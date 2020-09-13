py = python3
# cc := ${py} -m nuitka --follow-imports --standalone --remove-output --plugin-enable=multiprocessing --plugin-enable=numpy --show-progress 
cc := ${py} -m PyInstaller

pgg = dist/gui/pygame_gui
data = ${pgg}/data
pggdatacdn = https://raw.githubusercontent.com/MyreMylar/pygame_gui/main/pygame_gui/data

all: init build data

.PHONY: init build data test clean

init:
	$(py) -m pip install pyinstaller pytest
	$(py) -m pip install -r requirements.txt

build:
	$(cc) --onedir -y -w --noupx -i img/favicon.ico gui.spec
	$(cc) --onefile --noupx installer.py

data:
	- rm -r $(pgg)
	mkdir $(pgg)
	mkdir $(data)
	curl -s -o $(data)/default_theme.json $(pggdatacdn)/default_theme.json
	curl -s -o $(data)/FiraCode-Bold.ttf $(pggdatacdn)/FiraCode-Bold.ttf
	curl -s -o $(data)/FiraCode-Regular.ttf $(pggdatacdn)/FiraCode-Regular.ttf
	curl -s -o $(data)/FiraMono-BoldItalic.ttf $(pggdatacdn)/FiraMono-BoldItalic.ttf
	curl -s -o $(data)/FiraMono-RegularItalic.ttf $(pggdatacdn)/FiraMono-RegularItalic.ttf

test:
	$(py) -m pytest tests/

clean:
	rm -rf dist/ build/
