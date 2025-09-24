# palettes.py
"""
Módulo: palettes
----------------
Define funções de paletas de cor. Para adicionar uma nova paleta, crie uma função que retorna (r,g,b) e registre no PALETTE_REGISTRY.

Exemplo:
def fire_palette(t, intensity=1.0):
    ...
    return (r, g, b)
PALETTE_REGISTRY["fire"] = fire_palette

Assim, a nova paleta aparecerá automaticamente na UI.
"""

import math
import colorsys
import random

# Utilitário para ajustes de cor
def calibrate_color(rgb, brightness=1.0, contrast=1.0, saturation=1.0, gamma=1.0, hue_shift=0.0):
    # Converte para HSV
    r, g, b = [x / 255.0 for x in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    # Aplica hue shift
    h = (h + hue_shift) % 1.0
    # Aplica saturação
    s = max(0.0, min(1.0, s * saturation))
    # Aplica brilho
    v = max(0.0, min(1.0, v * brightness))
    # Volta para RGB
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    # Aplica contraste
    r = ((r - 0.5) * contrast + 0.5)
    g = ((g - 0.5) * contrast + 0.5)
    b = ((b - 0.5) * contrast + 0.5)
    # Aplica gamma
    r = pow(max(0, r), gamma)
    g = pow(max(0, g), gamma)
    b = pow(max(0, b), gamma)
    # Converte para 0-255
    return (
        int(max(0, min(255, r * 255))),
        int(max(0, min(255, g * 255))),
        int(max(0, min(255, b * 255)))
    )

PALETTE_REGISTRY = {}


# Rainbow: arco-íris clássico, saturação e brilho fixos
def rainbow_palette(t, intensity=1.0, brightness=1.0, contrast=1.0, saturation=1.0, gamma=1.0, hue_shift=0.0):
    h = t % 1.0
    s = 1.0
    v = 1.0
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    rgb = (r*255*intensity, g*255*intensity, b*255*intensity)
    return calibrate_color(rgb, brightness, contrast, saturation, gamma, hue_shift)
PALETTE_REGISTRY["rainbow"] = rainbow_palette


# Fire: tons de vermelho, laranja e amarelo, brilho crescente

# Nova fire_palette: gradiente de vermelho profundo, laranja, amarelo, branco, com "fagulhas" e variação de saturação
def fire_palette(t, intensity=1.0, brightness=1.0, contrast=1.0, saturation=1.0, gamma=1.0, hue_shift=0.0):
    # Fagulhas: pequenas explosões de branco/amarelo
    spark = 0.0
    if t > 0.85:
        spark = min(1.0, (t-0.85)*8)
    h = 0.04 + 0.12 * (1-t)  # vermelho escuro para amarelo
    s = 0.8 + 0.2 * (1-t) + 0.2 * spark
    v = 0.4 + 0.6 * t + 0.5 * spark
    # Pequena oscilação para "chama viva"
    h += 0.01 * math.sin(12*math.pi*t)
    s = min(1.0, s + 0.1 * math.sin(8*math.pi*t))
    v = min(1.0, v + 0.1 * math.cos(10*math.pi*t))
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    rgb = (r*255*intensity, g*255*intensity, b*255*intensity)
    return calibrate_color(rgb, brightness, contrast, saturation, gamma, hue_shift)
PALETTE_REGISTRY["fire"] = fire_palette


# Crystal: tons frios, azul, ciano, branco, brilho alto, saturação variável
def crystal_palette(t, intensity=1.0, brightness=1.0, contrast=1.0, saturation=1.0, gamma=1.0, hue_shift=0.0):
    h = 0.55 + 0.15 * math.sin(8 * math.pi * t)
    s = 0.3 + 0.7 * abs(math.cos(4 * math.pi * t))
    v = 0.85 + 0.15 * abs(math.sin(6 * math.pi * t))
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, max(0, min(1, s)), max(0, min(1, v)))
    rgb = (r*255*intensity, g*255*intensity, b*255*intensity)
    return calibrate_color(rgb, brightness, contrast, saturation, gamma, hue_shift)
PALETTE_REGISTRY["crystal"] = crystal_palette

# Paleta membrana

# Paleta membrane: tons azul-esverdeados orgânicos, suaves, com variação de saturação e brilho
def membrane_palette(t, intensity=1.0, brightness=1.0, contrast=1.0, saturation=1.0, gamma=1.0, hue_shift=0.0):
    h = 0.45 + 0.15 * math.sin(4 * math.pi * t)  # faixa azul-esverdeada
    s = 0.6 + 0.3 * math.cos(6 * math.pi * t)
    v = 0.7 + 0.2 * math.sin(8 * math.pi * t)
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, max(0, min(1, s)), max(0, min(1, v)))
    rgb = (r*255*intensity, g*255*intensity, b*255*intensity)
    return calibrate_color(rgb, brightness, contrast, saturation, gamma, hue_shift)
PALETTE_REGISTRY["membrane"] = membrane_palette


# Vertex: tons de verde, roxo e azul, padrão geométrico

# Nova vertex_palette: gradiente geométrico, tons de verde, azul, roxo, com "picos" e cortes abruptos
def vertex_palette(t, intensity=1.0, brightness=1.0, contrast=1.0, saturation=1.0, gamma=1.0, hue_shift=0.0):
    # Efeito "facetado": cortes abruptos de cor
    facet = int(t*6) % 2
    h = 0.3 + 0.25 * math.sin(10 * math.pi * t + facet*math.pi)
    s = 0.6 + 0.4 * abs(math.sin(7 * math.pi * t))
    v = 0.5 + 0.5 * abs(math.cos(9 * math.pi * t + facet*math.pi/2))
    # Pico de cor a cada "vértice"
    if facet == 1:
        h += 0.15
        s = min(1.0, s + 0.2)
        v = min(1.0, v + 0.2)
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, max(0, min(1, s)), max(0, min(1, v)))
    rgb = (r*255*intensity, g*255*intensity, b*255*intensity)
    return calibrate_color(rgb, brightness, contrast, saturation, gamma, hue_shift)
PALETTE_REGISTRY["vertex"] = vertex_palette

# Paleta raio

# Paleta ray: tons elétricos, contrastantes, com flashes de amarelo, magenta e azul
def ray_palette(t, intensity=1.0, brightness=1.0, contrast=1.0, saturation=1.0, gamma=1.0, hue_shift=0.0):
    # Alterna entre amarelo, magenta e azul em picos
    if t < 0.33:
        h = 0.15 + 0.1 * math.sin(24 * math.pi * t)  # amarelo
        s = 1.0
        v = 1.0
    elif t < 0.66:
        h = 0.83 + 0.1 * math.cos(18 * math.pi * t)  # magenta
        s = 0.9
        v = 0.8 + 0.2 * math.sin(10 * math.pi * t)
    else:
        h = 0.6 + 0.1 * math.sin(30 * math.pi * t)  # azul
        s = 0.8 + 0.2 * math.cos(12 * math.pi * t)
        v = 0.7 + 0.3 * math.sin(8 * math.pi * t)
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, max(0, min(1, s)), max(0, min(1, v)))
    rgb = (r*255*intensity, g*255*intensity, b*255*intensity)
    return calibrate_color(rgb, brightness, contrast, saturation, gamma, hue_shift)
PALETTE_REGISTRY["ray"] = ray_palette


# Wave: tons pastel, variação suave, efeito "onda" de cor
def wave_palette(t, intensity=1.0, brightness=1.0, contrast=1.0, saturation=1.0, gamma=1.0, hue_shift=0.0):
    h = 0.1 + 0.4 * abs(math.sin(2 * math.pi * t))
    s = 0.4 + 0.3 * math.sin(4 * math.pi * t)
    v = 0.7 + 0.2 * math.cos(6 * math.pi * t)
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, max(0, min(1, s)), max(0, min(1, v)))
    rgb = (r*255*intensity, g*255*intensity, b*255*intensity)
    return calibrate_color(rgb, brightness, contrast, saturation, gamma, hue_shift)
PALETTE_REGISTRY["wave"] = wave_palette


# Nature: tons terrosos, verdes, marrons, amarelos, padrão orgânico
def nature_palette(t, intensity=1.0, brightness=1.0, contrast=1.0, saturation=1.0, gamma=1.0, hue_shift=0.0):
    h = 0.22 + 0.15 * math.sin(3 * math.pi * t)  # verde para amarelo
    s = 0.7 - 0.3 * abs(math.cos(5 * math.pi * t))
    v = 0.5 + 0.4 * abs(math.sin(7 * math.pi * t))
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, max(0, min(1, s)), max(0, min(1, v)))
    rgb = (r*255*intensity, g*255*intensity, b*255*intensity)
    return calibrate_color(rgb, brightness, contrast, saturation, gamma, hue_shift)
PALETTE_REGISTRY["nature"] = nature_palette


# Tecnomagia: tons ciano, magenta, verde-limão, padrão "sintético"
def tecnomagia_palette(t, intensity=1.0, brightness=1.0, contrast=1.0, saturation=1.0, gamma=1.0, hue_shift=0.0):
    h = 0.5 + 0.3 * math.sin(10 * math.pi * t)
    s = 0.8 + 0.2 * math.cos(12 * math.pi * t)
    v = 0.6 + 0.3 * math.sin(8 * math.pi * t)
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, max(0, min(1, s)), max(0, min(1, v)))
    rgb = (r*255*intensity, g*255*intensity, b*255*intensity)
    return calibrate_color(rgb, brightness, contrast, saturation, gamma, hue_shift)
PALETTE_REGISTRY["tecnomagia"] = tecnomagia_palette

# ... (adicione as demais paletas do seu arquivo, seguindo o padrão acima)

# Plasma: gradiente psicodélico, magenta, azul, verde, amarelo
def plasma_palette(t, intensity=1.0, brightness=1.0, contrast=1.0, saturation=1.0, gamma=1.0, hue_shift=0.0):
    h = 0.7 + 0.3 * math.sin(8 * math.pi * t)
    s = 0.8 + 0.2 * math.cos(12 * math.pi * t)
    v = 0.6 + 0.4 * math.sin(10 * math.pi * t)
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, max(0, min(1, s)), max(0, min(1, v)))
    rgb = (r*255*intensity, g*255*intensity, b*255*intensity)
    return calibrate_color(rgb, brightness, contrast, saturation, gamma, hue_shift)
PALETTE_REGISTRY["plasma"] = plasma_palette

# Cyberpunk: azul neon, magenta, verde-limão, preto
def cyberpunk_palette(t, intensity=1.0, brightness=1.0, contrast=1.0, saturation=1.0, gamma=1.0, hue_shift=0.0):
    if t < 0.33:
        h = 0.55  # azul neon
        s = 1.0
        v = 0.8 + 0.2 * t
    elif t < 0.66:
        h = 0.83  # magenta
        s = 1.0
        v = 0.7 + 0.3 * (t-0.33)
    else:
        h = 0.28  # verde-limão
        s = 0.9
        v = 0.6 + 0.4 * (t-0.66)
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    rgb = (r*255*intensity, g*255*intensity, b*255*intensity)
    return calibrate_color(rgb, brightness, contrast, saturation, gamma, hue_shift)
PALETTE_REGISTRY["cyberpunk"] = cyberpunk_palette

def get_palette_types():
    return list(PALETTE_REGISTRY.keys())

def get_palette_func(name):
    return PALETTE_REGISTRY.get(name, rainbow_palette)
