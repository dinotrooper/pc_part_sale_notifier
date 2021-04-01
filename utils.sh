#!/bin/bash

venv-create() {
	python3 -m virtualenv env
}

venv-activate() {
	source env/bin/activate
}

tools-install() {
	python3 -m pip install pycodestyle
	python3 -m pip install pylint
	python3 -m pip install autopep8	
}

test() {
	pip install --force-reinstall -e .
	pytest --showlocals
}

pep8-auto-format() {
	cd pc_part_sale_notifier/
	files="$(ls)"
	for file in $files
	do
		if [[ ! -d $file ]]; then
			autopep8 --in-place --aggressive --aggressive $file
		fi
	done
	cd ../test
	files="$(ls)"
	for file in $files
	do
		if [[ ! -d $file ]]; then
			autopep8 --in-place --aggressive --aggressive $file
		fi
	done
	cd ..
}

pep8-check() {
	cd pc_part_sale_notifier/
	files="$(ls)"
	for file in $files
	do
		if [[ ! -d $file ]]; then
			pylint --rcfile=../pylint.config $file
			pycodestyle $file
		fi
	done
	cd ../test
	files="$(ls)"
	for file in $files
	do
		if [[ ! -d $file ]]; then
			pylint --rcfile=../pylint.config $file
			pycodestyle $file
		fi
	done
	cd ..
}

