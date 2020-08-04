py = python3
# cc := ${py} -m nuitka --follow-imports --standalone --remove-output --plugin-enable=multiprocessing --plugin-enable=numpy --show-progress 
cc := ${py} -m PyInstaller

all: init build

init:
	$(py) -m pip install pyinstaller pytest
	$(py) -m pip install -r requirements.txt

build:
	$(cc) --onedir -y -w --noupx -i img/favicon.ico gui.spec
	$(cc) --onefile --noupx installer.py

test:
	$(py) -m pytest tests/

clean:
	rm -rf dist/ build/
