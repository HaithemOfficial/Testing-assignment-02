# OrangeHRM End-to-End Automation Test

This project contains an automated end-to-end UI test for the [OrangeHRM Demo](https://opensource-demo.orangehrmlive.com) application using Selenium WebDriver with Python and pytest.

## Test Overview

The test automates the complete employee management workflow:

1. ✅ Login to OrangeHRM with admin credentials
2. ✅ Navigate to PIM → Add Employee
3. ✅ Add a new employee with first name, last name, and profile image
4. ✅ Enable Create Login Details and set credentials
5. ✅ Save the employee
6. ✅ Set job details (Joined Date, Job Title, Job Category, Location, Employment Status)
7. ✅ Add a supervisor (Odis Adalwin) in the Report-to section
8. ✅ Navigate to Employee List and apply filters
9. ✅ Verify the newly created employee appears in search results

## Features

- ✨ Uses explicit waits (no hardcoded sleep statements except where necessary)
- 🎯 Clear and maintainable XPath and CSS selectors
- ✅ Comprehensive assertions for validation
- 📝 Detailed comments explaining each step
- 🔧 Organized as pytest test functions with fixtures
- 🖼️ Profile image upload functionality
- 🔄 Unique employee data generation using timestamps
- 📊 Detailed console output for test progress

## Project Structure

```
task_02/
├── conftest.py                    # Pytest configuration and fixtures
├── test_orangehrm_e2e.py         # Main end-to-end test
├── requirements.txt               # Python dependencies
├── create_test_image.py          # Script to generate test profile image
├── test_data/
│   └── profile_image.png         # Sample profile image for upload
└── README.md                      # This file
```

## Prerequisites

- Python 3.8 or higher
- Chrome browser installed
- Internet connection

## Installation

1. **Clone or download this project**

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   This will install:
   - selenium (WebDriver for browser automation)
   - pytest (Testing framework)
   - pytest-html (HTML test reports)
   - webdriver-manager (Automatic ChromeDriver management)
   - Pillow (Image processing library)

## Running the Test

### Basic Test Execution

Run the test with verbose output:
```bash
pytest test_orangehrm_e2e.py -v -s
```

### Generate HTML Report

Run the test and generate an HTML report:
```bash
pytest test_orangehrm_e2e.py -v -s --html=report.html --self-contained-html
```

### Run in Headless Mode (Optional)

To run the test in headless mode, modify [conftest.py](conftest.py) and add this line in the `driver` fixture:
```python
chrome_options.add_argument("--headless")
```

## Test Execution Time

The complete test takes approximately **3-5 minutes** to execute, depending on network speed and system performance.

## Understanding the Test Output

The test provides detailed console output for each step:

```
=== Testing with Employee: John123456 Doe123456 ===
Step 1: Logging in to OrangeHRM...
✓ Login successful
Step 2: Navigating to Add Employee page...
✓ Add Employee page loaded
Step 3: Adding employee details...
  Generated Employee ID: 12345
Step 4: Uploading profile image...
✓ Profile image uploaded
...
✓ Employee 'John123456 Doe123456' found in search results

=== TEST PASSED ===
Employee 'John123456 Doe123456' successfully created and verified!
```

## Key Implementation Details

### Explicit Waits
The test uses `WebDriverWait` with expected conditions instead of `time.sleep()`:
```python
wait = WebDriverWait(driver, 20)
element = wait.until(EC.element_to_be_clickable((By.XPATH, "//button")))
```

### Unique Test Data
Each test run generates unique employee data using timestamps to avoid conflicts:
```python
timestamp = datetime.now().strftime("%H%M%S")
first_name = f"John{timestamp}"
last_name = f"Doe{timestamp}"
```

### Robust Selectors
The test uses a combination of XPath and CSS selectors for reliable element location:
- XPath: For text-based searches and complex hierarchies
- CSS: For simple class and attribute selections

### Error Handling
The test includes try-catch blocks for graceful handling of optional features like image upload.

## Troubleshooting

### ChromeDriver Issues
If you encounter ChromeDriver compatibility issues:
- The `webdriver-manager` package automatically handles ChromeDriver downloads
- Ensure Chrome browser is up to date
- Clear the WebDriver cache: `rm -rf ~/.wdm/`

### Timeout Errors
If elements take longer to load:
- Increase wait time in [test_orangehrm_e2e.py](test_orangehrm_e2e.py): `wait = WebDriverWait(driver, 30)`
- Check internet connection speed

### Element Not Found
If selectors fail:
- The OrangeHRM demo site may have updated their UI
- Use browser DevTools to inspect elements and update selectors
- Enable longer implicit wait in [conftest.py](conftest.py)

### Profile Image Upload Fails
If image upload doesn't work:
- Verify that `test_data/profile_image.png` exists
- Check file permissions
- The test will continue even if upload fails (warning message shown)

## Customization

### Change Login Credentials
Edit the `login_credentials` fixture in [conftest.py](conftest.py):
```python
@pytest.fixture(scope="session")
def login_credentials():
    return {
        "username": "YourUsername",
        "password": "YourPassword"
    }
```

### Modify Wait Times
Adjust wait times in [test_orangehrm_e2e.py](test_orangehrm_e2e.py):
```python
wait = WebDriverWait(driver, 30)  # Change from 20 to 30 seconds
```

### Use Different Browser
To use Firefox instead of Chrome, modify [conftest.py](conftest.py):
```python
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
```

## Test Assertions

The test includes the following assertions:
- ✅ Successful login verification
- ✅ Employee creation confirmation
- ✅ Job details save validation
- ✅ Supervisor addition verification
- ✅ Employee appears in filtered search results

## Best Practices Implemented

1. **Page Object Pattern Alternative**: While not using full POM, the test is well-organized with clear sections
2. **Explicit Waits**: Ensures reliability across different network speeds
3. **Unique Test Data**: Prevents test conflicts and allows parallel execution potential
4. **Comprehensive Logging**: Makes debugging easier
5. **Fixture-Based Configuration**: Easy to maintain and extend
6. **Error Recovery**: Graceful handling of optional features

## CI/CD Integration

To run this test in CI/CD pipelines, use headless mode:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    pytest test_orangehrm_e2e.py -v --html=report.html --self-contained-html
```

## License

This project is for educational and testing purposes.

## Author

Created as an automated testing demonstration for OrangeHRM.

---

**Note**: This test uses the public OrangeHRM demo site. The site resets periodically, so all test data is temporary.
