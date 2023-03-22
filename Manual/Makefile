#!/bin/bash
all:man.tex
	mkpdflatex man 
	mv man.pdf view.pdf
	printf "\033[1;32mSUCESS \033[0m "

auto:
	echo "man.tex" | entr -c make all 
	

