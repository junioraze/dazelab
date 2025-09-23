
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import math
import random
import colorsys
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# --- Custom Theme for Modern Dark UI ---
def set_modern_dark_style(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TFrame", background="#23272e")
    style.configure("TLabel", background="#23272e", foreground="#e0e0e0", font=("Segoe UI", 10))
    style.configure("TButton", background="#2d313a", foreground="#e0e0e0", font=("Segoe UI", 10, "bold"), borderwidth=0)
    style.map("TButton", background=[("active", "#3a3f4b")])
    style.configure("TCombobox", fieldbackground="#23272e", background="#23272e", foreground="#e0e0e0")
    style.configure("TEntry", fieldbackground="#23272e", background="#23272e", foreground="#e0e0e0")
    style.configure("TSpinbox", fieldbackground="#23272e", background="#23272e", foreground="#e0e0e0")
    style.configure("TNotebook", background="#23272e", tabposition='n')
    style.configure("TNotebook.Tab", background="#2d313a", foreground="#e0e0e0", font=("Segoe UI", 10, "bold"))
    style.map("TNotebook.Tab", background=[("selected", "#3a3f4b")])
    style.configure("Horizontal.TScale", background="#23272e")
    style.configure("TSeparator", background="#444")



# --- Fractal Core Functions ---
def screen_to_fractal(x, y, width, height, min_x, max_x, min_y, max_y):
    fractal_x = min_x + (x / width) * (max_x - min_x)
    fractal_y = min_y + (y / height) * (max_y - min_y)
    return fractal_x, fractal_y

def apply_transform(x, y, mode):
    if mode == "none":
        return x, y
    if mode == "sin":
        return math.sin(x), math.sin(y)
    if mode == "spiral":
        r = math.sqrt(x*x + y*y)
        angle = math.atan2(y, x)
        return r * math.cos(angle + r), r * math.sin(angle + r)
    if mode == "swirl":
        r = math.sqrt(x*x + y*y)
        return x * math.sin(r*r) - y * math.cos(r*r), x * math.cos(r*r) + y * math.sin(r*r)
    if mode == "waves":
        return x + 0.1 * math.sin(y * 10), y + 0.1 * math.sin(x * 10)
    if mode == "polar":
        r = math.sqrt(x*x + y*y)
        angle = math.atan2(y, x)
        return r, angle
    if mode == "hyperbolic":
        return x/(x*x + y*y + 0.1), y/(x*x + y*y + 0.1)
    return x, y

def mandelbrot(c, max_iterations=100, power=2.0, bailout=2.0):
    z = 0
    for i in range(max_iterations):
        if abs(z) > bailout:
            return i
        z = z**power + c
    return max_iterations

def julia(c, max_iterations=100, power=2.0, bailout=2.0, julia_constant=complex(-0.7, 0.27)):
    z = c
    for i in range(max_iterations):
        if abs(z) > bailout:
            return i
        z = z**power + julia_constant
    return max_iterations

def burning_ship(c, max_iterations=100, power=2.0, bailout=2.0):
    z = 0
    for i in range(max_iterations):
        if abs(z) > bailout:
            return i
        z = complex(abs(z.real), abs(z.imag))
        z = z**power + c
    return max_iterations

def newton(c, max_iterations=100, power=2.0, bailout=2.0):
    z = c
    for i in range(max_iterations):
        if abs(z) < 0.001:
            return max_iterations
        f = z**3 - 1
        df = 3 * z**2
        if abs(df) < 1e-6:
            return i
        z = z - f / df
        if abs(z) > bailout:
            return i
    return max_iterations

def spider(c, max_iterations=100, power=2.0, bailout=2.0):
    z = c
    for i in range(max_iterations):
        if abs(z) > bailout:
            return i
        z = z**power + c + z/2
    return max_iterations

def magnet(c, max_iterations=100, power=2.0, bailout=2.0):
    z = c
    for i in range(max_iterations):
        if abs(z) > bailout:
            return i
        numerator = (z**2 + c - 1)**2
        denominator = 4 * z * (z**2 - 1)
        if abs(denominator) < 1e-6:
            return i
    return max_iterations

def custom_formula(c, max_iterations=100, power=2.0, bailout=2.0):
    z = c
    for i in range(max_iterations):
        if abs(z) > bailout:
            return i
        z = math.sin(z.real) + math.cos(z.imag)*1j + c
    return max_iterations


_random_palette_seed = None
def get_color(iterations, max_iterations, z=None, color_palette="rainbow", color_shift=0.0, color_intensity=1.0):
    global _random_palette_seed
    if iterations == max_iterations:
        return (0, 0, 0)
    t = (iterations + color_shift * max_iterations) / max_iterations
    t = t % 1.0
    if color_palette == "default":
        r = int(9 * (1-t) * t * t * t * 255 * color_intensity)
        g = int(15 * (1-t) * (1-t) * t * t * 255 * color_intensity)
        b = int(8.5 * (1-t) * (1-t) * (1-t) * t * 255 * color_intensity)
    elif color_palette == "blue":
        r = int(5 * (1-t) * t * 255 * color_intensity)
        g = int(10 * (1-t) * (1-t) * t * 255 * color_intensity)
        b = int(15 * (1-t) * t * t * 255 * color_intensity)
    elif color_palette == "red":
        r = int(15 * (1-t) * t * t * 255 * color_intensity)
        g = int(5 * (1-t) * (1-t) * t * 255 * color_intensity)
        b = int(5 * (1-t) * (1-t) * (1-t) * 255 * color_intensity)
    elif color_palette == "green":
        r = int(5 * (1-t) * (1-t) * t * 255 * color_intensity)
        g = int(15 * (1-t) * t * t * 255 * color_intensity)
        b = int(5 * (1-t) * (1-t) * 255 * color_intensity)
    elif color_palette == "rainbow":
        h = t
        s = 0.8
        v = 1.0
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        r, g, b = int(r * 255 * color_intensity), int(g * 255 * color_intensity), int(b * 255 * color_intensity)
    elif color_palette == "monochrome":
        intensity = int(t * 255 * color_intensity)
        return (intensity, intensity, intensity)
    elif color_palette == "random":
        if _random_palette_seed is None:
            _random_palette_seed = random.randint(0, 1_000_000_000)
        random.seed(_random_palette_seed + iterations)
        r = int(random.random() * 255 * color_intensity)
        g = int(random.random() * 255 * color_intensity)
        b = int(random.random() * 255 * color_intensity)
    elif color_palette == "fire":
        r = min(255, int(255 * t * 1.5 * color_intensity))
        g = min(255, int(255 * t * 0.8 * color_intensity))
        b = min(255, int(255 * t * 0.3 * color_intensity))
    elif color_palette == "ice":
        r = min(255, int(255 * (1-t) * 0.7 * color_intensity))
        g = min(255, int(255 * t * 1.2 * color_intensity))
        b = min(255, int(255 * t * 1.5 * color_intensity))
    elif color_palette == "cosmic":
        r = int(127 * (1 + math.sin(3.0 * t)) * color_intensity)
        g = int(127 * (1 + math.sin(3.0 * t + 2)) * color_intensity)
        b = int(127 * (1 + math.sin(3.0 * t + 4)) * color_intensity)
    else:
        r = g = b = int(t * 255 * color_intensity)
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    return (r, g, b)

def generate_fractal_image(
    width=600, height=400, pixel_size=2,
    fractal_type=None, color_palette_override=None,
    max_iter=None, julia_const=None, zoom=None, center=None, color_shift_override=None,
    power=None, bailout=None, transform=None, intensity=None
):
    w, h = width, height
    px = int(pixel_size)
    cols = w // px
    rows = h // px
    zlevel = zoom or 1.0
    cx, cy = center or (0.0, 0.0)
    cshift = color_shift_override if color_shift_override is not None else 0.0
    maxit = max_iter or 100
    julia_c = julia_const or complex(-0.7, 0.27)
    palette = color_palette_override or "rainbow"
    ftype = fractal_type or "mandelbrot"
    pwr = power or 2.0
    blt = bailout or 2.0
    transf = transform or "none"
    inten = intensity or 1.0
    range_x = 3.0 / zlevel
    range_y = (3.0 * h / w) / zlevel
    min_x, max_x = cx - range_x/2, cx + range_x/2
    min_y, max_y = cy - range_y/2, cy + range_y/2
    if ftype == "mandelbrot":
        fractal_func = lambda c, maxit: mandelbrot(c, maxit, pwr, blt)
    elif ftype == "julia":
        fractal_func = lambda c, maxit: julia(c, maxit, pwr, blt, julia_c)
    elif ftype == "burning_ship":
        fractal_func = lambda c, maxit: burning_ship(c, maxit, pwr, blt)
    elif ftype == "newton":
        fractal_func = lambda c, maxit: newton(c, maxit, pwr, blt)
    elif ftype == "spider":
        fractal_func = lambda c, maxit: spider(c, maxit, pwr, blt)
    elif ftype == "magnet":
        fractal_func = lambda c, maxit: magnet(c, maxit, pwr, blt)
    elif ftype == "custom":
        fractal_func = lambda c, maxit: custom_formula(c, maxit, pwr, blt)
    else:
        fractal_func = lambda c, maxit: mandelbrot(c, maxit, pwr, blt)
    pixel_data = [None] * (cols * rows)
    def line_task(row):
        line = []
        for col in range(cols):
            fractal_x, fractal_y = screen_to_fractal(
                col, row, cols, rows, min_x, max_x, min_y, max_y
            )
            fractal_x, fractal_y = apply_transform(fractal_x, fractal_y, transf)
            c = complex(fractal_x, fractal_y)
            iterations = fractal_func(c, maxit)
            color = get_color(iterations, maxit, c, palette, cshift, inten)
            line.append(color)
        return (row, line)
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(line_task, row) for row in range(rows)]
        for future in as_completed(futures):
            row, line = future.result()
            for col, color in enumerate(line):
                pixel_data[row * cols + col] = color
    img = Image.new("RGB", (cols, rows))
    for row in range(rows):
        for col in range(cols):
            img.putpixel((col, row), pixel_data[row * cols + col])
    return img

class FractalApp(tk.Tk):


    def _on_tab_changed(self, event):
        # Garante que a imagem do fractal e o gif animado permaneçam visíveis ao alternar abas
        if hasattr(self, '_fractal_img_refs') and self._fractal_img_refs:
            img_tk = self._fractal_img_refs[-1]
            self.image_panel.config(image=img_tk)
            self.image_panel.image = img_tk
        if hasattr(self, '_gif_anim_frames') and self._gif_anim_frames:
            idx = getattr(self, '_last_gif_idx', 0)
            self.gif_panel.config(image=self._gif_anim_frames[idx])
            self.gif_panel.image = self._gif_anim_frames[idx]

    def generate_gif(self):
        # Limpa exibição do GIF anterior ao iniciar novo
        self.gif_panel.config(image='', text='Gerando GIF...', bg='#222', fg='#fff')
        self.gif_panel.image = None
        if hasattr(self, '_gif_anim_frames'):
            self._gif_anim_frames.clear()
        print('[DEBUG] Iniciando geração do GIF')
        params = self.get_params()
        num_frames = params['num_frames']
        frames = [None] * num_frames

        def frame_task(i):
            print(f'[DEBUG] Iniciando frame {i+1}/{num_frames}')
            self.after(0, lambda: self.gif_panel.config(text=f'Gerando frame {i+1}/{num_frames}...', image='', bg="#222", fg="#fff"))
            anim = params['anim_type']
            if anim == 'color':
                shift = (i / num_frames)
                print(f'[DEBUG] Frame {i+1}: shift={shift}')
                img = generate_fractal_image(
                    width=params['width'], height=params['height'], pixel_size=int(params['pixel_size']),
                    fractal_type=params['fractal'], color_palette_override=params['palette'],
                    max_iter=params['iterations'], julia_const=params['julia_const'],
                    zoom=params['zoom'], center=(params['center_x'], params['center_y']),
                    color_shift_override=shift, power=params['power'],
                    bailout=params['bailout'], transform=params['transform'], intensity=params['intensity']
                )
            elif anim == 'zoom_in':
                z = params['zoom'] * (1.05 ** i)
                print(f'[DEBUG] Frame {i+1}: zoom={z}')
                img = generate_fractal_image(
                    width=params['width'], height=params['height'], pixel_size=int(params['pixel_size']),
                    fractal_type=params['fractal'], color_palette_override=params['palette'],
                    max_iter=params['iterations'], julia_const=params['julia_const'],
                    zoom=z, center=(params['center_x'], params['center_y']),
                    color_shift_override=params['color_shift'], power=params['power'],
                    bailout=params['bailout'], transform=params['transform'], intensity=params['intensity']
                )
            elif anim == 'zoom_out':
                z = params['zoom'] * (0.95 ** i)
                print(f'[DEBUG] Frame {i+1}: zoom={z}')
                img = generate_fractal_image(
                    width=params['width'], height=params['height'], pixel_size=int(params['pixel_size']),
                    fractal_type=params['fractal'], color_palette_override=params['palette'],
                    max_iter=params['iterations'], julia_const=params['julia_const'],
                    zoom=z, center=(params['center_x'], params['center_y']),
                    color_shift_override=params['color_shift'], power=params['power'],
                    bailout=params['bailout'], transform=params['transform'], intensity=params['intensity']
                )
            elif anim == 'julia':
                angle = 2 * math.pi * (i / num_frames)
                julia_c = complex(math.cos(angle), math.sin(angle))
                print(f'[DEBUG] Frame {i+1}: julia_c={julia_c}')
                img = generate_fractal_image(
                    width=params['width'], height=params['height'], pixel_size=int(params['pixel_size']),
                    fractal_type='julia', color_palette_override=params['palette'],
                    max_iter=params['iterations'], julia_const=julia_c,
                    zoom=params['zoom'], center=(params['center_x'], params['center_y']),
                    color_shift_override=params['color_shift'], power=params['power'],
                    bailout=params['bailout'], transform=params['transform'], intensity=params['intensity']
                )
            elif anim == 'rotate':
                # Rotaciona o fractal em torno do centro
                angle = 2 * math.pi * (i / num_frames)
                cx, cy = params['center_x'], params['center_y']
                # Aplica rotação ao centro
                r = math.hypot(cx, cy)
                theta = math.atan2(cy, cx) + angle
                new_cx = r * math.cos(theta)
                new_cy = r * math.sin(theta)
                print(f'[DEBUG] Frame {i+1}: rotate angle={angle:.2f}, center=({new_cx:.3f},{new_cy:.3f})')
                img = generate_fractal_image(
                    width=params['width'], height=params['height'], pixel_size=int(params['pixel_size']),
                    fractal_type=params['fractal'], color_palette_override=params['palette'],
                    max_iter=params['iterations'], julia_const=params['julia_const'],
                    zoom=params['zoom'], center=(new_cx, new_cy),
                    color_shift_override=params['color_shift'], power=params['power'],
                    bailout=params['bailout'], transform=params['transform'], intensity=params['intensity']
                )
            elif anim == 'pan':
                # Move o centro do fractal em linha reta
                dx = 1.0 * math.cos(2 * math.pi * (i / num_frames))
                dy = 1.0 * math.sin(2 * math.pi * (i / num_frames))
                new_cx = params['center_x'] + dx * 0.5
                new_cy = params['center_y'] + dy * 0.5
                print(f'[DEBUG] Frame {i+1}: pan center=({new_cx:.3f},{new_cy:.3f})')
                img = generate_fractal_image(
                    width=params['width'], height=params['height'], pixel_size=int(params['pixel_size']),
                    fractal_type=params['fractal'], color_palette_override=params['palette'],
                    max_iter=params['iterations'], julia_const=params['julia_const'],
                    zoom=params['zoom'], center=(new_cx, new_cy),
                    color_shift_override=params['color_shift'], power=params['power'],
                    bailout=params['bailout'], transform=params['transform'], intensity=params['intensity']
                )
            elif anim == 'pulse':
                # Zoom pulsante (aproxima e afasta)
                z = params['zoom'] * (1 + 0.3 * math.sin(2 * math.pi * (i / num_frames)))
                print(f'[DEBUG] Frame {i+1}: pulse zoom={z}')
                img = generate_fractal_image(
                    width=params['width'], height=params['height'], pixel_size=int(params['pixel_size']),
                    fractal_type=params['fractal'], color_palette_override=params['palette'],
                    max_iter=params['iterations'], julia_const=params['julia_const'],
                    zoom=z, center=(params['center_x'], params['center_y']),
                    color_shift_override=params['color_shift'], power=params['power'],
                    bailout=params['bailout'], transform=params['transform'], intensity=params['intensity']
                )
            elif anim == 'warp':
                # Distorção ondulatória no parâmetro de transformação
                warp_mode = 'waves'
                print(f'[DEBUG] Frame {i+1}: warp transform={warp_mode}')
                img = generate_fractal_image(
                    width=params['width'], height=params['height'], pixel_size=int(params['pixel_size']),
                    fractal_type=params['fractal'], color_palette_override=params['palette'],
                    max_iter=params['iterations'], julia_const=params['julia_const'],
                    zoom=params['zoom'], center=(params['center_x'], params['center_y']),
                    color_shift_override=params['color_shift'], power=params['power'],
                    bailout=params['bailout'], transform=warp_mode, intensity=params['intensity']
                )
            else:
                img = generate_fractal_image(
                    width=params['width'], height=params['height'], pixel_size=int(params['pixel_size']),
                    fractal_type=params['fractal'], color_palette_override=params['palette'],
                    max_iter=params['iterations'], julia_const=params['julia_const'],
                    zoom=params['zoom'], center=(params['center_x'], params['center_y']),
                    color_shift_override=params['color_shift'], power=params['power'],
                    bailout=params['bailout'], transform=params['transform'], intensity=params['intensity']
                )
            assert img is not None, f'Frame {i+1} retornou None!'
            print(f'[DEBUG] Finalizado frame {i+1}/{num_frames} (type={type(img)})')
            self.after(0, lambda: self.gif_panel.config(text=f'Frame {i+1}/{num_frames} pronto!', image='', bg="#222", fg="#fff"))
            return (i, img)

        def animate_gif(frames_pil, delay=50):
            if not frames_pil:
                return
            self._gif_anim_frames = [ImageTk.PhotoImage(f.resize((600, 400))) for f in frames_pil]
            def loop(idx=0):
                if not hasattr(self, '_gif_anim_frames'):
                    return
                self.gif_panel.config(image=self._gif_anim_frames[idx], text='')
                self.gif_panel.image = self._gif_anim_frames[idx]
                self.after(delay, loop, (idx+1) % len(self._gif_anim_frames))
            loop()

        def task():
            global _random_palette_seed
            _random_palette_seed = None  # Garante nova seed a cada GIF
            from concurrent.futures import ThreadPoolExecutor, as_completed
            try:
                with ThreadPoolExecutor() as executor:
                    futures = [executor.submit(frame_task, i) for i in range(num_frames)]
                    for idx, future in enumerate(futures):
                        i, img = future.result()
                        frames[i] = img
                        self.status_var.set(f'Frame {i+1}/{num_frames} pronto.')
                print('[DEBUG] Todos os frames do GIF gerados')
                self.after(200, lambda: animate_gif(frames, delay=50))
                # Salva GIF se usuário quiser
                from tkinter import filedialog
                file = filedialog.asksaveasfilename(defaultextension='.gif', filetypes=[('GIF','*.gif')], initialfile=params['gif_name'])
                if file:
                    frames[0].save(file, save_all=True, append_images=frames[1:], duration=50, loop=0)
                    # Salva JSON com os parâmetros
                    import json, os                                                                                         
                    json_path = os.path.splitext(file)[0] + '.json'
                    # Remove objetos não serializáveis
                    params_serializable = {k: (float(v) if isinstance(v, (int, float)) else str(v)) for k, v in params.items()}
                    with open(json_path, 'w', encoding='utf-8') as fjson:
                        json.dump(params_serializable, fjson, ensure_ascii=False, indent=2)
                    self.status_var.set(f'GIF salvo como {file}\nParâmetros salvos em {json_path}')
                else:
                    self.status_var.set('GIF exibido (não salvo)')
            except Exception as e:
                print('[ERRO] Falha ao gerar GIF:', e)
                self.after(0, lambda: self._show_gif_error(str(e)))
            # Reabilita botão
            for tab in self.notebook.tabs():
                if self.notebook.tab(tab, 'text') == 'GIF Animado':
                    for child in self.notebook.nametowidget(tab).winfo_children():
                        if isinstance(child, ttk.Button) and child['text'] == 'Gerar GIF':
                            child.state(['!disabled'])

        # Desabilita botão durante processamento
        for tab in self.notebook.tabs():
            if self.notebook.tab(tab, 'text') == 'GIF Animado':
                for child in self.notebook.nametowidget(tab).winfo_children():
                    if isinstance(child, ttk.Button) and child['text'] == 'Gerar GIF':
                        child.state(['disabled'])

        threading.Thread(target=task).start()

    def _show_gif_error(self, msg):
        self.gif_panel.config(image='', text='Erro ao gerar GIF:\n'+msg, bg='#a00', fg='#fff')
        self.gif_panel.image = None
        self.status_var.set('Erro ao gerar GIF.')
    def generate_fractal(self):
        # Limpa exibição da imagem anterior ao iniciar novo
        self.image_panel.config(image='', text='Gerando fractal...', bg='#222', fg='#fff')
        self.image_panel.image = None
        if hasattr(self, '_fractal_img_refs'):
            self._fractal_img_refs.clear()
        print('[DEBUG] Iniciando geração do fractal')
        def worker():
            params = self.get_params()
            print('[DEBUG] Parâmetros:', params)
            try:
                img = generate_fractal_image(
                    width=params['width'], height=params['height'], pixel_size=int(params['pixel_size']),
                    fractal_type=params['fractal'], color_palette_override=params['palette'],
                    max_iter=params['iterations'], julia_const=params['julia_const'],
                    zoom=params['zoom'], center=(params['center_x'], params['center_y']),
                    color_shift_override=params['color_shift'], power=params['power'],
                    bailout=params['bailout'], transform=params['transform'], intensity=params['intensity']
                )
                print('[DEBUG] Fractal gerado com sucesso')
                self.after(0, lambda: self._show_fractal_image(img))
            except Exception as e:
                print('[ERRO] Falha ao gerar fractal:', e)
                self.after(0, lambda: self._show_fractal_error(str(e)))
        threading.Thread(target=worker, daemon=True).start()

    def _show_fractal_image(self, img):
        if img is None:
            self._show_fractal_error('Imagem não gerada')
            return
        # Mantém referência fixa para não sumir nunca
        if not hasattr(self, '_fractal_img_refs'):
            self._fractal_img_refs = []
        # Redimensiona imagem para caber no painel
        img_resized = img.resize((600, 400), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_resized)
        self._fractal_img_refs.append(img_tk)
        # Limpa o painel antes de exibir
        self.image_panel.config(image='', text='', bg='#222')
        self.image_panel.image = None
        # Exibe imagem
        self.image_panel.config(image=img_tk, text='')
        self.image_panel.image = img_tk
        self.image_panel.update_idletasks()
        # Limita o tamanho da lista de refs para evitar vazamento de memória
        if len(self._fractal_img_refs) > 5:
            self._fractal_img_refs = self._fractal_img_refs[-5:]
        self.status_var.set('Fractal gerado com sucesso.')

    def _show_fractal_error(self, msg):
        self.image_panel.config(image='', text='Erro ao gerar fractal:\n'+msg, bg='#a00', fg='#fff')
        self.image_panel.image = None
        self.status_var.set('Erro ao gerar fractal.')

    def _show_fractal_image(self, img):
        # Mantém referência fixa para não sumir nunca
        if not hasattr(self, '_fractal_img_refs'):
            self._fractal_img_refs = []
        # Redimensiona imagem para caber no painel
        img_resized = img.resize((600, 400), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_resized)
        self._fractal_img_refs.append(img_tk)
        # Limpa o painel antes de exibir
        self.image_panel.config(image='', text='', bg='#222')
        self.image_panel.image = None
        # Exibe imagem
        self.image_panel.config(image=img_tk, text='')
        self.image_panel.image = img_tk
        self.image_panel.update_idletasks()
        # Limita o tamanho da lista de refs para evitar vazamento de memória
        if len(self._fractal_img_refs) > 5:
            self._fractal_img_refs = self._fractal_img_refs[-5:]
        self.status_var.set('Fractal gerado com sucesso.')

    def display_image(self, img, panel):
        # Mantém referência para não sumir
        img_tk = ImageTk.PhotoImage(img)
        panel.config(image=img_tk)
        panel.image = img_tk

    def save_image(self):
        # TODO: implementar salvamento da imagem
        self.status_var.set('Função salvar imagem ainda não implementada.')

    def __init__(self):
        super().__init__()
        self.title('Infinity Fractal Generator (Tkinter)')
        self.geometry('1500x750')
        self.configure(bg='#23272e')
        set_modern_dark_style(self)
        self.fractal_params = {
            'fractal': tk.StringVar(value='mandelbrot'),
            'palette': tk.StringVar(value='rainbow'),
            'iterations': tk.IntVar(value=100),
            'zoom': tk.DoubleVar(value=1.0),
            'center_x': tk.DoubleVar(value=0.0),
            'center_y': tk.DoubleVar(value=0.0),
            'color_shift': tk.DoubleVar(value=0.0),
            'power': tk.DoubleVar(value=2.0),
            'bailout': tk.DoubleVar(value=4.0),
            'transform': tk.StringVar(value='none'),
            'intensity': tk.DoubleVar(value=1.0),
            'width': tk.IntVar(value=600),
            'height': tk.IntVar(value=400),
            'pixel_size': tk.DoubleVar(value=1.0),
            'julia_real': tk.DoubleVar(value=0.0),
            'julia_imag': tk.DoubleVar(value=0.0),
            'anim_type': tk.StringVar(value='color'),
            'num_frames': tk.IntVar(value=30),
            'gif_name': tk.StringVar(value='fractal.gif'),
        }
        # Inicializa atributos de painel e status
        self.image_panel = None
        self.gif_panel = None
        self.status_var = tk.StringVar(value='')
        self._fractal_img_refs = []
        self._gif_anim_frames = []
        self.create_widgets()

    # Removido método duplicado create_widgets que causava conflito de layout

    def get_params(self):
        p = {k: v.get() for k, v in self.fractal_params.items()}
        p['julia_const'] = complex(p['julia_real'], p['julia_imag'])
        return p

    def create_widgets(self):
        # Frame principal vertical
        main_frame = ttk.Frame(self, style="Dark.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Menu notebook direto no main_frame (sem frame extra)
        self.notebook = ttk.Notebook(main_frame, style="Dark.TNotebook")
        self.notebook.pack(side=tk.TOP, fill=tk.X, expand=False, padx=6, pady=(2, 0))

        # Vincula evento de troca de aba para manter imagens visíveis
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        # Aba 1: Parâmetros Fractal (5 linhas, 2 componentes por linha)
        tab_fractal = ttk.Frame(self.notebook)
        self.notebook.add(tab_fractal, text="Fractal")
        small_font = ("Segoe UI", 9)
        # Só mostra fractais realmente implementados
        fractal_options = [
            "mandelbrot", "julia", "burning_ship", "newton", "spider", "magnet", "custom"
        ]
        for i, (label1, widget1, label2, widget2) in enumerate([
            ('Tipo de Fractal', ttk.Combobox(tab_fractal, textvariable=self.fractal_params['fractal'], values=fractal_options, width=12, font=small_font),
             'Paleta de Cores', ttk.Combobox(tab_fractal, textvariable=self.fractal_params['palette'], values=["default", "blue", "red", "green", "rainbow", "monochrome", "random", "fire", "ice", "cosmic"], width=10, font=small_font)),
            ('Máximo de Iterações', ttk.Spinbox(tab_fractal, from_=10, to=1000, textvariable=self.fractal_params['iterations'], width=7, font=small_font),
             'Zoom', ttk.Entry(tab_fractal, textvariable=self.fractal_params['zoom'], width=8, font=small_font)),
            ('Centro X', ttk.Entry(tab_fractal, textvariable=self.fractal_params['center_x'], width=8, font=small_font),
             'Centro Y', ttk.Entry(tab_fractal, textvariable=self.fractal_params['center_y'], width=8, font=small_font)),
            ('Deslocamento de Cor', ttk.Scale(tab_fractal, from_=0.0, to=1.0, variable=self.fractal_params['color_shift'], orient=tk.HORIZONTAL, length=80),
             'Expoente (Power)', ttk.Entry(tab_fractal, textvariable=self.fractal_params['power'], width=8, font=small_font)),
            ('Valor de Escape (Bailout)', ttk.Entry(tab_fractal, textvariable=self.fractal_params['bailout'], width=8, font=small_font),
             'Transformação', ttk.Combobox(tab_fractal, textvariable=self.fractal_params['transform'], values=["none", "sin", "spiral", "swirl", "waves", "polar", "hyperbolic"], width=10, font=small_font)),
        ]):
            row = i
            ttk.Label(tab_fractal, text=label1, font=small_font).grid(row=row, column=0, sticky='w', padx=1, pady=0)
            widget1.grid(row=row, column=1, sticky='ew', padx=1, pady=0)
            ttk.Label(tab_fractal, text=label2, font=small_font).grid(row=row, column=2, sticky='w', padx=1, pady=0)
            widget2.grid(row=row, column=3, sticky='ew', padx=1, pady=0)
        # Linha extra para os campos restantes
        row += 1
        ttk.Label(tab_fractal, text='Intensidade de Cor', font=small_font).grid(row=row, column=0, sticky='w', padx=1, pady=0)
        ttk.Scale(tab_fractal, from_=0.1, to=5.0, variable=self.fractal_params['intensity'], orient=tk.HORIZONTAL, length=80).grid(row=row, column=1, sticky='ew', padx=1, pady=0)
        ttk.Label(tab_fractal, text='Largura (px)', font=small_font).grid(row=row, column=2, sticky='w', padx=1, pady=0)
        ttk.Entry(tab_fractal, textvariable=self.fractal_params['width'], width=8, font=small_font).grid(row=row, column=3, sticky='ew', padx=1, pady=0)
        row += 1
        ttk.Label(tab_fractal, text='Altura (px)', font=small_font).grid(row=row, column=0, sticky='w', padx=1, pady=0)
        ttk.Entry(tab_fractal, textvariable=self.fractal_params['height'], width=8, font=small_font).grid(row=row, column=1, sticky='ew', padx=1, pady=0)
        ttk.Label(tab_fractal, text='Tamanho do Pixel', font=small_font).grid(row=row, column=2, sticky='w', padx=1, pady=0)
        ttk.Entry(tab_fractal, textvariable=self.fractal_params['pixel_size'], width=8, font=small_font).grid(row=row, column=3, sticky='ew', padx=1, pady=0)
        row += 1
        ttk.Label(tab_fractal, text='Julia Real', font=small_font).grid(row=row, column=0, sticky='w', padx=1, pady=0)
        ttk.Entry(tab_fractal, textvariable=self.fractal_params['julia_real'], width=8, font=small_font).grid(row=row, column=1, sticky='ew', padx=1, pady=0)
        ttk.Label(tab_fractal, text='Julia Imag', font=small_font).grid(row=row, column=2, sticky='w', padx=1, pady=0)
        ttk.Entry(tab_fractal, textvariable=self.fractal_params['julia_imag'], width=8, font=small_font).grid(row=row, column=3, sticky='ew', padx=1, pady=0)
        for col in range(4):
            tab_fractal.grid_columnconfigure(col, weight=1)

        # Área de visualização: imagem do fractal e GIF lado a lado
        vis_frame = ttk.Frame(main_frame, style="Dark.TFrame")
        vis_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=2, pady=(2, 0))
        vis_frame.columnconfigure(0, weight=1)
        vis_frame.columnconfigure(1, weight=1)
        vis_frame.rowconfigure(0, weight=1)

        if self.image_panel is None:
            self.image_panel = tk.Label(vis_frame, bg="#222")
            self.image_panel.grid(row=0, column=0, padx=(0, 4), pady=(2, 0), sticky="nsew")
        if self.gif_panel is None:
            self.gif_panel = tk.Label(vis_frame, bg="#222")
            self.gif_panel.grid(row=0, column=1, padx=(4, 0), pady=(2, 0), sticky="nsew")
        # Barra de status
        status_bar = ttk.Label(self, textvariable=self.status_var, anchor='w', style="TLabel")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=0, pady=0)

        # Aba 2: GIF Animado
        tab_gif = ttk.Frame(self.notebook)
        self.notebook.add(tab_gif, text="GIF Animado")
        ttk.Label(tab_gif, text='Tipo de Animação').pack(anchor='w', padx=8, pady=2)
        ttk.Combobox(tab_gif, textvariable=self.fractal_params['anim_type'], values=[
            "color", "zoom_in", "zoom_out", "julia", "rotate", "pan", "pulse", "warp"
        ], width=15).pack(padx=8, pady=2)
        ttk.Label(tab_gif, text='Frames do GIF').pack(anchor='w', padx=8, pady=2)
        ttk.Spinbox(tab_gif, from_=5, to=120, textvariable=self.fractal_params['num_frames'], width=10).pack(padx=8, pady=2)
        ttk.Label(tab_gif, text='Nome do GIF').pack(anchor='w', padx=8, pady=2)
        ttk.Entry(tab_gif, textvariable=self.fractal_params['gif_name'], width=18).pack(padx=8, pady=2)
        # Barra de progresso
        self.gif_progress = ttk.Progressbar(tab_gif, orient='horizontal', mode='determinate', length=200)
        self.gif_progress.pack(padx=8, pady=4)
        self.gif_progress.pack_forget()  # Esconde inicialmente
        ttk.Button(tab_gif, text='Gerar GIF', command=self.generate_gif).pack(fill=tk.X, padx=8, pady=8)

        # Aba 3: Ações
        tab_actions = ttk.Frame(self.notebook)
        self.notebook.add(tab_actions, text="Ações")
        actions_frame = ttk.Frame(tab_actions)
        actions_frame.pack(anchor='center', pady=6)
        ttk.Button(actions_frame, text='Gerar Fractal', command=self.generate_fractal, width=18).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(actions_frame, text='Salvar Imagem', command=self.save_image, width=18).pack(side=tk.LEFT, padx=(8, 0))


def main():
    app = FractalApp()
    app.mainloop()

if __name__ == "__main__":
    main()