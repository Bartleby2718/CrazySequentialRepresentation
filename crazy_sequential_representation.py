import itertools
import re
import unittest

# TODO: Introduce prefix/postfix unary operators
PREFIX_UNARY_OPERATORS = '-',
POSTFIX_UNARY_OPERATORS = '!',
UNARY_OPERATORS = tuple(list(PREFIX_UNARY_OPERATORS) + list(POSTFIX_UNARY_OPERATORS))
BINARY_OPERATORS = (
    '+',
    '*',
    '^',
    # '-',  # TODO: Introduce subtraction
    # '/',  # TODO: Introduce division
    # '%',  # TODO: Introduce modulus
    # 'C',  # TODO: Introduce C
    # 'P',  # TODO: Introduce P
)
operators = tuple(list(UNARY_OPERATORS) + list(BINARY_OPERATORS))
EMPTY_STRING = ''
QUESTION_MARK = '?'
fillers = tuple([EMPTY_STRING] + list(operators))


def delimiters_to_re(delimiter):
    if delimiter == QUESTION_MARK or delimiter in '+*^':
        return '\\' + delimiter
    else:
        return delimiter


def wrap_with_parentheses(string):
    return '(' + string + ')'


def group_with_parentheses(delimited, delimiters):
    num_delimited = len(delimited)
    num_delimiters = len(delimiters)
    assert num_delimited == num_delimiters + 1, '{} != {}'.format(num_delimited, num_delimiters + 1)
    parenthesized = []
    # 1. do nothing
    original = interleave(delimited, delimiters)
    parenthesized += [original]
    # 2. wrap everything
    all_wrapped = wrap_with_parentheses(original)
    parenthesized += [all_wrapped]
    if num_delimiters != 1:
        # 3. others
        # how many? summation ((n+1 - i) * a_(n+1 - i) * a_i, i ) from 2 to n-1
        for i in range(2, num_delimited):
            # group i consecutive operands into one expression
            for j in range(num_delimited - i + 1):
                # group elements from index j to index j + i - 1
                # i elements from max(j) to n-1
                # n-1 - max(j) + 1 = i
                # max(j) = n - i
                grouped_expressions = group_with_parentheses(delimited[j:j + i], delimiters[j:j + i - 1])
                for group in grouped_expressions:
                    a, b = separate_delimiters(group)
                    for g in group_with_parentheses(a, b):
                        remaining_operands = delimited[:j] + [g] + delimited[j + i:]
                        remaining_operators = delimiters[:j] + delimiters[j + i - 1:]
                        final = group_with_parentheses(remaining_operands, remaining_operators)
                        parenthesized += final
    return parenthesized


def compress(expression_with_question_marks):
    count = expression_with_question_marks.count(QUESTION_MARK)
    options = EMPTY_STRING, QUESTION_MARK
    choices = itertools.product(options, repeat=count)
    delimited = separate_delimiters(expression_with_question_marks, delimiters=['?'])[0]
    compressed = [interleave(delimited, choice) for choice in choices]
    return compressed


def separate_delimiters(expression, delimiters=BINARY_OPERATORS):
    delimiters = [character for character in expression if character in delimiters]
    delimiters_in_re = [delimiters_to_re(delimiter) for delimiter in delimiters]
    delimited = re.split('|'.join(delimiters_in_re), expression)
    return delimited, delimiters


def interleave(delimited, delimiters):
    assert len(delimited) == len(delimiters) + 1, '{} != {}'.format(len(delimited), len(delimiters) + 1)
    operands_count = len(delimited)
    expression = EMPTY_STRING
    for i in range(operands_count - 1):
        expression += delimited[i] + delimiters[i]
    expression += delimited[-1]
    return expression


class TestCrazySequentialRepresentation(unittest.TestCase):
    def test_separate_delimiters(self):
        expression = '1*2+3^4+5'
        actual = separate_delimiters(expression)
        expected_delimited = ['1', '2', '3', '4', '5']
        expected_delimiters = ['*', '+', '^', '+']
        expected = expected_delimited, expected_delimiters
        self.assertEqual(expected, actual)

    def test_interleave(self):
        operands = ['1', '2', '3', '4', '5']
        operators = ['*', '+', '^', '+']
        expected = '1*2+3^4+5'
        actual = interleave(operands, operators)
        self.assertEqual(expected, actual)

    def test_compress(self):
        expression_with_question_marks = '1?2?3?4'
        expected = [expression_with_question_marks, '12?3?4', '1?23?4', '1?2?34', '123?4', '12?34', '1?234', '1234']
        actual = compress(expression_with_question_marks)
        self.assertEqual(set(expected), set(actual))

    def test_group_with_parentheses(self):
        delimited = ['1', '2', '3']
        delimiters = ['+', '*']
        actual = group_with_parentheses(delimited, delimiters)
        expected = [
            '1+2*3', '(1+2*3)',
            '(1+2)*3', '((1+2))*3', '((1+2)*3)', '(((1+2))*3)',
            '1+(2*3)', '1+((2*3))', '(1+(2*3))', '(1+((2*3)))',
        ]
        self.assertEqual(set(expected), set(actual))


if __name__ == '__main__':
    # unittest.main()
    result = []
    start = 1
    end = 5
    numbers_to_use = list(str(i) for i in range(start, end + 1))
    in_between = list('?' * (end - start))
    raw_expression = interleave(numbers_to_use, in_between)
    compressed_expressions = compress(raw_expression)
    for compressed in compressed_expressions:
        num_operators = sum(1 for character in compressed if character == QUESTION_MARK)
        choices_of_operators = itertools.product(BINARY_OPERATORS, repeat=num_operators)
        for choice in choices_of_operators:
            delimited = compressed.split(QUESTION_MARK)
            parenthesized_expressions = group_with_parentheses(delimited, choice)
            for parenthesized in parenthesized_expressions:
                parenthesized = parenthesized.replace('^', '**')
                # TODO: if the value is too big, pass
                value = eval(parenthesized)
                if value > 0 and value not in result:
                    print('{} = {}'.format(value, parenthesized))
                    result.append(value)
    print(result)

# 숫자와 숫자 사이 : nothing, +, * , ^
# a nothing b = 10*a + b
# expression 주변에는 ()
# binary operator = [+, *, ^]
# precedence: + < * < ^
# unary operation을 제외하면 expression이...
# (n - 1)! * a_n
# 1개 = a
# 2개 = a ? b
#           (a ? b)
# 3개 = a ? b ? c
#           (a ? b) ? c, a? (b ? c)
#           (a ? b ? c)
# 4개 = a ? b ? c ? d
#           (a ? b) ? c ? d, a ? (b ? c) ? d, a ? b ? (c ? d)
#           (a ? b ? c) ? d, a ? (b ? c ? d)
# a_n = 2 + summation (n+1 - k) * a_(n+1 - k) * a_k, k from 2 to n-1, k개를 하나의 expression으로 만드는 것
# a1 = 1
# a2 = 2
# a3 = 2 + 2a2a2 = 10
# 123456789
# 1?2?3?4?5?6?7?8?9
# delimit by binary operators
