import ast
from textwrap import dedent

from flake8_spm import Plugin


def _results(s: str) -> set[str]:
    tree = ast.parse(s)
    plugin = Plugin(tree)
    print(ast.dump(tree, indent=4))
    return {f'{line}:{col} {msg}' for line, col, msg, _ in plugin.run()}


def test_EmptyFile_OK():
    assert _results('') == set()


def test_OneDummyFunctionWithoutPatternMatching_OK():
    content = dedent(
        """\
      def func(a, b):
          return a, b
      """
    )
    assert _results(content) == set()


def test_MatchScalar_RaisingOnDefault_OK():
    content = dedent(
        """\
        match value:
          case 1:
            return 'One'
          case _:
            raise ValueError('Unexpected value')
        """
    )
    assert _results(content) == set()


def test_MatchScalar_ReturningOnDefault_Error():
    content = dedent(
        """\
        match value:
          case 1:
            return 'One'
          case _:
            return 'Default'
        """
    )
    assert _results(content) == set(
        {'5:4 SPM100 not raising when matching default value'}
    )


def test_MatchScalarInsideFunction_RaisingOnDefault_OK():
    content = dedent(
        """\
        def func(value):
          match value:
            case 1:
              return 'One'
            case _:
              raise ValueError('Unexpected value')
        """
    )
    assert _results(content) == set()


def test_MatchScalarInsideFunction_ReturningOnDefault_Error():
    content = dedent(
        """\
        def func(value):
          match value:
            case 1:
              return 'One'
            case _:
              return 'Default'
        """
    )
    assert _results(content) == set(
        {'6:6 SPM100 not raising when matching default value'}
    )


def test_MatchSubpatternScalar_ReturningOnDefault_Error():
    content = dedent(
        """\
        match value:
          case 1:
            return 'One'
          case _ as default:
            return 'Default'
        """
    )
    assert _results(content) == set(
        {'5:4 SPM100 not raising when matching default value'}
    )


def test_MatchSubpatternListElement_RaisingOnDefault_OK():
    content = dedent(
        """\
        match value:
          case [1] as y:
            return 'Subpattern match'
          case _:
            raise ValueError('Unexpected value')
        """
    )
    assert _results(content) == set()


def test_MatchScalar_PrintingOnDefault_Error():
    content = dedent(
        """\
        match value:
          case 1:
            print('One')
          case _:
            print('Default')
        """
    )
    assert _results(content) == set(
        {'5:4 SPM100 not raising when matching default value'}
    )


def test_MatchListElement_ReturningOnDefault_Error():
    content = dedent(
        """\
        match value:
          case [1]:
            return 'One'
          case _:
            return 'Default'
        """
    )
    assert _results(content) == set(
        {'5:4 SPM100 not raising when matching default value'}
    )


def test_MatchDictValues_ReturningOnDefault_Error():
    content = dedent(
        """\
        match value:
          case {'a': _, 'b': _}:
            return 'A and B from dict'
          case _:
            return 'Default'
        """
    )
    assert _results(content) == set(
        {'5:4 SPM100 not raising when matching default value'}
    )


def test_MatchDictValues_RasingOnDefault_OK():
    content = dedent(
        """\
        match value:
          case {'a': _, 'b': _}:
            return 'A and B from dict'
          case _:
            raise ValueError('Unexpected value')
        """
    )
    assert _results(content) == set()


def test_MatchMultiplePatterns_RaiseOnDefault_OK():
    content = dedent(
        """\
        match value:
          case 1:
            return 'Scalar'
          case 'value':
            return 'Literal value'
          case [1]:
            return 'Element from list'
          case {'a': _, 'b': _}:
            return 'A and B from dict'
          case _:
            raise ValueError('Unexpected value to match')
        """
    )
    assert _results(content) == set()


def test_MatchMultiplePatterns_ReturningOnDefault_Error():
    content = dedent(
        """\
        match value:
          case 1:
            return 'Scalar'
          case 'value':
            return 'Literal value'
          case [1]:
            return 'Element from list'
          case {'a': _, 'b': _}:
            return 'A and B from dict'
          case _:
            return 'Default'
        """
    )
    assert _results(content) == set(
        {'11:4 SPM100 not raising when matching default value'}
    )


def test_MatchScalar_ReturningAndThenRaisingOnDefault_Error():
    content = dedent(
        """\
        match value:
          case 1:
            return 'One'
          case _:
            return 'Default'
            raise ValueError('Unexpected pattern')
        """
    )
    assert _results(content) == set(
        {'5:4 SPM100 not raising when matching default value'}
    )


def test_MatchScalar_RaisingOnDefaultFollowedByComment_OK():
    content = dedent(
        """\
        match value:
          case 1:
            return 'One'
          case _:
            raise ValueError('Unexpected pattern')
            # some comment
        """
    )
    assert _results(content) == set()
