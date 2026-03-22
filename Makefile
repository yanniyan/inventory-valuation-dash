new:
	@echo "Creating project: $(name)"
	mkdir -p $(name)
	cd $(name) && python3 -m venv .venv
	cd $(name) && . venv/bin/activate && pip install --upgrade pip
	cd $(name) && . venv/bin/activate && pip install jupyter ipykernel
	cd $(name) && . venv/bin/activate && python -m ipykernel install --user --name=$(name)
	cd $(name) && mkdir -p notebooks src data scripts .vscode
	echo '{ "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python" }' > $(name)/.vscode/settings.json
	code $(name)
run:
	. venv/bin/activate && python app/app.py

notebook:
	. venv/bin/activate && jupyter notebook

install:
	. venv/bin/activate && pip install -r requirements.txt

freeze:
	. venv/bin/activate && pip freeze > requirements.txt

clean:
	rm -rf .venv
	find . -type d -name "__pycache__" -exec rm -r {} +
