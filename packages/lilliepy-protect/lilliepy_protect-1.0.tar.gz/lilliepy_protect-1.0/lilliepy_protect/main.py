from reactpy import component, use_scope
from reactpy_router import navigate
from functools import wraps

def protect(fallback, attr="granted"):
    def decorator(comp):
        @wraps(comp)
        @component
        def protected_component(*args, **kwargs):
            scope = use_scope()
            if getattr(scope["user"], attr, False):  
                return comp(*args, **kwargs)
            else:
                if callable(fallback):  
                    return fallback()
                elif isinstance(fallback, str):  
                    navigate(fallback)
                else:
                    raise ValueError("Invalid fallback type. Must be callable or URL string.")
        
        return protected_component
    return decorator
