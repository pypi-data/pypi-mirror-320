import ast
from typing import Iterator


class DefaultMatchCaseVisitor(ast.NodeVisitor):
    error_message = 'SPM100 not raising when matching default value'

    def __init__(self) -> None:
        self.problems: list[tuple[int, int]] = []

    def visit_Match(self, node: ast.Match) -> None:
        for bad_node in _bad_nodes(node):
            self.problems.append(
                (
                    bad_node.lineno,  # type: ignore
                    bad_node.col_offset,  # type: ignore
                ),
            )
        self.generic_visit(node)


def _bad_nodes(node: ast.Match) -> Iterator[ast.AST]:
    for case in node.cases:
        if _empty_match_default(case) and (
            _last_statement_does_not_raise(case)
            or _return_preceds_exception_raising(case)
        ):
            yield _find_bad_node(case)


def _empty_match_default(case: ast.match_case) -> bool:
    pattern = case.pattern
    return isinstance(pattern, ast.MatchAs) and (
        pattern.pattern is None
        or (
            isinstance(pattern.pattern, ast.MatchAs)
            and pattern.pattern.pattern is None
        )
    )


def _last_statement_does_not_raise(case: ast.match_case) -> bool:
    return not isinstance(case.body[-1], ast.Raise)


def _return_preceds_exception_raising(
    case: ast.match_case,
) -> bool:
    return_idx = -1
    raise_idx = -1
    for idx, body in enumerate(case.body):
        if isinstance(body, ast.Return):
            return_idx = idx
        if isinstance(body, ast.Raise):
            raise_idx = idx
    return return_idx >= 0 and return_idx < raise_idx


def _find_bad_node(case) -> ast.AST:
    for body in case.body:
        # Handle special case when return preceds exception raising
        # In this case the bad node is that with the return statement
        if isinstance(body, ast.Return):
            return body
    return case.body[-1]
