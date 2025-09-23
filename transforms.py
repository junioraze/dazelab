# transforms.py
"""
Módulo: transforms
------------------
Define funções de transformação para fractais. Para adicionar uma nova transformação, crie uma função e registre no TRANSFORM_REGISTRY.

Exemplo:
def swirl_transform(z, **kwargs):
    # lógica
    return z
TRANSFORM_REGISTRY["swirl"] = swirl_transform

Assim, a nova transformação aparecerá automaticamente na UI.
"""

TRANSFORM_REGISTRY = {}

def none_transform(z, **kwargs):
    return z
TRANSFORM_REGISTRY["none"] = none_transform

def sin_transform(z, **kwargs):
    import cmath
    return cmath.sin(z)
TRANSFORM_REGISTRY["sin"] = sin_transform

def spiral_transform(z, **kwargs):
    import cmath
    return z * cmath.exp(1j * abs(z))
TRANSFORM_REGISTRY["spiral"] = spiral_transform

# ...adicione outras transformações conforme necessário...

def get_transform_types():
    return list(TRANSFORM_REGISTRY.keys())

def get_transform_func(name):
    return TRANSFORM_REGISTRY.get(name, none_transform)
