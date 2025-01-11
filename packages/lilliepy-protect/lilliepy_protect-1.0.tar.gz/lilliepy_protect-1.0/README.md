# Lilliepy Protect

a decorator to protect you components

## how to use

```python
from lilliepy_protect import protect
from reactpy import component, html

@component
def fallback():
    return html.h1("u werent logged in...")

@protect(fallback=fallback, attr="logged_in")
@component
def ProtectedPage():
    return html.h1("welcome")
```

```python

# ...

protect -> (
    comp: reactpy.types.ComponentType, # the component to be protected
    fallback: reactpy.types.ComponentType, # the return url or component to navigate/render
    attr: str # the value to find in the scope (basically the granter code)(defaulted to "granted")
)

# ...

```