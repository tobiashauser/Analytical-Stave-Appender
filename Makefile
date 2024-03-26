shell:
	poetry shell
	poetry install
publish:
	poetry build
	poetry publish
clean:
	find . -name "*.pyc" | xargs rm -f
	find . -name "__pycache__" | xargs rm -rf
test:
	poetry run pytest
