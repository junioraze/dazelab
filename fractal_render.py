# fractal_render.py
"""
Função utilitária para gerar a imagem do fractal usando a função de fractal e a paleta escolhidas.
Percorre cada pixel, calcula o valor de c, chama a função do fractal, aplica a paleta e monta a imagem PIL.
"""
from PIL import Image
from fractal_core import get_fractal_func
from palettes import get_palette_func
import math

def generate_fractal_image(
    width, height, pixel_size, fractal_type, color_palette_override,
    max_iter, julia_const, zoom, center, color_shift_override, power, bailout, transform, intensity,
    brightness=1.0, contrast=1.0, saturation=1.0, gamma=1.0, hue_shift=0.0
):
    fractal_func = get_fractal_func(fractal_type)
    palette_func = get_palette_func(color_palette_override)
    img = Image.new('RGB', (width, height))
    px = img.load()
    cx, cy = center
    for y in range(height):
        for x in range(width):
            # Mapeia pixel para plano complexo
            zx = (x - width/2) * (4.0/(zoom*width)) * pixel_size + cx
            zy = (y - height/2) * (4.0/(zoom*height)) * pixel_size + cy
            c = complex(zx, zy)
            # Calcula iteração
            iter_count = fractal_func(
                c,
                max_iterations=max_iter,
                power=power,
                bailout=bailout,
                julia_const=julia_const
            )
            t = iter_count / max_iter
            t = (t + color_shift_override) % 1.0
            color = palette_func(
                t,
                intensity=intensity,
                brightness=brightness,
                contrast=contrast,
                saturation=saturation,
                gamma=gamma,
                hue_shift=hue_shift
            )
            px[x, y] = color
    return img
