# PyBen-Test
Alternative Testing Module

## PyBEN Tester
Tester application helping find and execute test files with an easy-to-use GUI

### Arguments:
    directory: Root directory of test files
    module: Locate test files in a python module instead of directory
    regex: Regex to match test files (default='**/test_*.py')
    prefix: python module to execute each test file with (default='pytest')
    args: Arguments to pass to each test file execution

### Execution function (easy to understand):
    
```python

for i in self.selected_files:
    main_args = [sys.executable, '-m'] + self.prefix.split() + [' ', i, ' '] + self.suffix.split()
    subprocess.run(main_args)
```
### Use cases:
Show ArgParser info:

    python -m pybentest.tester -h

Default: Find and execute pytest files under the current working directory:

    python -m pybentest.tester

Find and execute pytest files under a different directory:

    python -m pybentest.tester -d 

Find and execute pytest files under a specific python module (if the module has pytest files inside it):

    python -m pybentest.tester -m <module name>

You can also pass extra arguments like '--junitxml=utput.xml':

    python -m pybentest.tester -a --junitxml=utput.xml
    python -m pybentest.tester -a "--junitxml=utput.xml --alluredir=allure-results"