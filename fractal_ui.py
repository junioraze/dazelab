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
import io
from fractal_core import get_fractal_types, get_fractal_func
from palettes import get_palette_types, get_palette_func
from fractal_animations import get_animation_types, get_animation_func
from transforms import get_transform_types
import persistence

# Tema visual agradável

def set_modern_dark_style(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TFrame", background="#23272e")
    style.configure("TLabel", background="#23272e", foreground="#b6eaff", font=("Segoe UI", 11, "bold"))
    style.configure("TButton", background="#1e2a38", foreground="#b6eaff", font=("Segoe UI", 10, "bold"), borderwidth=1, relief="flat")
    style.map("TButton", background=[("active", "#2e3a48")], foreground=[("active", "#fff")])
    style.configure("TCombobox", fieldbackground="#1a1d22", background="#1a1d22", foreground="#b6eaff", selectbackground="#23272e", selectforeground="#fff")
    style.configure("TEntry", fieldbackground="#1a1d22", background="#1a1d22", foreground="#b6eaff")
    style.configure("TSpinbox", fieldbackground="#1a1d22", background="#1a1d22", foreground="#b6eaff")
    style.configure("TNotebook", background="#23272e", tabposition='n')
    style.configure("TNotebook.Tab", background="#1e2a38", foreground="#b6eaff", font=("Segoe UI", 10, "bold"))
    style.map("TNotebook.Tab", background=[("selected", "#2e3a48")], foreground=[("selected", "#fff")])
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
        if not hasattr(self, 'image_panel') or self.image_panel is None:
            return
        self._last_fractal_img = img
        if img is None:
            self.image_panel.config(image='', text='Imagem não gerada', bg='#a00', fg='#fff')
            self.image_panel.image = None
            self.status_var.set('Erro ao gerar fractal.')
            return
        if not hasattr(self, '_fractal_img_refs'):
            self._fractal_img_refs = []
        img_resized = img.resize((600, 400))
        img_tk = ImageTk.PhotoImage(img_resized)
        self._fractal_img_refs.append(img_tk)
        self.image_panel.config(image=img_tk, text='', bg='#222', fg='#b6eaff')
        self.image_panel.image = img_tk
        self.image_panel.update_idletasks()
        if len(self._fractal_img_refs) > 5:
            self._fractal_img_refs = self._fractal_img_refs[-5:]
        self.status_var.set('Fractal gerado com sucesso.')

        # Garante que o painel está visível e com highlight
        self.image_panel.lift()
        self.image_panel.update()

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
        self.gif_progress['value'] = value
        self.status_var.set(f'Gerando GIF... ({value}/{total})')
        self.gif_progress.update_idletasks()

    def _show_gif_frames(self, frames):
        if not hasattr(self, 'gif_panel') or self.gif_panel is None:
            return
        if not frames:
            self.gif_panel.config(image='', text='GIF não gerado', bg='#a00', fg='#fff')
            self.gif_panel.image = None
            self.status_var.set('Erro ao gerar GIF.')
            return
        self._last_gif_frames = frames  # Salva os frames para persistência
        self._gif_anim_frames = [ImageTk.PhotoImage(f.resize((600, 400))) for f in frames]
        self._gif_anim_running = True
        def loop(idx=0):
            if not hasattr(self, '_gif_anim_frames') or not self._gif_anim_running or not self._gif_anim_frames:
                return
            self.gif_panel.config(image=self._gif_anim_frames[idx], text='', bg='#181c20')
            self.gif_panel.image = self._gif_anim_frames[idx]
            self.gif_panel.after(100, loop, (idx+1)%len(self._gif_anim_frames))
        loop()
        self.status_var.set('GIF animado gerado com sucesso.')
            
    def _save_ser(self):
        # Pega campos
        nome = self.ser_fields['nome'].get()
        descricao = self.ser_fields['descricao'].get()
        tipo1 = self.ser_fields['tipo1'].get()
        tipo2 = self.ser_fields['tipo2'].get()
        try:
            vida = int(self.ser_fields['vida'].get())
            poder = int(self.ser_fields['poder'].get())
            resistencia = int(self.ser_fields['resistencia'].get())
            sabedoria = int(self.ser_fields['sabedoria'].get())
            espirito = int(self.ser_fields['espirito'].get())
            impeto = int(self.ser_fields['impeto'].get())
        except Exception:
            messagebox.showerror('Erro', 'Atributos devem ser números inteiros.')
            return
        # Pega fractal atual
        if not hasattr(self, '_last_fractal_img') or self._last_fractal_img is None:
            messagebox.showerror('Erro', 'Gere um fractal antes de salvar.')
            return
        img = self._last_fractal_img
        # Pega gif atual (se houver)
        gif_bytes = None
        if hasattr(self, '_last_gif_frames') and self._last_gif_frames:
            # import io (moved to global imports)
            frames = self._last_gif_frames
            buf = io.BytesIO()
            frames[0].save(buf, save_all=True, append_images=frames[1:], format='GIF', duration=50, loop=0)
            gif_bytes = buf.getvalue()
        # Pega params
        params = self.get_params()
        persistence.save_ser(nome, descricao, tipo1, tipo2, vida, poder, resistencia, sabedoria, espirito, impeto, params, img, gif_bytes)
        messagebox.showinfo('Sucesso', f'Ser "{nome}" salvo com sucesso!')
        self.status_var.set(f'Ser "{nome}" salvo!')
        self._refresh_seres_list()
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

        # Notebook de abas ocupa o centro/topo
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=6, pady=(2, 0))
        self.notebook = notebook

        # Painéis de imagem e GIF SEMPRE visíveis na parte inferior do main_frame
        vis_frame = ttk.Frame(main_frame)
        vis_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=2, pady=(2, 0))
        vis_frame.grid_columnconfigure(0, minsize=600, weight=1)
        vis_frame.grid_columnconfigure(1, minsize=600, weight=1)
        vis_frame.grid_rowconfigure(0, minsize=400, weight=1)

        # Frame para imagem
        img_frame = tk.Frame(vis_frame, bg="#181c20", width=600, height=400)
        img_frame.grid(row=0, column=0, padx=(0, 4), pady=(2, 0), sticky="nsew")
        img_frame.grid_propagate(False)
        self.image_panel = tk.Label(
            img_frame, bg="#181c20", bd=2, relief="groove",
            highlightbackground="#b6eaff", highlightthickness=2,
            anchor='center', justify='center',
            text="Imagem Fractal", fg="#b6eaff", font=("Segoe UI", 16, "bold")
        )
        self.image_panel.place(relx=0.5, rely=0.5, anchor="center", width=600, height=400)

        # Frame para GIF
        gif_frame = tk.Frame(vis_frame, bg="#181c20", width=600, height=400)
        gif_frame.grid(row=0, column=1, padx=(4, 0), pady=(2, 0), sticky="nsew")
        gif_frame.grid_propagate(False)
        self.gif_panel = tk.Label(
            gif_frame, bg="#181c20", bd=2, relief="groove",
            highlightbackground="#b6eaff", highlightthickness=2,
            anchor='center', justify='center',
            text="GIF Animado", fg="#b6eaff", font=("Segoe UI", 16, "bold")
        )
        self.gif_panel.place(relx=0.5, rely=0.5, anchor="center", width=600, height=400)

        # Placeholder sempre visível
        self.image_panel.config(image='', text='Imagem Fractal', bg='#181c20', fg='#b6eaff', font=("Segoe UI", 16, "bold"))
        self.gif_panel.config(image='', text='GIF Animado', bg='#181c20', fg='#b6eaff', font=("Segoe UI", 16, "bold"))

        # Expansão correta do main_frame
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=0)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
            # Aba Fractal
        tab_fractal = ttk.Frame(notebook)
        notebook.add(tab_fractal, text="Fractal")
        small_font = ("Segoe UI", 9)
        slider_value_font = ("Segoe UI", 12, "bold")
        fractal_options = get_fractal_types()
        palette_options = get_palette_types()
        transform_options = get_transform_types()
        # Campos da aba Fractal com Spinbox de 0.1 para DoubleVar
        row = 0
        ttk.Label(tab_fractal, text='Tipo de Fractal', font=("Segoe UI", 11, "bold"), foreground="#7fffd4").grid(row=row, column=0, sticky='w', padx=1, pady=2)
        ttk.Combobox(tab_fractal, textvariable=self.fractal_params['fractal'], values=fractal_options, width=12, font=("Segoe UI", 11)).grid(row=row, column=1, sticky='ew', padx=1, pady=2)
        ttk.Label(tab_fractal, text='Paleta de Cores', font=("Segoe UI", 11, "bold"), foreground="#7fffd4").grid(row=row, column=2, sticky='w', padx=1, pady=2)
        ttk.Combobox(tab_fractal, textvariable=self.fractal_params['palette'], values=palette_options, width=12, font=("Segoe UI", 11)).grid(row=row, column=3, sticky='ew', padx=1, pady=2)
        row += 1
        ttk.Label(tab_fractal, text='Máximo de Iterações', font=small_font).grid(row=row, column=0, sticky='e', padx=8, pady=4)
        ttk.Scale(tab_fractal, from_=10, to=10000, orient='horizontal', variable=self.fractal_params['iterations'], length=180).grid(row=row, column=1, sticky='ew', padx=8, pady=4)
        ttk.Label(tab_fractal, textvariable=self.fractal_params['iterations'], font=slider_value_font, foreground='#7fffd4').grid(row=row, column=1, sticky='e', padx=(120,8), pady=4)
        ttk.Label(tab_fractal, text='Zoom', font=small_font).grid(row=row, column=2, sticky='e', padx=8, pady=4)
        ttk.Scale(tab_fractal, from_=0.01, to=20.0, orient='horizontal', variable=self.fractal_params['zoom'], length=180).grid(row=row, column=3, sticky='ew', padx=8, pady=4)
        ttk.Label(tab_fractal, textvariable=self.fractal_params['zoom'], font=slider_value_font, foreground='#7fffd4').grid(row=row, column=3, sticky='e', padx=(120,8), pady=4)
        row += 1
        ttk.Label(tab_fractal, text='Centro X', font=small_font).grid(row=row, column=0, sticky='e', padx=8, pady=4)
        ttk.Scale(tab_fractal, from_=-10.0, to=10.0, orient='horizontal', variable=self.fractal_params['center_x'], length=180).grid(row=row, column=1, sticky='ew', padx=8, pady=4)
        ttk.Label(tab_fractal, textvariable=self.fractal_params['center_x'], font=slider_value_font, foreground='#7fffd4').grid(row=row, column=1, sticky='e', padx=(120,8), pady=4)
        ttk.Label(tab_fractal, text='Centro Y', font=small_font).grid(row=row, column=2, sticky='e', padx=8, pady=4)
        ttk.Scale(tab_fractal, from_=-10.0, to=10.0, orient='horizontal', variable=self.fractal_params['center_y'], length=180).grid(row=row, column=3, sticky='ew', padx=8, pady=4)
        ttk.Label(tab_fractal, textvariable=self.fractal_params['center_y'], font=slider_value_font, foreground='#7fffd4').grid(row=row, column=3, sticky='e', padx=(120,8), pady=4)
        row += 1
        ttk.Label(tab_fractal, text='Deslocamento de Cor', font=small_font).grid(row=row, column=0, sticky='e', padx=8, pady=4)
        ttk.Scale(tab_fractal, from_=0.0, to=1.0, orient='horizontal', variable=self.fractal_params['color_shift'], length=180).grid(row=row, column=1, sticky='ew', padx=8, pady=4)
        ttk.Label(tab_fractal, textvariable=self.fractal_params['color_shift'], font=slider_value_font, foreground='#7fffd4').grid(row=row, column=1, sticky='e', padx=(120,8), pady=4)
        ttk.Label(tab_fractal, text='Expoente (Power)', font=small_font).grid(row=row, column=2, sticky='e', padx=8, pady=4)
        ttk.Scale(tab_fractal, from_=0.1, to=10.0, orient='horizontal', variable=self.fractal_params['power'], length=180).grid(row=row, column=3, sticky='ew', padx=8, pady=4)
        ttk.Label(tab_fractal, textvariable=self.fractal_params['power'], font=slider_value_font, foreground='#7fffd4').grid(row=row, column=3, sticky='e', padx=(120,8), pady=4)
        row += 1
        ttk.Label(tab_fractal, text='Valor de Escape (Bailout)', font=small_font).grid(row=row, column=0, sticky='e', padx=8, pady=4)
        ttk.Scale(tab_fractal, from_=0.1, to=100.0, orient='horizontal', variable=self.fractal_params['bailout'], length=180).grid(row=row, column=1, sticky='ew', padx=8, pady=4)
        ttk.Label(tab_fractal, textvariable=self.fractal_params['bailout'], font=slider_value_font, foreground='#7fffd4').grid(row=row, column=1, sticky='e', padx=(120,8), pady=4)
        ttk.Label(tab_fractal, text='Transformação', font=small_font).grid(row=row, column=2, sticky='e', padx=8, pady=4)
        ttk.Combobox(tab_fractal, textvariable=self.fractal_params['transform'], values=transform_options, width=12, font=small_font).grid(row=row, column=3, sticky='ew', padx=8, pady=4)
        row += 1
        ttk.Label(tab_fractal, text='Intensidade de Cor', font=small_font).grid(row=row, column=0, sticky='e', padx=8, pady=4)
        ttk.Scale(tab_fractal, from_=0.1, to=5.0, orient='horizontal', variable=self.fractal_params['intensity'], length=180).grid(row=row, column=1, sticky='ew', padx=8, pady=4)
        ttk.Label(tab_fractal, textvariable=self.fractal_params['intensity'], font=slider_value_font, foreground='#7fffd4').grid(row=row, column=1, sticky='e', padx=(120,8), pady=4)
        ttk.Label(tab_fractal, text='Largura (px)', font=small_font).grid(row=row, column=2, sticky='e', padx=8, pady=4)
        ttk.Scale(tab_fractal, from_=100, to=3000, orient='horizontal', variable=self.fractal_params['width'], length=180).grid(row=row, column=3, sticky='ew', padx=8, pady=4)
        ttk.Label(tab_fractal, textvariable=self.fractal_params['width'], font=slider_value_font, foreground='#7fffd4').grid(row=row, column=3, sticky='e', padx=(120,8), pady=4)
        row += 1
        ttk.Label(tab_fractal, text='Altura (px)', font=small_font).grid(row=row, column=0, sticky='e', padx=8, pady=4)
        ttk.Scale(tab_fractal, from_=100, to=3000, orient='horizontal', variable=self.fractal_params['height'], length=180).grid(row=row, column=1, sticky='ew', padx=8, pady=4)
        ttk.Label(tab_fractal, textvariable=self.fractal_params['height'], font=slider_value_font, foreground='#7fffd4').grid(row=row, column=1, sticky='e', padx=(120,8), pady=4)
        ttk.Label(tab_fractal, text='Tamanho do Pixel', font=small_font).grid(row=row, column=2, sticky='e', padx=8, pady=4)
        ttk.Scale(tab_fractal, from_=1, to=20, orient='horizontal', variable=self.fractal_params['pixel_size'], length=180).grid(row=row, column=3, sticky='ew', padx=8, pady=4)
        ttk.Label(tab_fractal, textvariable=self.fractal_params['pixel_size'], font=slider_value_font, foreground='#7fffd4').grid(row=row, column=3, sticky='e', padx=(120,8), pady=4)
        row += 1
        ttk.Label(tab_fractal, text='Julia Real', font=small_font).grid(row=row, column=0, sticky='e', padx=8, pady=4)
        ttk.Scale(tab_fractal, from_=-2.0, to=2.0, orient='horizontal', variable=self.fractal_params['julia_real'], length=180).grid(row=row, column=1, sticky='ew', padx=8, pady=4)
        ttk.Label(tab_fractal, textvariable=self.fractal_params['julia_real'], font=slider_value_font, foreground='#7fffd4').grid(row=row, column=1, sticky='e', padx=(120,8), pady=4)
        ttk.Label(tab_fractal, text='Julia Imag', font=small_font).grid(row=row, column=2, sticky='e', padx=8, pady=4)
        ttk.Scale(tab_fractal, from_=-2.0, to=2.0, orient='horizontal', variable=self.fractal_params['julia_imag'], length=180).grid(row=row, column=3, sticky='ew', padx=8, pady=4)
        ttk.Label(tab_fractal, textvariable=self.fractal_params['julia_imag'], font=slider_value_font, foreground='#7fffd4').grid(row=row, column=3, sticky='e', padx=(120,8), pady=4)
        row += 1
        # Controles de calibração de cor
        ttk.Label(tab_fractal, text='Brilho', font=small_font).grid(row=row, column=0, sticky='e', padx=8, pady=4)
        ttk.Scale(tab_fractal, from_=0.1, to=2.0, orient='horizontal', variable=self.fractal_params['brightness'], length=180).grid(row=row, column=1, sticky='ew', padx=8, pady=4)
        ttk.Label(tab_fractal, textvariable=self.fractal_params['brightness'], font=slider_value_font, foreground='#7fffd4').grid(row=row, column=1, sticky='e', padx=(120,8), pady=4)
        ttk.Label(tab_fractal, text='Contraste', font=small_font).grid(row=row, column=2, sticky='e', padx=8, pady=4)
        ttk.Scale(tab_fractal, from_=0.1, to=2.0, orient='horizontal', variable=self.fractal_params['contrast'], length=180).grid(row=row, column=3, sticky='ew', padx=8, pady=4)
        ttk.Label(tab_fractal, textvariable=self.fractal_params['contrast'], font=slider_value_font, foreground='#7fffd4').grid(row=row, column=3, sticky='e', padx=(120,8), pady=4)
        row += 1
        ttk.Label(tab_fractal, text='Saturação', font=small_font).grid(row=row, column=0, sticky='e', padx=8, pady=4)
        ttk.Scale(tab_fractal, from_=0.1, to=2.0, orient='horizontal', variable=self.fractal_params['saturation'], length=180).grid(row=row, column=1, sticky='ew', padx=8, pady=4)
        ttk.Label(tab_fractal, textvariable=self.fractal_params['saturation'], font=slider_value_font, foreground='#7fffd4').grid(row=row, column=1, sticky='e', padx=(120,8), pady=4)
        ttk.Label(tab_fractal, text='Gamma', font=small_font).grid(row=row, column=2, sticky='e', padx=8, pady=4)
        ttk.Scale(tab_fractal, from_=0.1, to=3.0, orient='horizontal', variable=self.fractal_params['gamma'], length=180).grid(row=row, column=3, sticky='ew', padx=8, pady=4)
        ttk.Label(tab_fractal, textvariable=self.fractal_params['gamma'], font=slider_value_font, foreground='#7fffd4').grid(row=row, column=3, sticky='e', padx=(120,8), pady=4)
        row += 1
        ttk.Label(tab_fractal, text='Deslocamento de Matiz (Hue)', font=small_font).grid(row=row, column=0, sticky='e', padx=8, pady=4)
        ttk.Scale(tab_fractal, from_=-0.5, to=0.5, orient='horizontal', variable=self.fractal_params['hue_shift'], length=180).grid(row=row, column=1, sticky='ew', padx=8, pady=4)
        ttk.Label(tab_fractal, textvariable=self.fractal_params['hue_shift'], font=slider_value_font, foreground='#7fffd4').grid(row=row, column=1, sticky='e', padx=(120,8), pady=4)

        button_frame = ttk.Frame(tab_fractal)
        button_frame.grid(row=row+1, column=0, columnspan=4, pady=(8, 2))
        ttk.Button(button_frame, text='Gerar Fractal', command=self.generate_fractal, width=16).pack(side=tk.LEFT, padx=(0, 6))
        for col in range(4):
            tab_fractal.grid_columnconfigure(col, weight=1)

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

        # Aba Persistir Ser (formulário de cadastro, usando os mesmos painéis de imagem/gif)
        tab_persistir = ttk.Frame(notebook)
        notebook.add(tab_persistir, text="Persistir Ser")


        # Frame principal horizontal para formulário e botão
        persistir_main = ttk.Frame(tab_persistir)
        persistir_main.pack(fill=tk.BOTH, expand=True)

        # Frame do formulário (esquerda)
        form_frame = ttk.Frame(persistir_main)
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=12, pady=8)
        self.ser_fields = {}
        # Campos em duas colunas
        labels = [
            ("Nome do Ser", "nome"),
            ("Descrição", "descricao"),
            ("Tipo 1", "tipo1"),
            ("Tipo 2", "tipo2"),
            ("VIDA", "vida"),
            ("PODER", "poder"),
            ("RESISTENCIA", "resistencia"),
            ("SABEDORIA", "sabedoria"),
            ("ESPIRITO", "espirito"),
            ("IMPETO", "impeto")
        ]
        for i, (label, key) in enumerate(labels):
            col = 0 if i < len(labels)//2 + len(labels)%2 else 2
            row = i if i < len(labels)//2 + len(labels)%2 else i - (len(labels)//2 + len(labels)%2)
            ttk.Label(form_frame, text=label).grid(row=row, column=col, sticky='w', padx=2, pady=2)
            entry = ttk.Entry(form_frame, width=16)
            entry.grid(row=row, column=col+1, sticky='ew', padx=2, pady=2)
            self.ser_fields[key] = entry
        # Ajustar espaçamento
        for c in range(4):
            form_frame.grid_columnconfigure(c, weight=1)

        # Frame do botão (direita)
        btn_frame = ttk.Frame(persistir_main)
        btn_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=8)
        salvar_btn = ttk.Button(btn_frame, text="Salvar Ser (com fractal e gif)", command=self._save_ser, width=22)
        salvar_btn.pack(side=tk.TOP, anchor='n', pady=24)

        # Reutiliza os painéis de imagem/gif já criados (self.image_panel, self.gif_panel)
        # Não precisa criar novos, pois já estão visíveis acima

        # Aba Seres Salvos (listagem e visualização)
        tab_seres = ttk.Frame(notebook)
        notebook.add(tab_seres, text="Seres Salvos")
        # Layout horizontal compacto
        left_frame = ttk.Frame(tab_seres)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=6)
        right_frame = ttk.Frame(tab_seres)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=6)

        # Filtros
        filter_frame = ttk.Frame(left_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 4))
        self.filter_attr = tk.StringVar(value='nome')
        self.filter_value = tk.StringVar(value='')
        ttk.Label(filter_frame, text="Filtrar por:").pack(side=tk.LEFT, padx=2)
        ttk.Combobox(filter_frame, textvariable=self.filter_attr, values=["nome","tipo1","tipo2"], width=8).pack(side=tk.LEFT, padx=2)
        ttk.Entry(filter_frame, textvariable=self.filter_value, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(filter_frame, text="Filtrar", command=self._refresh_seres_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(filter_frame, text="Limpar", command=self._clear_seres_filter).pack(side=tk.LEFT, padx=2)

        # Listbox de seres
        # Listbox estilizada para dark mode
        self.seres_listbox = tk.Listbox(
            left_frame, width=28, height=18,
            bg="#181c20", fg="#b6eaff", selectbackground="#2e3a48", selectforeground="#fff",
            highlightbackground="#b6eaff", highlightcolor="#7fffd4", relief="flat", bd=2,
            font=("Segoe UI", 10, "bold")
        )
        self.seres_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 4))
        self.seres_listbox.bind('<<ListboxSelect>>', self._on_ser_select)

        # Painel de atributos
        attr_frame = ttk.Frame(right_frame)
        attr_frame.pack(fill=tk.X, pady=(0, 4))
        self.ser_attr_table = ttk.Frame(attr_frame)
        self.ser_attr_table.pack(fill=tk.X)

        # Painel de imagem/gif
        img_gif_frame = ttk.Frame(right_frame)
        img_gif_frame.pack(fill=tk.X, pady=(0, 4))

        # Painéis de imagem/gif com tamanho fixo e não expansível
        self._ser_img_panel_size = (200, 140)
        self.ser_img_panel = tk.Label(img_gif_frame, bg="#222", width=self._ser_img_panel_size[0], height=self._ser_img_panel_size[1], anchor='center')
        self.ser_img_panel.pack(side=tk.LEFT, padx=(0, 8), pady=0, ipadx=0, ipady=0)
        self.ser_gif_panel = tk.Label(img_gif_frame, bg="#222", width=self._ser_img_panel_size[0], height=self._ser_img_panel_size[1], anchor='center')
        self.ser_gif_panel.pack(side=tk.LEFT, padx=(8, 0), pady=0, ipadx=0, ipady=0)

        # Frame para ações (deletar) - garantir que right_frame existe
        self._ser_action_frame = None
        if 'right_frame' in locals() or 'right_frame' in globals():
            self._ser_action_frame = ttk.Frame(right_frame)
            self._ser_action_frame.pack(fill=tk.X, pady=(2, 0))

        # Botão de deletar ser selecionado (abaixo da lista)
        self.delete_ser_btn = ttk.Button(left_frame, text="Deletar Ser Selecionado", command=self._delete_selected_ser)
        self.delete_ser_btn.pack(fill=tk.X, pady=(2, 0))

        self._refresh_seres_list()
    def _delete_selected_ser(self):
        # Deleta o ser atualmente selecionado na lista
        if not self.seres_listbox.curselection():
            messagebox.showinfo("Atenção", "Selecione um ser para deletar.")
            return
        idx = self.seres_listbox.curselection()[0]
        seres = getattr(self, '_filtered_seres', persistence.list_seres())
        if idx >= len(seres):
            return
        ser_id = seres[idx]['id']
        self._delete_ser(ser_id)


    def _abrir_cadastro_ser(self):
        if self.cadastro_ser_frame is not None:
            self.cadastro_ser_frame.destroy()
        self.cadastro_ser_frame = tk.Toplevel(self)
        self.cadastro_ser_frame.title("Cadastrar novo Ser")
        self.cadastro_ser_frame.geometry("400x420")
        self.cadastro_ser_frame.configure(bg="#23272e")
        form = ttk.Frame(self.cadastro_ser_frame)
        form.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        self.ser_fields = {}
        row = 0
        for label, key in [
            ("Nome do Ser", "nome"),
            ("Descrição", "descricao"),
            ("Tipo 1", "tipo1"),
            ("Tipo 2", "tipo2"),
            ("VIDA", "vida"),
            ("PODER", "poder"),
            ("RESISTENCIA", "resistencia"),
            ("SABEDORIA", "sabedoria"),
            ("ESPIRITO", "espirito"),
            ("IMPETO", "impeto")
        ]:
            ttk.Label(form, text=label).grid(row=row, column=0, sticky='w', padx=2, pady=2)
            entry = ttk.Entry(form, width=24)
            entry.grid(row=row, column=1, sticky='ew', padx=2, pady=2)
            self.ser_fields[key] = entry
            row += 1
        ttk.Button(form, text="Salvar Ser (com fractal e gif)", command=self._save_ser).grid(row=row, column=0, columnspan=2, pady=12)
        ttk.Button(form, text="Cancelar", command=self.cadastro_ser_frame.destroy).grid(row=row+1, column=0, columnspan=2, pady=2)

    def _refresh_seres_list(self):
        self.seres_listbox.delete(0, tk.END)
        # Filtro
        attr = self.filter_attr.get() if hasattr(self, 'filter_attr') else 'nome'
        value = self.filter_value.get() if hasattr(self, 'filter_value') else ''
        seres = persistence.list_seres()
        if value:
            value_lower = value.lower()
            def match(ser):
                v = str(ser.get(attr, '')).lower()
                return value_lower in v
            seres = [ser for ser in seres if match(ser)]
        if not seres:
            self.seres_listbox.insert(tk.END, "Nenhum ser encontrado.")
            self.status_var.set("Nenhum ser encontrado.")
        else:
            for ser in seres:
                self.seres_listbox.insert(tk.END, f"[{ser['id']}] {ser['nome']}")
        self._filtered_seres = seres

    def _clear_seres_filter(self):
        if hasattr(self, 'filter_value'):
            self.filter_value.set('')
        self._refresh_seres_list()

    def _on_ser_select(self, event):
        # Atualiza apenas os painéis já existentes, sem alterar layout
        if not self.seres_listbox.curselection():
            return
        idx = self.seres_listbox.curselection()[0]
        seres = getattr(self, '_filtered_seres', persistence.list_seres())
        if idx >= len(seres):
            return
        ser_id = seres[idx]['id']
        ser = persistence.load_ser(ser_id)
        # Limpa tabela de atributos
        for w in self.ser_attr_table.winfo_children():
            w.destroy()
        # Cabeçalho
        ttk.Label(self.ser_attr_table, text="Atributo", font=("Segoe UI", 10, "bold"), anchor='w').grid(row=0, column=0, sticky='w', padx=2, pady=1)
        ttk.Label(self.ser_attr_table, text="Valor", font=("Segoe UI", 10, "bold"), anchor='w').grid(row=0, column=1, sticky='w', padx=2, pady=1)
        # Linhas de atributos
        attrs = [
            ("Nome", ser['nome']),
            ("Tipo 1", ser['tipo1']),
            ("Tipo 2", ser['tipo2']),
            ("Descrição", ser['descricao']),
            ("VIDA", ser['vida']),
            ("PODER", ser['poder']),
            ("RESISTENCIA", ser['resistencia']),
            ("SABEDORIA", ser['sabedoria']),
            ("ESPIRITO", ser['espirito']),
            ("IMPETO", ser['impeto'])
        ]
        for i, (k, v) in enumerate(attrs, start=1):
            ttk.Label(self.ser_attr_table, text=k, anchor='w').grid(row=i, column=0, sticky='w', padx=2, pady=1)
            ttk.Label(self.ser_attr_table, text=str(v), anchor='w').grid(row=i, column=1, sticky='w', padx=2, pady=1)
        # Parâmetros do fractal (resumido)
        fractal_params = ser['params']
        param_str = ', '.join(f"{k}={v}" for k, v in list(fractal_params.items())[:6])
        ttk.Label(self.ser_attr_table, text="Parâmetros Fractal", font=("Segoe UI", 10, "bold"), anchor='w').grid(row=len(attrs)+1, column=0, sticky='w', padx=2, pady=1)
        ttk.Label(self.ser_attr_table, text=param_str+" ...", anchor='w').grid(row=len(attrs)+1, column=1, sticky='w', padx=2, pady=1)

        # Atualiza imagem no painel existente
        img = ser['img'].copy()
        max_w, max_h = self._ser_img_panel_size
        img.thumbnail((max_w, max_h), Image.LANCZOS)
        self._ser_img_tk = ImageTk.PhotoImage(img)
        self.ser_img_panel.config(image=self._ser_img_tk, width=max_w, height=max_h)
        self.ser_img_panel.image = self._ser_img_tk

        # Atualiza gif no painel existente
        self.ser_gif_panel.config(image='')
        self.ser_gif_panel.image = None
        self._ser_gif_tk_frames = []
        if ser['gif_bytes']:
            try:
                gif = Image.open(io.BytesIO(ser['gif_bytes']))
                frames = []
                while True:
                    frames.append(gif.copy())
                    gif.seek(len(frames))
            except EOFError:
                pass
            except Exception:
                frames = []
            if not frames:
                try:
                    gif = Image.open(io.BytesIO(ser['gif_bytes']))
                    frames = [gif.copy()]
                except Exception:
                    frames = []
            if frames:
                gif_resized = []
                for f in frames:
                    f2 = f.copy()
                    f2.thumbnail((max_w, max_h), Image.LANCZOS)
                    gif_resized.append(f2)
                self._ser_gif_tk_frames = [ImageTk.PhotoImage(f) for f in gif_resized]
                def gif_loop(idx=0):
                    if not hasattr(self, '_ser_gif_tk_frames') or not self._ser_gif_tk_frames:
                        return
                    self.ser_gif_panel.config(image=self._ser_gif_tk_frames[idx], width=max_w, height=max_h)
                    self.ser_gif_panel.image = self._ser_gif_tk_frames[idx]
                    self.ser_gif_panel.after(120, gif_loop, (idx+1)%len(self._ser_gif_tk_frames))
                gif_loop()

        # Atualiza botões de ação (deletar)
        if not hasattr(self, '_ser_action_frame'):
            self._ser_action_frame = ttk.Frame(self.ser_gif_panel.master)
            self._ser_action_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(8,0))
        for w in self._ser_action_frame.winfo_children():
            w.destroy()
        ttk.Button(self._ser_action_frame, text="Deletar Ser", command=lambda: self._delete_ser(ser['id'])).pack(side=tk.LEFT, padx=4)

    def _delete_ser(self, ser_id):
        if messagebox.askyesno("Deletar Ser", "Tem certeza que deseja deletar este ser?"):
            persistence.delete_ser(ser_id)
            self._refresh_seres_list()
            # Limpa apenas os painéis de imagem/gif
            self.ser_img_panel.config(image='')
            self.ser_img_panel.image = None
            self.ser_gif_panel.config(image='')
            self.ser_gif_panel.image = None

# Para rodar:
def main():
    app = FractalApp()
    app.mainloop()

if __name__ == "__main__":
    main()
