# fractal_animations.py
"""
Módulo: fractal_animations
--------------------------
Define funções de animação para GIFs de fractal. Para adicionar uma nova animação, crie uma função que gere uma sequência de imagens e registre no ANIMATION_REGISTRY.

Assinatura esperada:
def anim_nome(params, frame_idx, num_frames):
    ...
    return PIL.Image

Para registrar:
ANIMATION_REGISTRY["nome"] = anim_nome

Assim, a nova animação aparecerá automaticamente na UI.
"""

from fractal_render import generate_fractal_image
import math
import numpy as np
from PIL import Image, ImageEnhance, ImageChops

ANIMATION_REGISTRY = {}

def color_anim(params, frame_idx, num_frames):
    # Efeito: ciclo de cor/fade
    base = generate_fractal_image(
        width=params['width'], height=params['height'], pixel_size=int(params['pixel_size']),
        fractal_type=params['fractal'], color_palette_override=params['palette'],
        max_iter=params['iterations'], julia_const=params['julia_const'],
        zoom=params['zoom'], center=(params['center_x'], params['center_y']),
        color_shift_override=params['color_shift'], power=params['power'],
        bailout=params['bailout'], transform=params['transform'], intensity=params['intensity'],
        brightness=params.get('brightness', 1.0), contrast=params.get('contrast', 1.0),
        saturation=params.get('saturation', 1.0), gamma=params.get('gamma', 1.0),
        hue_shift=params.get('hue_shift', 0.0)
    )
    # Fade de cor usando ImageEnhance
    factor = 0.7 + 0.3 * math.sin(2 * math.pi * frame_idx / num_frames)
    enhancer = ImageEnhance.Color(base)
    return enhancer.enhance(factor)
ANIMATION_REGISTRY["color"] = color_anim

# Animação cristalina
def crystal_anim(params, frame_idx, num_frames):
    # Efeito: "facetado" com deslocamento de pixels (crystalize)
    base = generate_fractal_image(
        width=params['width'], height=params['height'], pixel_size=int(params['pixel_size']),
        fractal_type=params['fractal'], color_palette_override=params['palette'],
        max_iter=params['iterations'], julia_const=params['julia_const'],
        zoom=params['zoom'], center=(params['center_x'], params['center_y']),
        color_shift_override=params['color_shift'], power=params['power'],
        bailout=params['bailout'], transform=params['transform'], intensity=params['intensity'],
        brightness=params.get('brightness', 1.0), contrast=params.get('contrast', 1.0),
        saturation=params.get('saturation', 1.0), gamma=params.get('gamma', 1.0),
        hue_shift=params.get('hue_shift', 0.0)
    )
    arr = np.array(base)
    h, w = arr.shape[:2]
    block = int(4 + 8 * abs(math.sin(2 * math.pi * frame_idx / num_frames)))
    for y in range(0, h, block):
        for x in range(0, w, block):
            arr[y:y+block, x:x+block] = arr[y, x]
    return Image.fromarray(arr)
ANIMATION_REGISTRY["crystal"] = crystal_anim

# Animação membrana
def membrane_anim(params, frame_idx, num_frames):
    # Efeito: "orgânico" - distorção de onda
    base = generate_fractal_image(
        width=params['width'], height=params['height'], pixel_size=int(params['pixel_size']),
        fractal_type=params['fractal'], color_palette_override=params['palette'],
        max_iter=params['iterations'], julia_const=params['julia_const'],
        zoom=params['zoom'], center=(params['center_x'], params['center_y']),
        color_shift_override=params['color_shift'], power=params['power'],
        bailout=params['bailout'], transform=params['transform'], intensity=params['intensity'],
        brightness=params.get('brightness', 1.0), contrast=params.get('contrast', 1.0),
        saturation=params.get('saturation', 1.0), gamma=params.get('gamma', 1.0),
        hue_shift=params.get('hue_shift', 0.0)
    )
    arr = np.array(base)
    h, w = arr.shape[:2]
    new_arr = np.zeros_like(arr)
    for y in range(h):
        offset = int(8 * math.sin(2 * math.pi * (y / h) + 2 * math.pi * frame_idx / num_frames))
        new_arr[y] = np.roll(arr[y], offset, axis=0)
    return Image.fromarray(new_arr)
ANIMATION_REGISTRY["membrane"] = membrane_anim

# Animação vértice
def vertex_anim(params, frame_idx, num_frames):
    # Efeito: "teleporte" - jump cut
    base = generate_fractal_image(
        width=params['width'], height=params['height'], pixel_size=int(params['pixel_size']),
        fractal_type=params['fractal'], color_palette_override=params['palette'],
        max_iter=params['iterations'], julia_const=params['julia_const'],
        zoom=params['zoom'], center=(params['center_x'], params['center_y']),
        color_shift_override=params['color_shift'], power=params['power'],
        bailout=params['bailout'], transform=params['transform'], intensity=params['intensity'],
        brightness=params.get('brightness', 1.0), contrast=params.get('contrast', 1.0),
        saturation=params.get('saturation', 1.0), gamma=params.get('gamma', 1.0),
        hue_shift=params.get('hue_shift', 0.0)
    )
    if frame_idx % (num_frames // 4 + 1) == 0:
        # Inverter imagem como "teleporte"
        return base.transpose(Image.FLIP_LEFT_RIGHT)
    return base
ANIMATION_REGISTRY["vertex"] = vertex_anim

# Animação raio
def ray_anim(params, frame_idx, num_frames):
    # Efeito: "elétrico" - flashes (dissolve)
    base = generate_fractal_image(
        width=params['width'], height=params['height'], pixel_size=int(params['pixel_size']),
        fractal_type=params['fractal'], color_palette_override=params['palette'],
        max_iter=params['iterations'], julia_const=params['julia_const'],
        zoom=params['zoom'], center=(params['center_x'], params['center_y']),
        color_shift_override=params['color_shift'], power=params['power'],
        bailout=params['bailout'], transform=params['transform'], intensity=params['intensity'],
        brightness=params.get('brightness', 1.0), contrast=params.get('contrast', 1.0),
        saturation=params.get('saturation', 1.0), gamma=params.get('gamma', 1.0),
        hue_shift=params.get('hue_shift', 0.0)
    )
    arr = np.array(base)
    mask = np.random.rand(*arr.shape[:2]) < (0.1 + 0.2 * abs(math.sin(8 * math.pi * frame_idx / num_frames)))
    arr[mask] = 255 - arr[mask]
    return Image.fromarray(arr)
ANIMATION_REGISTRY["ray"] = ray_anim

# Animação onda
def wave_anim(params, frame_idx, num_frames):
    # Efeito: "onda" - deslocamento vertical suave
    base = generate_fractal_image(
        width=params['width'], height=params['height'], pixel_size=int(params['pixel_size']),
        fractal_type=params['fractal'], color_palette_override=params['palette'],
        max_iter=params['iterations'], julia_const=params['julia_const'],
        zoom=params['zoom'], center=(params['center_x'], params['center_y']),
        color_shift_override=params['color_shift'], power=params['power'],
        bailout=params['bailout'], transform=params['transform'], intensity=params['intensity'],
        brightness=params.get('brightness', 1.0), contrast=params.get('contrast', 1.0),
        saturation=params.get('saturation', 1.0), gamma=params.get('gamma', 1.0),
        hue_shift=params.get('hue_shift', 0.0)
    )
    arr = np.array(base)
    h, w = arr.shape[:2]
    new_arr = np.zeros_like(arr)
    for x in range(w):
        offset = int(10 * math.sin(2 * math.pi * (x / w) + 2 * math.pi * frame_idx / num_frames))
        new_arr[:, x] = np.roll(arr[:, x], offset, axis=0)
    return Image.fromarray(new_arr)
ANIMATION_REGISTRY["wave"] = wave_anim

# Animação natureza
def nature_anim(params, frame_idx, num_frames):
    # Efeito: "dissolução orgânica" - fade + ruído
    base = generate_fractal_image(
        width=params['width'], height=params['height'], pixel_size=int(params['pixel_size']),
        fractal_type=params['fractal'], color_palette_override=params['palette'],
        max_iter=params['iterations'], julia_const=params['julia_const'],
        zoom=params['zoom'], center=(params['center_x'], params['center_y']),
        color_shift_override=params['color_shift'], power=params['power'],
        bailout=params['bailout'], transform=params['transform'], intensity=params['intensity'],
        brightness=params.get('brightness', 1.0), contrast=params.get('contrast', 1.0),
        saturation=params.get('saturation', 1.0), gamma=params.get('gamma', 1.0),
        hue_shift=params.get('hue_shift', 0.0)
    )
    arr = np.array(base).astype(np.float32)
    alpha = 0.5 + 0.5 * math.sin(2 * math.pi * frame_idx / num_frames)
    noise = np.random.normal(0, 30 * (1 - alpha), arr.shape)
    arr = np.clip(arr * alpha + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)
ANIMATION_REGISTRY["nature"] = nature_anim

# ... (adicione as demais animações do seu arquivo, seguindo o padrão acima)

def get_animation_types():
    return list(ANIMATION_REGISTRY.keys())

def get_animation_func(name):
    return ANIMATION_REGISTRY.get(name, color_anim)
