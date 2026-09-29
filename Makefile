.PHONY: figures portfolio-check test

figures:
	python3 scripts/generate_portfolio_figures.py
	python3 scripts/generate_v4_summary_figure.py

portfolio-check:
	python3 scripts/validate_portfolio.py

test:
	python3 -m unittest discover -s tests -p 'test_*.py'
