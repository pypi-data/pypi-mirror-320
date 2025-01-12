import ast


class _DowngradeAnnAssign(ast.NodeTransformer):
	"""Converts AnnAssign nodes (annotated assignment) to simpler Assign nodes."""

	def visit_AnnAssign(self, node: ast.AnnAssign) -> ast.Assign | None:
		if node.value is not None:
			return ast.Assign(targets = [node.target], value = node.value)
		return None  # just so mypy can leave me alone


def remove_types_ast(path: str, *, return_str: bool = False, output_file_path: str = 'output.py') -> None | str:
	"""
		Strips the types declared in the file at **path**
		Either one of return_str or output_file_path must be set
		:param path: Required parameter deciding what file to strip from types
		:param return_str: dictates if the function returns a str; can be mixed with output_file_path param
		:param output_file_path: dictates where the function saves the data; can be mixed with return_str param
		:return: str if return_str is True else None
	"""

	with open(path) as f:
		nodes = ast.parse(f.read())

	for node in ast.walk(nodes):
		if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
			# See: https://docs.python.org/3/library/ast.html#ast.arguments
			for arg in [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]:
				arg.annotation = None
			if node.args.vararg is not None:
				node.args.vararg.annotation = None
			if node.args.kwarg is not None:
				node.args.kwarg.annotation = None
			node.returns = None
	nodes = ast.fix_missing_locations(_DowngradeAnnAssign().visit(nodes))

	if return_str:
		return ast.unparse(nodes)
	with open(output_file_path, 'w') as f:
		f.writelines(ast.unparse(nodes))
	return None  # just so mypy can leave me alone
