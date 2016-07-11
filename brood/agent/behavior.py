from functools import wraps


def behavior(*required_vars):
    """decorator to declare an agent behavior
    and its required state variables.
    when an Agent class is created, presence of
    required variables is validated.
    behaviors should not modify state variables directly!
    they should only _submit_ updates to be applied during the update phase."""
    def decorator(f):
        f.required_vars = list(required_vars)
        @wraps(f)
        def func(agent, *args, **kwargs):
            return f(agent, *args, **kwargs)
        return func
    return decorator

