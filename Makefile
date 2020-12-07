KOMI ?= 5.5
SIZE ?= 9

test:
	python -m unittest tests/*.py

play:
	python src/GoPlay.py 9

play5:
	python src/GoPlay.py 5 8.5

play_test:
	python src/GoPlay.py $(SIZE) $(KOMI)