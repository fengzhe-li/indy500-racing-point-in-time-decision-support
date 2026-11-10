.PHONY: figures portfolio-check test cpp-build cpp-test

figures:
	python3 scripts/generate_portfolio_figures.py
	python3 scripts/generate_v4_summary_figure.py

portfolio-check:
	python3 scripts/validate_portfolio.py

test:
	python3 -m unittest discover -s tests -p 'test_*.py'

cpp-build:
	cmake -S cpp -B cpp/build -DCMAKE_BUILD_TYPE=Release
	cmake --build cpp/build -j4

cpp-test: cpp-build
	ctest --test-dir cpp/build --output-on-failure -V
