import subprocess
import sys
import os

TESTS = [
    "test_e2e_employee.py",
    "test_personal_details.py",
    "test_recruitment_add_candidate.py",
    "test_buzz_post.py",
    "test_pim_report.py",
]

def run_tests():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(base_dir, "..", ".venv", "Scripts", "python.exe")
    if not os.path.exists(venv_python):
        venv_python = sys.executable  # fallback to current python
    for test in TESTS:
        print(f"\n==== Running {test} ====")
        result = subprocess.run([
            venv_python, "-m", "pytest", test, "-vv", "--disable-warnings"
        ], cwd=base_dir)
        if result.returncode != 0:
            print(f"FAILED: {test} (exit code {result.returncode})")
            sys.exit(result.returncode)
        print(f"PASSED: {test}")
    print("\nAll tests completed successfully.")

if __name__ == "__main__":
    run_tests()
