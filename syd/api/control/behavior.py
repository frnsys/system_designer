"""
this is unsafe but we can assume you're in control of where it's running
and who has access (like ipython notebooks) (TODO check ipython notebook
security model)
"""

import ast

def parse_behavior(name, body, behaviors):
    args = sorted({node.id for node in ast.walk(ast.parse(body)) if isinstance(node, ast.Name)})
    source = 'def {name}({args}): return {body}'.format(
        name=name,
        args=','.join(args),
        body=body)
    exec(compile(source, '', 'exec'), {}, behaviors)

behaviors = {}
body = 'x + y'
name = 'my_behavior'
parse_behavior(name, body, behaviors)
print(behaviors)
print(behaviors['my_behavior'](2,2))