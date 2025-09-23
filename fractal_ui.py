# fractal_ui.py
"""
Módulo: fractal_ui
------------------
Interface Tkinter separada da lógica. Importa fractal_core, palettes, fractal_animations e monta a UI dinamicamente.

Como adicionar novas opções:
- Fractal: crie função em fractal_core.py e registre no FRACTAL_REGISTRY.
- Paleta: crie função em palettes.py e registre no PALETTE_REGISTRY.
- Animação: crie função em fractal_animations.py e registre no ANIMATION_REGISTRY.

A UI detecta automaticamente as opções disponíveis.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from fractal_core import get_fractal_types, get_fractal_func
from palettes import get_palette_types, get_palette_func
from fractal_animations import get_animation_types, get_animation_func
from transforms import get_transform_types

# Tema visual agradável

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

class FractalApp(tk.Tk):
    def save_image(self):
        # Salva a última imagem fractal exibida, se houver
        if not hasattr(self, '_fractal_img_refs') or not self._fractal_img_refs:
            messagebox.showerror('Erro', 'Nenhuma imagem fractal para salvar.')
            return
        # Recupera a última imagem PIL usada para exibição
        if hasattr(self, '_last_fractal_img') and self._last_fractal_img is not None:
            img = self._last_fractal_img
        else:
            messagebox.showerror('Erro', 'Nenhuma imagem fractal para salvar.')
            return
        file = filedialog.asksaveasfilename(defaultextension='.png', filetypes=[('PNG','*.png'),('JPEG','*.jpg'),('Todos','*.*')], initialfile='fractal.png')
        if file:
            try:
                img.save(file)
                self.status_var.set(f'Imagem salva em: {file}')
            except Exception as e:
                messagebox.showerror('Erro ao salvar', str(e))
                self.status_var.set('Erro ao salvar imagem.')

    def generate_fractal(self):
        # Limpa exibição da imagem anterior ao iniciar novo
        self.image_panel.config(image='', text='Gerando fractal...', bg='#222', fg='#fff')
        self.image_panel.image = None
        self.status_var.set('Gerando fractal...')
        if hasattr(self, '_fractal_img_refs'):
            self._fractal_img_refs.clear()
        def worker():
            params = self.get_params()
            try:
                from fractal_render import generate_fractal_image
                img = generate_fractal_image(
                    width=params['width'],
                    height=params['height'],
                    pixel_size=int(params['pixel_size']),
                    fractal_type=params['fractal'],
                    color_palette_override=params['palette'],
                    max_iter=params['iterations'],
                    julia_const=params['julia_const'],
                    zoom=params['zoom'],
                    center=(params['center_x'], params['center_y']),
                    color_shift_override=params['color_shift'],
                    power=params['power'],
                    bailout=params['bailout'],
                    transform=params['transform'],
                    intensity=params['intensity'],
                    brightness=params.get('brightness', 1.0),
                    contrast=params.get('contrast', 1.0),
                    saturation=params.get('saturation', 1.0),
                    gamma=params.get('gamma', 1.0),
                    hue_shift=params.get('hue_shift', 0.0)
                )
                self.after(0, lambda: self._show_fractal_image(img))
            except Exception as e:
                self.after(0, lambda: self._show_fractal_error(str(e)))
        import threading
        threading.Thread(target=worker, daemon=True).start()

    def _show_fractal_image(self, img):
        # Guarda referência à última imagem PIL para salvar
        self._last_fractal_img = img
        if img is None:
            self._show_fractal_error('Imagem não gerada')
            return
        if not hasattr(self, '_fractal_img_refs'):
            self._fractal_img_refs = []
        img_resized = img.resize((600, 400))
        from PIL import ImageTk
        img_tk = ImageTk.PhotoImage(img_resized)
        self._fractal_img_refs.append(img_tk)
        self.image_panel.config(image='', text='', bg='#222')
        self.image_panel.image = None
        self.image_panel.config(image=img_tk, text='')
        self.image_panel.image = img_tk
        self.image_panel.update_idletasks()
        if len(self._fractal_img_refs) > 5:
            self._fractal_img_refs = self._fractal_img_refs[-5:]
        self.status_var.set('Fractal gerado com sucesso.')

    def _show_fractal_error(self, msg):
        self.image_panel.config(image='', text='Erro ao gerar fractal:\n'+msg, bg='#a00', fg='#fff')
        self.image_panel.image = None
        self.status_var.set('Erro ao gerar fractal.')
    def get_params(self):
        p = {k: v.get() for k, v in self.fractal_params.items()}
        p['julia_const'] = complex(p['julia_real'], p['julia_imag'])
        return p


    def generate_gif(self):
        # Parar animação anterior, se houver
        if hasattr(self, '_gif_anim_running') and self._gif_anim_running:
            self._gif_anim_running = False
        params = self.get_params()
        num_frames = params['num_frames']
        anim_type = params['anim_type']
        frames = []
        self.status_var.set('Gerando GIF...')
        self.gif_progress['maximum'] = num_frames
        self.gif_progress['value'] = 0
        self.gif_progress.pack()
        def worker():
            for i in range(num_frames):
                frame_params = params.copy()
                anim_func = get_animation_func(anim_type)
                img = anim_func(frame_params, i, num_frames)
                frames.append(img)
                self.after(0, lambda v=i+1: self._update_gif_progress(v, num_frames))
            self.after(0, lambda: self._show_gif_frames(frames))
        import threading
        threading.Thread(target=worker, daemon=True).start()

    def _update_gif_progress(self, value, total):
        self.gif_progress['value'] = value
        self.status_var.set(f'Gerando GIF... ({value}/{total})')
        self.gif_progress.update_idletasks()

    def _show_gif_frames(self, frames):
        self._gif_anim_frames = [ImageTk.PhotoImage(f.resize((600, 400))) for f in frames]
        self._gif_anim_running = True
        def loop(idx=0):
            if not hasattr(self, '_gif_anim_frames') or not self._gif_anim_running:
                return
            self.gif_panel.config(image=self._gif_anim_frames[idx], text='')
            self.gif_panel.image = self._gif_anim_frames[idx]
            self._gif_anim_loop_id = self.after(50, loop, (idx+1) % len(self._gif_anim_frames))
        loop()
        self.gif_progress.pack_forget()
        self.status_var.set('GIF gerado com sucesso.')
        # Salvar GIF
        params = self.get_params()
        file = filedialog.asksaveasfilename(defaultextension='.gif', filetypes=[('GIF','*.gif')], initialfile=params['gif_name'])
        if file:
            frames[0].save(file, save_all=True, append_images=frames[1:], duration=50, loop=0)
    def __init__(self):
        super().__init__()
        self.title('Infinity Fractal Generator (Tkinter)')
        self.geometry('1500x750')
        self.configure(bg='#23272e')
        self.status_var = tk.StringVar(value='')
        self._fractal_img_refs = []
        self._gif_anim_frames = []
        self.image_panel = None
        self.gif_panel = None
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
            # Novos parâmetros de calibração de cor
            'brightness': tk.DoubleVar(value=1.0),
            'contrast': tk.DoubleVar(value=1.0),
            'saturation': tk.DoubleVar(value=1.0),
            'gamma': tk.DoubleVar(value=1.0),
            'hue_shift': tk.DoubleVar(value=0.0),
        }
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        notebook = ttk.Notebook(main_frame)
        notebook.pack(side=tk.TOP, fill=tk.X, expand=False, padx=6, pady=(2, 0))
        self.notebook = notebook
        # Aba Fractal
        tab_fractal = ttk.Frame(notebook)
        notebook.add(tab_fractal, text="Fractal")
        small_font = ("Segoe UI", 9)
        fractal_options = get_fractal_types()
        palette_options = get_palette_types()
        transform_options = get_transform_types()
        # Componentes mais compactos (width reduzido, length reduzido)
        for i, (label1, widget1, label2, widget2) in enumerate([
            ('Tipo de Fractal', ttk.Combobox(tab_fractal, textvariable=self.fractal_params['fractal'], values=fractal_options, width=10, font=small_font),
             'Paleta de Cores', ttk.Combobox(tab_fractal, textvariable=self.fractal_params['palette'], values=palette_options, width=10, font=small_font)),
            ('Máximo de Iterações', ttk.Spinbox(tab_fractal, from_=10, to=1000, textvariable=self.fractal_params['iterations'], width=5, font=small_font),
             'Zoom', ttk.Entry(tab_fractal, textvariable=self.fractal_params['zoom'], width=6, font=small_font)),
            ('Centro X', ttk.Entry(tab_fractal, textvariable=self.fractal_params['center_x'], width=6, font=small_font),
             'Centro Y', ttk.Entry(tab_fractal, textvariable=self.fractal_params['center_y'], width=6, font=small_font)),
            ('Deslocamento de Cor', ttk.Scale(tab_fractal, from_=0.0, to=1.0, variable=self.fractal_params['color_shift'], orient=tk.HORIZONTAL, length=60),
             'Expoente (Power)', ttk.Entry(tab_fractal, textvariable=self.fractal_params['power'], width=6, font=small_font)),
            ('Valor de Escape (Bailout)', ttk.Entry(tab_fractal, textvariable=self.fractal_params['bailout'], width=6, font=small_font),
             'Transformação', ttk.Combobox(tab_fractal, textvariable=self.fractal_params['transform'], values=transform_options, width=10, font=small_font)),
        ]):
            row = i
            ttk.Label(tab_fractal, text=label1, font=small_font).grid(row=row, column=0, sticky='w', padx=1, pady=0)
            widget1.grid(row=row, column=1, sticky='ew', padx=1, pady=0)
            ttk.Label(tab_fractal, text=label2, font=small_font).grid(row=row, column=2, sticky='w', padx=1, pady=0)
            widget2.grid(row=row, column=3, sticky='ew', padx=1, pady=0)
        row += 1
        # Controles de calibração de cor (sem resolution, pois ttk.Scale não suporta)
        ttk.Label(tab_fractal, text='Brilho', font=small_font).grid(row=row, column=0, sticky='w', padx=1, pady=0)
        ttk.Scale(tab_fractal, from_=0.1, to=2.0, variable=self.fractal_params['brightness'], orient=tk.HORIZONTAL, length=60).grid(row=row, column=1, sticky='ew', padx=1, pady=0)
        ttk.Label(tab_fractal, text='Contraste', font=small_font).grid(row=row, column=2, sticky='w', padx=1, pady=0)
        ttk.Scale(tab_fractal, from_=0.1, to=2.0, variable=self.fractal_params['contrast'], orient=tk.HORIZONTAL, length=60).grid(row=row, column=3, sticky='ew', padx=1, pady=0)
        row += 1
        ttk.Label(tab_fractal, text='Saturação', font=small_font).grid(row=row, column=0, sticky='w', padx=1, pady=0)
        ttk.Scale(tab_fractal, from_=0.1, to=2.0, variable=self.fractal_params['saturation'], orient=tk.HORIZONTAL, length=60).grid(row=row, column=1, sticky='ew', padx=1, pady=0)
        ttk.Label(tab_fractal, text='Gamma', font=small_font).grid(row=row, column=2, sticky='w', padx=1, pady=0)
        ttk.Scale(tab_fractal, from_=0.1, to=3.0, variable=self.fractal_params['gamma'], orient=tk.HORIZONTAL, length=60).grid(row=row, column=3, sticky='ew', padx=1, pady=0)
        row += 1
        ttk.Label(tab_fractal, text='Deslocamento de Matiz (Hue)', font=small_font).grid(row=row, column=0, sticky='w', padx=1, pady=0)
        ttk.Scale(tab_fractal, from_=-0.5, to=0.5, variable=self.fractal_params['hue_shift'], orient=tk.HORIZONTAL, length=60).grid(row=row, column=1, sticky='ew', padx=1, pady=0)
        ttk.Label(tab_fractal, text='Intensidade de Cor', font=small_font).grid(row=row, column=2, sticky='w', padx=1, pady=0)
        ttk.Scale(tab_fractal, from_=0.1, to=5.0, variable=self.fractal_params['intensity'], orient=tk.HORIZONTAL, length=60).grid(row=row, column=3, sticky='ew', padx=1, pady=0)
        row += 1
        ttk.Label(tab_fractal, text='Largura (px)', font=small_font).grid(row=row, column=0, sticky='w', padx=1, pady=0)
        ttk.Entry(tab_fractal, textvariable=self.fractal_params['width'], width=6, font=small_font).grid(row=row, column=1, sticky='ew', padx=1, pady=0)
        ttk.Label(tab_fractal, text='Altura (px)', font=small_font).grid(row=row, column=2, sticky='w', padx=1, pady=0)
        ttk.Entry(tab_fractal, textvariable=self.fractal_params['height'], width=6, font=small_font).grid(row=row, column=3, sticky='ew', padx=1, pady=0)
        row += 1
        ttk.Label(tab_fractal, text='Tamanho do Pixel', font=small_font).grid(row=row, column=0, sticky='w', padx=1, pady=0)
        ttk.Entry(tab_fractal, textvariable=self.fractal_params['pixel_size'], width=6, font=small_font).grid(row=row, column=1, sticky='ew', padx=1, pady=0)
        ttk.Label(tab_fractal, text='Julia Real', font=small_font).grid(row=row, column=2, sticky='w', padx=1, pady=0)
        ttk.Entry(tab_fractal, textvariable=self.fractal_params['julia_real'], width=6, font=small_font).grid(row=row, column=3, sticky='ew', padx=1, pady=0)
        row += 1
        ttk.Label(tab_fractal, text='Julia Imag', font=small_font).grid(row=row, column=0, sticky='w', padx=1, pady=0)
        ttk.Entry(tab_fractal, textvariable=self.fractal_params['julia_imag'], width=6, font=small_font).grid(row=row, column=1, sticky='ew', padx=1, pady=0)
        button_frame = ttk.Frame(tab_fractal)
        button_frame.grid(row=row+1, column=0, columnspan=4, pady=(8, 2))
        ttk.Button(button_frame, text='Gerar Fractal', command=self.generate_fractal, width=18).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(button_frame, text='Salvar Imagem', command=self.save_image, width=18).pack(side=tk.LEFT, padx=(8, 0))
        for col in range(4):
            tab_fractal.grid_columnconfigure(col, weight=1)
        # Área de visualização
        vis_frame = ttk.Frame(main_frame)
        vis_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=2, pady=(2, 0))
        vis_frame.columnconfigure(0, weight=1)
        vis_frame.columnconfigure(1, weight=1)
        vis_frame.rowconfigure(0, weight=1)
        self.image_panel = tk.Label(vis_frame, bg="#222")
        self.image_panel.grid(row=0, column=0, padx=(0, 4), pady=(2, 0), sticky="nsew")
        self.gif_panel = tk.Label(vis_frame, bg="#222")
        self.gif_panel.grid(row=0, column=1, padx=(4, 0), pady=(2, 0), sticky="nsew")
        status_bar = ttk.Label(self, textvariable=self.status_var, anchor='w', style="TLabel")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=0, pady=0)
        # Aba GIF Animado
        tab_gif = ttk.Frame(notebook)
        notebook.add(tab_gif, text="GIF Animado")
        ttk.Label(tab_gif, text='Tipo de Animação').pack(anchor='w', padx=8, pady=2)
        anim_options = get_animation_types()
        ttk.Combobox(tab_gif, textvariable=self.fractal_params['anim_type'], values=anim_options, width=16).pack(padx=8, pady=2)
        ttk.Label(tab_gif, text='Frames do GIF').pack(anchor='w', padx=8, pady=2)
        ttk.Spinbox(tab_gif, from_=5, to=120, textvariable=self.fractal_params['num_frames'], width=10).pack(padx=8, pady=2)
        ttk.Label(tab_gif, text='Nome do GIF').pack(anchor='w', padx=8, pady=2)
        ttk.Entry(tab_gif, textvariable=self.fractal_params['gif_name'], width=18).pack(padx=8, pady=2)
        self.gif_progress = ttk.Progressbar(tab_gif, orient='horizontal', mode='determinate', length=200)
        self.gif_progress.pack(padx=8, pady=4)
        self.gif_progress.pack_forget()
        ttk.Button(tab_gif, text='Gerar GIF', command=self.generate_gif).pack(fill=tk.X, padx=8, pady=8)

# Para rodar:
def main():
    app = FractalApp()
    app.mainloop()

if __name__ == "__main__":
    main()
