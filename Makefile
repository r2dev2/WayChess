py = python3
cc := ${py} -m nuitka --follow-imports --standalone --remove-output --plugin-enable=multiprocessing --plugin-enable=numpy --show-progress 

all: init build

init:
	$(py) -m pip install nuitka
	$(py) -m pip install -r requirements.txt

build: init
	$(cc) gui.py
	$(cc) installer.py

clean: *.dist *.build
	rm -rf *.dist *.build
