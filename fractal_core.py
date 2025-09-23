# fractal_core.py
"""
Módulo: fractal_core
-------------------
Contém todas as funções de geração de fractais. Para adicionar um novo tipo de fractal, basta criar uma função que siga a assinatura abaixo e registrá-la no dicionário FRACTAL_REGISTRY.

Assinatura esperada:
def nome_fractal(c, max_iterations, power, bailout, julia_const=None):
    ...
    return iterations (int)

Para registrar:
FRACTAL_REGISTRY["nome"] = nome_fractal

Assim, o novo tipo aparecerá automaticamente na UI.
"""
import math
import random
import cmath

FRACTAL_REGISTRY = {}

def mandelbrot(c, max_iterations=100, power=2.0, bailout=2.0, **kwargs):
    # Mandelbrot clássico, padrão
    z = 0
    for i in range(max_iterations):
        if abs(z) > bailout:
            return i
        z = z**power + c
    return max_iterations
FRACTAL_REGISTRY["mandelbrot"] = mandelbrot

def julia(c, max_iterations=100, power=2.0, bailout=2.0, julia_const=complex(-0.7,0.27), **kwargs):
    # Julia: fractal de plano alternativo, com rotação sutil
    z = c
    for i in range(max_iterations):
        if abs(z) > bailout:
            return i
        z = z**power + julia_const * cmath.exp(1j * 0.2 * i)
    return max_iterations
FRACTAL_REGISTRY["julia"] = julia

def burning_ship(c, max_iterations=100, power=2.0, bailout=2.0, **kwargs):
    # Burning Ship: fractal "navio em chamas", com distorção vertical
    z = 0
    for i in range(max_iterations):
        if abs(z) > bailout:
            return i
        z = complex(abs(z.real), -abs(z.imag))
        z = z**power + c + 0.2 * complex(math.sin(i * 0.1), math.cos(i * 0.1))
    return max_iterations
FRACTAL_REGISTRY["burning_ship"] = burning_ship

def newton(c, max_iterations=100, power=2.0, bailout=2.0, **kwargs):
    # Newton: fractal de raízes, com rotação e caos
    z = c
    for i in range(max_iterations):
        if abs(z) < 0.001:
            return max_iterations
        f = z**3 - 1
        df = 3 * z**2 + 0.5 * cmath.exp(1j * i * 0.1)
        if abs(df) < 1e-6:
            return i
        z = z - f / df + 0.1 * cmath.exp(1j * i * 0.2)
        if abs(z) > bailout:
            return i
    return max_iterations
FRACTAL_REGISTRY["newton"] = newton

# ... (adicione aqui as demais funções de fractal do seu arquivo, seguindo o padrão acima)

# Exemplo de função customizada:
def eldritch_fractal(c, max_iterations=100, power=2.0, bailout=2.0, **kwargs):
    # Eldritch: fractal "caótico", distorções não-euclidianas
    z = c
    for i in range(max_iterations):
        if abs(z) > bailout:
            return i
        z = (z**power + c) * complex(math.sin(z.real * i * 0.1), math.cos(z.imag * i * 0.1))
        z += 0.2 * cmath.exp(1j * (z.real + z.imag))
    return max_iterations
FRACTAL_REGISTRY["eldritch"] = eldritch_fractal

# Repita para todos os tipos do seu arquivo, mudando o nome e a lógica.
# Fractal cristalino
def crystal_fractal(c, max_iterations=100, power=2.0, bailout=2.0, **kwargs):
    # Crystal: fractal "cristalino", simetria e padrões facetados
    z = c
    for i in range(max_iterations):
        if abs(z) > bailout:
            return i
        z = abs(z.real) ** power - abs(z.imag) ** power + c
        z = complex(z, math.sin(z.imag * 3) + math.cos(z.real * 3))
        z += 0.1 * cmath.exp(1j * i * 0.3)
    return max_iterations
FRACTAL_REGISTRY["crystal"] = crystal_fractal

# Fractal membrana
def membrane_fractal(c, max_iterations=100, power=2.0, bailout=2.0, **kwargs):
    # Membrane: fractal "orgânico", padrões pulsantes
    z = c
    for i in range(max_iterations):
        if abs(z) > bailout:
            return i
        z = (z**power + c) * (0.7 + 0.3 * math.sin(i * 0.2 + z.real * 0.5))
        z += 0.15 * complex(math.sin(z.real * 5 + i * 0.1), math.cos(z.imag * 5 + i * 0.1))
    return max_iterations
FRACTAL_REGISTRY["membrane"] = membrane_fractal

# Fractal vértice
def vertex_fractal(c, max_iterations=100, power=2.0, bailout=2.0, **kwargs):
    # Vertex: fractal "geométrico", vértices e padrões angulares
    z = c
    for i in range(max_iterations):
        if abs(z) > bailout:
            return i
        z = (z**power + c) * (1 + 0.7 * abs(math.sin(i * 0.5 + z.imag * 0.3)))
        z += 0.25 * complex(math.sin(z.real * 8 + i * 0.2), math.cos(z.imag * 8 + i * 0.2))
    return max_iterations
FRACTAL_REGISTRY["vertex"] = vertex_fractal

# Fractal raio
def ray_fractal(c, max_iterations=100, power=2.0, bailout=2.0, **kwargs):
    # Ray: fractal "elétrico", padrões de raio e flashes
    z = c
    for i in range(max_iterations):
        if abs(z) > bailout:
            return i
        z = (z**power + c) * (1 + 0.9 * math.sin(i * 0.7 + z.real * 0.6))
        z += 0.35 * complex(math.sin(z.real * 12 + i * 0.3), math.cos(z.imag * 12 + i * 0.3))
    return max_iterations
FRACTAL_REGISTRY["ray"] = ray_fractal

# Fractal onda
def wave_fractal(c, max_iterations=100, power=2.0, bailout=2.0, **kwargs):
    # Wave: fractal "ondulante", padrões suaves e harmônicos
    z = c
    for i in range(max_iterations):
        if abs(z) > bailout:
            return i
        z = (z**power + c) * (1 + 0.5 * math.sin(i * 0.3 + z.imag * 0.4))
        z += 0.22 * complex(math.sin(z.real * 6 + i * 0.15), math.cos(z.imag * 6 + i * 0.15))
    return max_iterations
FRACTAL_REGISTRY["wave"] = wave_fractal

# Fractal natureza
def nature_fractal(c, max_iterations=100, power=2.0, bailout=2.0, **kwargs):
    # Nature: fractal "orgânico", padrões naturais e ramificados
    z = c
    for i in range(max_iterations):
        if abs(z) > bailout:
            return i
        z = (z**power + c) * (1 + 0.4 * math.sin(i * 0.2 + z.real * 0.2 + z.imag * 0.2))
        z += 0.18 * complex(math.sin(z.real * 3 + i * 0.1), math.cos(z.imag * 3 + i * 0.1))
    return max_iterations
FRACTAL_REGISTRY["nature"] = nature_fractal

# Para obter a lista de fractais disponíveis:
def get_fractal_types():
    return list(FRACTAL_REGISTRY.keys())

# Para obter a função:
def get_fractal_func(name):
    return FRACTAL_REGISTRY.get(name, mandelbrot)
