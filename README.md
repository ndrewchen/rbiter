# rbiter
Rbiter (Arbiter) is a wrapper of [Sympy](https://www.sympy.org/en/index.html)'s expression evaluator intended to be used for automatic grading of CMIMC Math Contest submissions.

The intended workflow is:
1. Submissions are imported from a google spreadsheet
2. Submissions are evaluated for correctness
3. Graded results are reuploaded to a different column in the google spreadsheet

## Prerequisites
To run this project, you need:
1. Python 3.7
2. [pip](https://pypi.org/project/pip/) package installer
3. A Google Cloud project with the API enabled (refer to [this](https://developers.google.com/workspace/guides/create-project))
   1. Add the `https://www.googleapis.com/auth/drive.file` scope to the OAuth consent screen
4. Auth credentials for a desktop app on Google Cloud (refer to [this](https://developers.google.com/workspace/guides/create-credentials))
5. A Google account
   1. Add this Google account to the Google Cloud project's allowed testers

## Installation
1. Clone this repository into a python 3.7 <strong>conda</strong> environment
2. Run `pip install -r requirements.txt`
3. Move the json credentials file generated in step 4 of the prerequisites into the rbiter root directory and rename it to `credentials.json`
4. Run `main.py`. A login window will appear, and you need to login to a Google account that has read and write access to the sheet with the submissions

## Grading setup
1. Get the sheet id of your google spreadsheet from its url and replace the given id in `main.py`(for example, in `https://docs.google.com/spreadsheets/d/aaaaaaaaaaaaaaa/edit` the id is `aaaaaaaaaaaaaaa`)
2. For each column to grade, call `grade_column()` with the appropriate parameters (documentation below). The submissions will be automatically graded and the results will be printed accordingly on the spreadsheet. 

Example code:
```python
sheet_id = 'YOUR SHEET ID HERE'

# DO NOT MODIFY
creds = get_credentials()
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

# test
correct = 'CORRECT LATEX EXPRESSION'
grade_column(sheet, sheet_id, correct, 'Sheet!A1:A2', 'Sheet!B1:B2') # A1 notation
```
This takes all entries on the sheet with id `sheet_id` from the range `Sheet!A1:A2`, compares them to `correct`, and outputs the graded results onto the range `Sheet!B1:B2`.

## Documentation

### `evaluate_latex()`
Evaluates a latex string into a sympy expression

Required parameters:
- `exp` (string): latex string of an expression

Optional parameters:
- `mode` (string)(default = `numeric`): mode of sympy evaluation to use. Available modes:
  - `numeric`: evaluate `exp` to a number
  - `symbolic`: evaluate `exp` to a symbol
- `maxn` (int)(default = `100`): number of digits of precision to use during numerical evaluation

Returns:
- sympy expression containing evaluated latex


### `comp_exp_latex()`
Compares a sympy expression to a latex string

Required parameters:
- `exp1` : sympy expression. Note it is not a latex string so a latex answer key only needs to be ran through `evaluate_latex()` once before being compared to all submissions.
- `exp2` (string): latex string of an expression

Optional parameters:
- `mode` (string)(default = `numeric`): mode of sympy evaluation to use. Available modes:
  - `numeric`: evaluate `exp` to a number
  - `symbolic`: evaluate `exp` to a symbol
- `maxn` (int)(default = `100`): number of digits of precision to use during numerical evaluation
- `suspicious_threshold` (int)(default = `6`): inclusive threshold for number of consecutive digits necessary to mark as suspicious (IE if it's 6 the number 123456 is suspicious but 12345 is not). Note you can suppress suspicion by flooring the output.
- `numeric_threshold` (float)(default = `0`): inclusive threshold for grading two numerically-evaluated expressions as equivalent (IE |a-b| <= numerical_threshold means a and b are considered equivalent). Note this is unused during symbolic evaluation. 

Returns:
- (float) number representing the result of the comparison:
  - `0` : not equivalent
  - `0.1` : not equivalent and exp2 is suspicious
  - `1` : equivalent
  - `1.1` : equivalent and exp2 is suspicious
  
### `comp_exp_list()`
Compares a latex expression to a list of latex expressions

Required parameters:
- `exp` (string): latex string of an expression to compare to all expressions in `exp_list`. THIS SHOULD BE THE CORRECT ANSWER!!
- `exp_list` (List[string]): list of latex strings of expressions to compare to `exp`

Optional parameters:
- `mode` (string)(default = `numeric`): mode of sympy evaluation to use. Available modes:
  - `numeric`: evaluate `exp` to a number
  - `symbolic`: evaluate `exp` to a symbol
- `exec_limit` (int)(default = `1`): limit of execution time per expression evaluation in seconds
- `maxn` (int)(default = `100`): number of digits of precision to use during numerical evaluation
- `suspicious_threshold` (int)(default = `6`): inclusive threshold for number of consecutive digits necessary to mark as suspicious (IE if it's 6 the number 123456 is suspicious but 12345 is not). Note you can suppress suspicion by flooring the output.
- `numeric_threshold` (float)(default = `0`): inclusive threshold for grading two numerically-evaluated expressions as equivalent (IE |a-b| <= numerical_threshold means a and b are considered equivalent). Note this is unused during symbolic evaluation. 

Returns:
- (List[float]) list containing floats representing the results of comparisons between `exp` and corresponding expressions in `exp_list`:
  - `0` : not equivalent
  - `0.1` : not equivalent and exp2 is suspicious
  - `1` : equivalent
  - `1.1` : equivalent and exp2 is suspicious
  - `2` : took too long to evaluate
  - `3` : other
  
### `grade_column()`
Grades a column of latex answers by comparing them to the correct answer, and outputs the results onto the provided sheet. ENSURE COLUMN AND DESTINATION ARE THE SAME SIZE AND DOES NOT
INCLUDE LABELS

Required parameters:
- `sheet` : Google spreadsheets object generated in `main.py`
- `sheet_id` (string) : the sheet id
- `correct` (string) : latex string of the correct answer
- `column` (string) : A1 notation of column to grade (see https://developers.google.com/sheets/api/guides/concepts#expandable-1)
- `destination` (string) : A1 notation of column to output graded results to (see https://developers.google.com/sheets/api/guides/concepts#expandable-1)

Optional parameters:
- `mode` (string)(default = `numeric`): mode of sympy evaluation to use. Available modes:
  - `numeric`: evaluate `exp` to a number
  - `symbolic`: evaluate `exp` to a symbol
- `exec_limit` (int)(default = `1`): limit of execution time per expression evaluation in seconds
- `maxn` (int)(default = `100`): number of digits of precision to use during numerical evaluation
- `suspicious_threshold` (int)(default = `6`): inclusive threshold for number of consecutive digits necessary to mark as suspicious (IE if it's 6 the number 123456 is suspicious but 12345 is not). Note you can suppress suspicion by flooring the output.
- `numeric_threshold` (float)(default = `0`): inclusive threshold for grading two numerically-evaluated expressions as equivalent (IE |a-b| <= numerical_threshold means a and b are considered equivalent). Note this is unused during symbolic evaluation. 

Returns:
- None
