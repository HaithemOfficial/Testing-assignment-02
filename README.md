# Test suite

Minimal instructions to run the test suite locally (Windows PowerShell).

1) Create and activate a Python virtual environment

```powershell
python -m venv .venv
& .venv\Scripts\Activate.ps1
```

2) Install test dependencies

If you have a `requirements.txt` at project root, run:

```powershell
pip install -r requirements.txt
```

Otherwise install the minimal packages used by these tests:

```powershell
pip install pytest selenium webdriver-manager
```

3) Run all tests sequentially

From the repository root run:

```powershell
python tests/run_all_tests.py
```

This script runs the test files in order, stopping on the first failure and printing a per-test summary.

4) Run a single test file

From the `tests` folder you can run a single file with pytest, for example:

```powershell
pytest test_e2e_employee.py -vv --disable-warnings
```

5) Headless mode

To run tests in headless mode (no browser windows), set the `HEADLESS` environment variable before running.

```powershell
$env:HEADLESS = '1'
python tests/run_all_tests.py
```

If you need a CI workflow or a different README format, tell me what you prefer.