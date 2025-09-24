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

# Swirl: gira o ponto em torno da origem proporcional à distância
def swirl_transform(z, **kwargs):
    import cmath
    angle = abs(z) * 1.5
    return z * cmath.exp(1j * angle)
TRANSFORM_REGISTRY["swirl"] = swirl_transform

# Kaleidoscope: repete o ângulo em setores, criando simetria
def kaleidoscope_transform(z, **kwargs):
    import cmath
    n = kwargs.get('kaleidoscope_n', 6)
    r, theta = abs(z), cmath.phase(z)
    theta = (theta % (2*math.pi/n)) * n
    return cmath.rect(r, theta)
TRANSFORM_REGISTRY["kaleidoscope"] = kaleidoscope_transform

# Fold: dobra o plano ao redor do eixo Y
def fold_transform(z, **kwargs):
    if z.real < 0:
        return complex(-z.real, z.imag)
    return z
TRANSFORM_REGISTRY["fold"] = fold_transform

# Mirror: espelha em relação ao eixo X
def mirror_transform(z, **kwargs):
    if z.imag < 0:
        return complex(z.real, -z.imag)
    return z
TRANSFORM_REGISTRY["mirror"] = mirror_transform

# Polar: transforma para coordenadas polares e distorce
def polar_transform(z, **kwargs):
    import cmath
    r, theta = abs(z), cmath.phase(z)
    r = r ** 1.2
    theta = theta * 1.5
    return cmath.rect(r, theta)
TRANSFORM_REGISTRY["polar"] = polar_transform

def get_transform_types():
    return list(TRANSFORM_REGISTRY.keys())

def get_transform_func(name):
    return TRANSFORM_REGISTRY.get(name, none_transform)
