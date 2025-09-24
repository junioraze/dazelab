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

# Nova membrane_anim: distorção orgânica + "pulsação" e glitch
def membrane_anim(params, frame_idx, num_frames):
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
        # Onda orgânica + "pulsação" vertical
        offset = int(8 * math.sin(2 * math.pi * (y / h) + 2 * math.pi * frame_idx / num_frames))
        offset += int(4 * math.sin(2 * math.pi * frame_idx / num_frames))
        new_arr[y] = np.roll(arr[y], offset, axis=0)
    # Glitch: linhas horizontais deslocadas
    if frame_idx % 8 == 0:
        for y in range(0, h, 12):
            new_arr[y] = np.roll(new_arr[y], int(10 * math.sin(frame_idx)), axis=0)
    return Image.fromarray(new_arr)
ANIMATION_REGISTRY["membrane"] = membrane_anim

# Animação vértice

# Nova vertex_anim: cortes abruptos, "glitch" geométrico, saltos e inversões
def vertex_anim(params, frame_idx, num_frames):
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
    # Jump cut: inverter, espelhar, rotacionar em quadros específicos
    if frame_idx % (num_frames // 5 + 1) == 0:
        arr = np.flipud(arr)
    if frame_idx % (num_frames // 7 + 1) == 0:
        arr = np.fliplr(arr)
    if frame_idx % (num_frames // 9 + 1) == 0:
        arr = np.rot90(arr)
    # Glitch: blocos deslocados
    if frame_idx % 6 == 0:
        for y in range(0, h, 32):
            arr[y:y+8] = np.roll(arr[y:y+8], int(10 * math.sin(frame_idx)), axis=1)
    return Image.fromarray(arr)
ANIMATION_REGISTRY["vertex"] = vertex_anim

# Animação raio
def ray_anim(params, frame_idx, num_frames):
    # Efeito: "raio energético" - traçado de linhas brilhantes e flashes dinâmicos
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
    # Desenha "raios" diagonais e flashes
    num_rays = 3 + (frame_idx % 3)
    for i in range(num_rays):
        angle = 2 * math.pi * (i / num_rays) + math.pi * math.sin(frame_idx / 7.0)
        cx = w // 2 + int((w//3) * math.sin(angle + frame_idx * 0.1))
        cy = h // 2 + int((h//3) * math.cos(angle - frame_idx * 0.13))
        length = int(0.7 * min(w, h))
        for l in range(length):
            x = int(cx + l * math.cos(angle + 0.2 * math.sin(frame_idx/3)))
            y = int(cy + l * math.sin(angle + 0.2 * math.cos(frame_idx/3)))
            if 0 <= x < w and 0 <= y < h:
                arr[y, x] = [255, 255, 180] if l % 7 < 3 else [200, 200, 255]
    # Flashes aleatórios
    if frame_idx % 5 == 0:
        for _ in range(8):
            fx = np.random.randint(0, w)
            fy = np.random.randint(0, h)
            arr[max(0,fy-2):min(h,fy+2), max(0,fx-2):min(w,fx+2)] = [255, 255, 255]
    # Oscilação de brilho
    arr = np.clip(arr * (0.9 + 0.2 * math.sin(frame_idx/2)), 0, 255).astype(np.uint8)
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

# Glitch: cortes horizontais e deslocamentos aleatórios
def glitch_anim(params, frame_idx, num_frames):
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
    for y in range(0, h, 12):
        if (frame_idx + y) % 3 == 0:
            arr[y] = np.roll(arr[y], int(20 * math.sin(frame_idx + y)), axis=0)
    return Image.fromarray(arr)
ANIMATION_REGISTRY["glitch"] = glitch_anim

# Plasma wave: distorção ondulatória colorida
def plasma_wave_anim(params, frame_idx, num_frames):
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
    for x in range(w):
        offset = int(18 * math.sin(2 * math.pi * (x / w) + 2 * math.pi * frame_idx / num_frames))
        arr[:, x] = np.roll(arr[:, x], offset, axis=0)
    return Image.fromarray(arr)
ANIMATION_REGISTRY["plasma_wave"] = plasma_wave_anim


def get_animation_types():
    return list(ANIMATION_REGISTRY.keys())

def get_animation_func(name):
    return ANIMATION_REGISTRY.get(name, color_anim)
