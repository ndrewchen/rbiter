from sympy import *
from sympy.parsing.latex import parse_latex
import re
import signal
from contextlib import contextmanager


class TimeoutException(Exception): pass


@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Evaluation timed out")

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


def evaluate_latex(exp, mode='numeric', maxn=100):
    """
    Evaluates latex according to the mode

    :param string exp: latex string of an expression
    :param string mode: mode to evaluate exp in
        - numeric = evaluate exp to a number
        - symbolic = evaluate exp to the most simplified form
    :param int maxn: number of digits of precision to use during numerical evaluation
    :return: Numerical evaluation of expression (if possible) or most simplified sympy expression
    """
    if mode == 'numeric':
        try:
            sympy_exp = parse_latex(exp)
            return N(sympy_exp, maxn)
        except Exception as e:
            raise RuntimeError('Failed to numerically evaluate expression.') from e
    elif mode == 'symbolic':
        try:
            sympy_exp = parse_latex(exp)
            return sympy_exp
        except Exception as e:
            raise RuntimeError('Failed to symbolically simplify.') from e
    else:
        raise LookupError('Invalid mode "' + mode + '". ')


def comp_exp_latex(exp1, exp2, mode='numeric', maxn=100, suspicious_threshold=6, numeric_threshold=0):
    """
    Compares a sympy expression to a latex string

    :param string exp1: sympy expression
    :param string exp2: latex string of second expression
    :param string mode: mode to evaluate expressions in
        - numeric = evaluate exp to a number
        - symbolic = evaluate exp to the most simplified form
    :param int maxn: number of digits of precision to use during numerical evaluation
    :param int suspicious_threshold: number of consecutive digits necessary to mark as suspicious
    :param float numeric_threshold: inclusive threshold for grading two numerically-evaluated expressions as equivalent
    :return:
        - 0 = not equivalent
        - 0.1 = not equivalent and exp2 is suspicious
        - 1 = equivalent
        - 1.1 = equivalent and exp2 is suspicious (IE too many decimals to have been calculated by hand)
    """

    # mark suspicious if there exists a number in the latex with length >= suspicious_threshold
    suspicious = len(max(re.split(r'\D+', exp2), key=len)) >= suspicious_threshold
    if mode == 'numeric':
        try:
            sympy_exp = evaluate_latex(exp2, mode='numeric', maxn=maxn)
            equiv = Abs(sympy_exp - exp1) <= numeric_threshold
            if equiv:
                return 1.1 if suspicious else float(1)
            else:
                return 0.1 if suspicious else float(0)
        except Exception as e:
            raise RuntimeError('Failed to numerically compare expressions.') from e
    elif mode == 'symbolic':
        try:
            sympy_exp = evaluate_latex(exp2, mode='symbolic')
            equiv = (simplify(sympy_exp - exp1) == 0)
            if equiv:
                return 1.1 if suspicious else float(1)
            else:
                return 0.1 if suspicious else float(0)
        except Exception as e:
            raise RuntimeError('Failed to symbolically compare expressions.') from e
    else:
        raise LookupError('Invalid mode "' + mode + '". ')
    # parse latex to sympy, evaluate sympy, compare results


def comp_exp_list(exp, exp_list, mode='numeric', exec_limit=1, maxn=100, suspicious_threshold=6, numeric_threshold=0):
    """
    Compares an expression to a list of expressions

    :param string exp: latex string of expression to compare to all expressions in exp_list. THIS SHOULD BE THE CORRECT
        ANSWER
    :param List[string] exp_list: list of latex strings of expressions to compare to exp
    :param string mode:
        - numeric = evaluate expressions to a number
        - symbolic = evaluate expressions in symbolic form
    :param int exec_limit: limit of execution time per expression evaluation in seconds
    :param int maxn: number of digits of precision to use during evaluation
    :param int suspicious_threshold: number of consecutive digits necessary to mark as suspicious
    :param float numeric_threshold: inclusive threshold for marking two numerically-evaluated expressions as equivalent
    :return:
        - 0 = not equivalent
        - 0.1 = not equivalent and exp2 is suspicious
        - 1 = equivalent
        - 1.1 = equivalent and exp2 is suspicious (IE too many decimals to have been calculated by hand)
        - 2 = took too long to evaluate
        - 3 = other
    """
    if mode != 'numeric' and mode != 'symbolic':
        raise RuntimeError('Invalid mode')

    correct_exp = evaluate_latex(exp)
    out = []
    for exp1 in exp_list:
        if len(exp1) == 0:
            out.append(0)
            continue
        try:
            with time_limit(1):
                if mode == 'numeric':
                    out.append(comp_exp_latex(correct_exp, exp1, mode='numeric', maxn=maxn,
                                              suspicious_threshold=suspicious_threshold,
                                              numeric_threshold=numeric_threshold))
                elif mode == 'symbolic':
                    out.append(comp_exp_latex(correct_exp, exp1, mode='symbolic',
                                              suspicious_threshold=suspicious_threshold))
        except TimeoutException:
            out.append(float(2))
        except Exception:
            out.append(float(3))
    return out


def grade_column(sheet, sheet_id, correct, column, destination, mode='numeric', exec_limit=1, maxn=100,
                 suspicious_threshold=6, numeric_threshold=0):
    """
    Grades a column of latex answers by comparing them to the correct answer. ENSURE COLUMN AND DESTINATION DOES NOT
    INCLUDE LABELS

    :param sheet: Google spreadsheets object
    :param sheet_id: the sheet id
    :param string correct: latex string of correct answer
    :param column: A1 notation of column to grade (see
        https://developers.google.com/sheets/api/guides/concepts#expandable-1)
    :param destination: A1 notation of column to output graded results to (see
        https://developers.google.com/sheets/api/guides/concepts#expandable-1)
    :param string mode:
        - numeric = evaluate expressions to a number
        - symbolic = evaluate expressions in symbolic form
    :param int exec_limit: limit of execution time per expression evaluation in seconds
    :param int maxn: number of digits of precision to use during evaluation
    :param int suspicious_threshold: number of consecutive digits necessary to mark as suspicious
    :param float numeric_threshold: inclusive threshold for marking two numerically-evaluated expressions as equivalent
    :return: None
    """
    result = sheet.values().get(spreadsheetId=sheet_id,
                                     range=column).execute()
    raw_values = result.get('values', [])
    values = []
    for lst in raw_values:
        if len(lst) == 0:
            values.append('')
        else:
            values.append(lst[0])
    graded_result = comp_exp_list(correct, values, mode=mode, exec_limit=exec_limit, maxn=maxn, suspicious_threshold=suspicious_threshold, numeric_threshold=numeric_threshold)
    body = {
        'values': [[ele] for ele in graded_result]
    }
    sheet.values().update(
        spreadsheetId=sheet_id, range=destination,
        valueInputOption='RAW', body=body).execute()


if __name__ == "__main__":
    # tests
    teststr1 = '\\frac{88}{379}'
    teststr2 = '\\frac{\left(10\\binom{66}{23}\\right)}{\left(25\\binom{66}{22}+30\\binom{66}{23}\\right)}'

    # evaluate_latex
    print(evaluate_latex(teststr1))
    print(evaluate_latex(teststr2))

    # comp_exp_latex
    print(comp_exp_latex(evaluate_latex(teststr2), teststr1))

    # comp_exp_list
    teststrlist = ['\\frac{2}{11}',
                   '\\frac{27}{106}',
                   '\\frac{35200}{151600}',
                   '\\frac{1}{3}',
                   '\\frac{10\cdot\\binom{66}{23}}{25\cdot\\binom{66}{22}+30\cdot\\binom{66}{23}}']
    # expecting [0, 0, 1.1, 0, 1]
    print(comp_exp_list(teststr1, teststrlist))