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
    def _on_tab_changed(self, event=None):
        # Esconde painéis de imagem/GIF na aba Análise, mostra nas demais
        tab = self.notebook.tab(self.notebook.select(), 'text')
        if hasattr(self, 'vis_frame'):
            if tab == 'Análise':
                self.vis_frame.grid_remove()
            else:
                self.vis_frame.grid()

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
        # Permitir cancelar geração
        self._gif_cancel = False
        params = self.get_params()
        num_frames = params['num_frames']
        anim_type = params['anim_type']
        frames = []
        self.status_var.set('Gerando GIF...')
        self.gif_progress['maximum'] = num_frames
        self.gif_progress['value'] = 0
        self.gif_progress.pack()
        def cancel():
            self._gif_cancel = True
            self.status_var.set('Geração de GIF cancelada.')
        # Botão de cancelar
        if not hasattr(self, '_gif_cancel_btn') or not self._gif_cancel_btn.winfo_exists():
            self._gif_cancel_btn = ttk.Button(self.notebook.nametowidget(self.notebook.tabs()[1]), text='Cancelar', command=cancel)
            self._gif_cancel_btn.pack(padx=8, pady=2)
        def worker():
            import gc
            from PIL import Image
            for i in range(num_frames):
                if self._gif_cancel:
                    break
                frame_params = params.copy()
                anim_func = get_animation_func(anim_type)
                img = anim_func(frame_params, i, num_frames)
                # Otimizar: converter para P mode (paleta) para economizar RAM
                if img.mode != 'P':
                    img = img.convert('P', palette=Image.ADAPTIVE)
                frames.append(img)
                if i % 5 == 0:
                    gc.collect()
                self.after(0, lambda v=i+1: self._update_gif_progress(v, num_frames))
            self.after(0, lambda: self._show_gif_frames(frames))
            # Esconde botão cancelar
            if hasattr(self, '_gif_cancel_btn') and self._gif_cancel_btn.winfo_exists():
                self._gif_cancel_btn.pack_forget()
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
        # Limitar quantidade de frames exibidos na animação para não travar a interface
        max_anim_frames = 60
        if len(frames) > max_anim_frames:
            step = max(1, len(frames)//max_anim_frames)
            anim_frames = frames[::step]
        else:
            anim_frames = frames
        self._gif_anim_frames = [ImageTk.PhotoImage(f.resize((600, 400))) for f in anim_frames]
        self._gif_anim_running = True
        def loop(idx=0):
            # Protege contra lista vazia ou índice fora do range
            if not hasattr(self, '_gif_anim_frames') or not self._gif_anim_running or not self._gif_anim_frames:
                return
            if idx >= len(self._gif_anim_frames):
                idx = 0
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
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=6, pady=(2, 0))
        self.notebook = notebook

        # --- Aba Fractal ---
        tab_fractal = ttk.Frame(notebook)
        notebook.add(tab_fractal, text="Fractal")
        # Layout Fractal: 6 colunas, centralizado
        controls_frame = ttk.Frame(tab_fractal)
        controls_frame.pack(pady=12, padx=12, anchor="n")
        # Lista de parâmetros (label, widget, var, tipo, min, max, step)
        params = [
            ("Tipo de Fractal:", ttk.Combobox, 'fractal', get_fractal_types(), None, None, None),
            ("Paleta de Cores:", ttk.Combobox, 'palette', get_palette_types(), None, None, None),
            ("Iterações:", ttk.Scale, 'iterations', None, 10, 1000, 1),
            ("Zoom:", ttk.Scale, 'zoom', None, 0.1, 10.0, 0.01),
            ("Centro X:", ttk.Scale, 'center_x', None, -2.0, 2.0, 0.01),
            ("Centro Y:", ttk.Scale, 'center_y', None, -2.0, 2.0, 0.01),
            ("Color Shift:", ttk.Scale, 'color_shift', None, 0.0, 1.0, 0.01),
            ("Power:", ttk.Scale, 'power', None, 1.0, 8.0, 0.01),
            ("Bailout:", ttk.Scale, 'bailout', None, 2.0, 100.0, 0.01),
            ("Transformação:", ttk.Combobox, 'transform', get_transform_types(), None, None, None),
            ("Intensidade:", ttk.Scale, 'intensity', None, 0.1, 5.0, 0.01),
            ("Largura:", ttk.Scale, 'width', None, 200, 1200, 1),
            ("Altura:", ttk.Scale, 'height', None, 200, 1200, 1),
            ("Pixel Size:", ttk.Scale, 'pixel_size', None, 0.5, 8.0, 0.01),
            ("Julia Real:", ttk.Scale, 'julia_real', None, -2.0, 2.0, 0.01),
            ("Julia Imag:", ttk.Scale, 'julia_imag', None, -2.0, 2.0, 0.01),
            ("Brilho:", ttk.Scale, 'brightness', None, 0.1, 2.0, 0.01),
            ("Contraste:", ttk.Scale, 'contrast', None, 0.1, 2.0, 0.01),
            ("Saturação:", ttk.Scale, 'saturation', None, 0.1, 2.0, 0.01),
            ("Gamma:", ttk.Scale, 'gamma', None, 0.1, 3.0, 0.01),
            ("Hue Shift:", ttk.Scale, 'hue_shift', None, -1.0, 1.0, 0.01)
        ]
        n_cols = 6
        n_rows = (len(params) + n_cols - 1) // n_cols
        value_labels = {}
        for idx, (label, widget_type, varname, values, vmin, vmax, vstep) in enumerate(params):
            col = idx % n_cols
            row = idx // n_cols
            ttk.Label(controls_frame, text=label).grid(row=row*2, column=col, sticky="e", padx=4, pady=2)
            if widget_type == ttk.Combobox:
                cb = ttk.Combobox(controls_frame, textvariable=self.fractal_params[varname], values=values, width=14)
                cb.grid(row=row*2+1, column=col, sticky="ew", padx=4, pady=2)
            else:
                scale = ttk.Scale(controls_frame, from_=vmin, to=vmax, variable=self.fractal_params[varname], orient=tk.HORIZONTAL, length=170)
                scale.grid(row=row*2+1, column=col, sticky="ew", padx=4, pady=3)
                # Label de valor
                val = self.fractal_params[varname].get()
                if isinstance(val, float):
                    val_str = f"{val:.2f}"
                else:
                    val_str = str(val)
                lval = ttk.Label(controls_frame, text=val_str, font=("Segoe UI", 11, "bold"))
                lval.grid(row=row*2+1, column=col, sticky="e", padx=(0, 4), pady=3)
                value_labels[varname] = lval
                # Atualiza valor ao mover
                def make_update(var=varname, lbl=lval, step=vstep):
                    return lambda v: lbl.config(text=f"{float(v):.2f}" if step < 1 else str(int(float(v))))
                scale.config(command=make_update())
        # Botões Fractal centralizados + Importar Parâmetros
        btn_frame = ttk.Frame(tab_fractal)
        btn_frame.pack(pady=8)
        ttk.Button(btn_frame, text="Gerar Fractal", command=self.generate_fractal).pack(side=tk.LEFT, padx=8)
        ttk.Button(btn_frame, text="Salvar Imagem", command=self.save_image).pack(side=tk.LEFT, padx=8)
        def importar_parametros():
            win = tk.Toplevel(self)
            win.title("Importar Parâmetros do Fractal")
            win.geometry("480x220")
            win.configure(bg="#23272e")
            ttk.Label(win, text="Cole o JSON dos parâmetros do fractal:", background="#23272e", foreground="#b6eaff").pack(pady=8)
            txt = tk.Text(win, height=6, bg="#181c20", fg="#b6eaff", insertbackground="#b6eaff", font=("Consolas", 10))
            txt.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)
            def aplicar():
                import json
                try:
                    data = json.loads(txt.get("1.0", tk.END))
                    for k, v in data.items():
                        if k in self.fractal_params:
                            if isinstance(self.fractal_params[k], tk.StringVar):
                                self.fractal_params[k].set(str(v))
                            else:
                                try:
                                    self.fractal_params[k].set(float(v))
                                except Exception:
                                    pass
                    win.destroy()
                except Exception as e:
                    messagebox.showerror("Erro", f"JSON inválido: {e}")
            btns = ttk.Frame(win)
            btns.pack(pady=8)
            ttk.Button(btns, text="Aplicar", command=aplicar).pack(side=tk.LEFT, padx=8)
            ttk.Button(btns, text="Cancelar", command=win.destroy).pack(side=tk.LEFT, padx=8)
        ttk.Button(btn_frame, text="Importar Parâmetros", command=importar_parametros).pack(side=tk.LEFT, padx=8)

        # --- Aba GIF Animado ---
        tab_gif = ttk.Frame(notebook)
        notebook.add(tab_gif, text="GIF Animado")
        gif_frame = ttk.Frame(tab_gif)
        gif_frame.pack(pady=12, padx=12, anchor="n")
        row = 0
        ttk.Label(gif_frame, text="Tipo de Animação:").grid(row=row, column=0, sticky="e", padx=2, pady=2)
        cb_anim = ttk.Combobox(gif_frame, textvariable=self.fractal_params['anim_type'], values=get_animation_types(), width=16)
        cb_anim.grid(row=row, column=1, sticky="w", padx=2, pady=2)
        row += 1
        ttk.Label(gif_frame, text="Frames:").grid(row=row, column=0, sticky="e", padx=2, pady=2)
        s_frames = ttk.Scale(gif_frame, from_=5, to=120, variable=self.fractal_params['num_frames'], orient=tk.HORIZONTAL, length=180, command=lambda v: l_frames.config(text=str(int(float(v)))))
        s_frames.grid(row=row, column=1, sticky="w", padx=2, pady=2)
        l_frames = ttk.Label(gif_frame, text=str(self.fractal_params['num_frames'].get()), font=("Segoe UI", 11, "bold"))
        l_frames.grid(row=row, column=2, sticky="w", padx=4)
        row += 1
        ttk.Label(gif_frame, text="Nome do GIF:").grid(row=row, column=0, sticky="e", padx=2, pady=2)
        e_gif = ttk.Entry(gif_frame, textvariable=self.fractal_params['gif_name'], width=20)
        e_gif.grid(row=row, column=1, sticky="w", padx=2, pady=2)
        row += 1
        btn_gif = ttk.Button(gif_frame, text="Gerar GIF Animado", command=self.generate_gif)
        btn_gif.grid(row=row, column=0, columnspan=2, pady=8)
        self.gif_progress = ttk.Progressbar(gif_frame, orient=tk.HORIZONTAL, length=220, mode='determinate')
        self.gif_progress.grid(row=row+1, column=0, columnspan=3, pady=4)
        self.gif_progress.pack_forget()

        # --- Aba Persistir Ser ---
        tab_persistir = ttk.Frame(notebook)
        notebook.add(tab_persistir, text="Persistir Ser")
        # Persistir Ser: duas colunas
        persist_frame = ttk.Frame(tab_persistir)
        persist_frame.pack(pady=12, padx=12, anchor="n")
        self.ser_fields = {}
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
        # 6 linhas, 2 colunas (lado a lado)
        for i, (label, key) in enumerate(labels):
            row = i % 6
            col = (i // 6) * 2
            ttk.Label(persist_frame, text=label).grid(row=row, column=col, sticky='e', padx=2, pady=2)
            entry = ttk.Entry(persist_frame, width=18)
            entry.grid(row=row, column=col+1, sticky='w', padx=2, pady=2)
            self.ser_fields[key] = entry
        # Botão ocupa linha 6, centralizado nas 4 colunas
        ttk.Button(persist_frame, text="Salvar Ser (com fractal e gif)", command=self._save_ser).grid(row=6, column=0, columnspan=4, pady=12)

        # --- Aba Seres Salvos ---
        tab_seres = ttk.Frame(notebook)
        notebook.add(tab_seres, text="Seres Salvos")
        seres_frame = ttk.Frame(tab_seres)
        seres_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        # Filtros
        filter_frame = ttk.Frame(seres_frame)
        filter_frame.pack(fill=tk.X, pady=(0,4))
        self.filter_attr = tk.StringVar(value='nome')
        self.filter_value = tk.StringVar(value='')
        ttk.Label(filter_frame, text="Filtrar por:").pack(side=tk.LEFT, padx=2)
        cb_attr = ttk.Combobox(filter_frame, textvariable=self.filter_attr, values=["nome","tipo1","tipo2"], width=8)
        cb_attr.pack(side=tk.LEFT, padx=2)
        e_val = ttk.Entry(filter_frame, textvariable=self.filter_value, width=16)
        e_val.pack(side=tk.LEFT, padx=2)
        ttk.Button(filter_frame, text="Filtrar", command=self._refresh_seres_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(filter_frame, text="Limpar", command=self._clear_seres_filter).pack(side=tk.LEFT, padx=2)
        # Lista de seres estilizada (Treeview dark)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.Treeview",
                background="#23272e",
                fieldbackground="#23272e",
                foreground="#b6eaff",
                rowheight=28,
                font=("Segoe UI", 10))
        style.configure("Dark.Treeview.Heading",
                background="#1e2a38",
                foreground="#7fffd4",
                font=("Segoe UI", 10, "bold"))
        style.map("Dark.Treeview",
            background=[('selected', '#2e3a48')],
            foreground=[('selected', '#fff')])
        self.seres_tree = ttk.Treeview(seres_frame, columns=("id","nome","tipo1","tipo2"), show="headings", height=12, style="Dark.Treeview")
        self.seres_tree.heading("id", text="ID")
        self.seres_tree.heading("nome", text="Nome")
        self.seres_tree.heading("tipo1", text="Tipo 1")
        self.seres_tree.heading("tipo2", text="Tipo 2")
        self.seres_tree.column("id", width=40, anchor="center")
        self.seres_tree.column("nome", width=120, anchor="w")
        self.seres_tree.column("tipo1", width=80, anchor="center")
        self.seres_tree.column("tipo2", width=80, anchor="center")
        self.seres_tree.pack(side=tk.LEFT, fill=tk.Y, padx=(0,8), pady=2)
        self.seres_tree.bind('<<TreeviewSelect>>', self._on_ser_select)
        # Painel de atributos
        attr_panel = ttk.Frame(seres_frame)
        attr_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.ser_attr_table = ttk.Frame(attr_panel)
        self.ser_attr_table.pack(fill=tk.X, pady=(0,8))
        # Painel de imagem/gif do ser
        img_gif_panel = ttk.Frame(attr_panel)
        img_gif_panel.pack(fill=tk.BOTH, expand=True)
        self._ser_img_panel_size = (220, 180)
        self.ser_img_panel = tk.Label(img_gif_panel, bg="#181c20", bd=2, relief="groove", width=220, height=180)
        self.ser_img_panel.pack(side=tk.LEFT, padx=4, pady=2)
        self.ser_gif_panel = tk.Label(img_gif_panel, bg="#181c20", bd=2, relief="groove", width=220, height=180)
        self.ser_gif_panel.pack(side=tk.LEFT, padx=4, pady=2)
        # Botão deletar
        btns_frame = ttk.Frame(attr_panel)
        btns_frame.pack(fill=tk.X, pady=(8,0))
        ttk.Button(btns_frame, text="Deletar Ser", command=self._delete_selected_ser).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns_frame, text="Novo Ser", command=self._abrir_cadastro_ser).pack(side=tk.LEFT, padx=4)
        self.cadastro_ser_frame = None
        self._refresh_seres_list()

        # --- Aba Analítica ---
        tab_analise = ttk.Frame(notebook)
        notebook.add(tab_analise, text="Análise")
        # --- Análise Intuitiva ---
        # --- Filtros bonitos e escuros ---
        filtros = tk.Frame(tab_analise, bg="#23272e")
        filtros.pack(fill=tk.X, padx=12, pady=(8, 8))
        ttk.Label(tab_analise, text="Análise de Seres Persistidos", font=("Segoe UI", 14, "bold"), background="#23272e", foreground="#7fffd4").pack(anchor="w", padx=12, pady=(2, 8))
        # Linha 1: Tipos
        tipo_frame = tk.Frame(filtros, bg="#23272e")
        tipo_frame.pack(fill=tk.X, pady=2)
        ttk.Label(tipo_frame, text="Tipo 1:", background="#23272e", foreground="#b6eaff", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, padx=4)
        self.analise_tipo1 = tk.StringVar(value="")
        self.analise_tipo1_cb = ttk.Combobox(tipo_frame, textvariable=self.analise_tipo1, width=12)
        self.analise_tipo1_cb.pack(side=tk.LEFT, padx=4)
        ttk.Label(tipo_frame, text="Tipo 2:", background="#23272e", foreground="#b6eaff", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, padx=4)
        self.analise_tipo2 = tk.StringVar(value="")
        self.analise_tipo2_cb = ttk.Combobox(tipo_frame, textvariable=self.analise_tipo2, width=12)
        self.analise_tipo2_cb.pack(side=tk.LEFT, padx=4)
        ttk.Button(tipo_frame, text="Atualizar Tipos", command=self._analise_atualizar_tipos).pack(side=tk.LEFT, padx=8)
        ttk.Button(tipo_frame, text="Atualizar Estatísticas", command=self._atualizar_analise).pack(side=tk.LEFT, padx=8)
        # Linha 2: Consulta média atributo
        media_frame = tk.Frame(filtros, bg="#23272e")
        media_frame.pack(fill=tk.X, pady=2)
        ttk.Label(media_frame, text="Média de:", background="#23272e", foreground="#b6eaff").pack(side=tk.LEFT, padx=4)
        self.analise_atributo_tipo = tk.StringVar(value="vida")
        self.analise_atributo_tipo_cb = ttk.Combobox(media_frame, textvariable=self.analise_atributo_tipo, values=["vida","poder","resistencia","sabedoria","espirito","impeto"], width=12)
        self.analise_atributo_tipo_cb.pack(side=tk.LEFT, padx=4)
        ttk.Label(media_frame, text="para Tipo 1:", background="#23272e", foreground="#b6eaff").pack(side=tk.LEFT, padx=4)
        self.analise_tipo_especifico = tk.StringVar(value="")
        self.analise_tipo_especifico_cb = ttk.Combobox(media_frame, textvariable=self.analise_tipo_especifico, width=12)
        self.analise_tipo_especifico_cb.pack(side=tk.LEFT, padx=4)
        self.analise_media_tipo_label = ttk.Label(media_frame, text="", font=("Segoe UI", 11, "bold"), background="#23272e", foreground="#7fffd4")
        self.analise_media_tipo_label.pack(side=tk.LEFT, padx=8)
        ttk.Button(media_frame, text="Consultar Média", command=self._analise_media_atributo_tipo).pack(side=tk.LEFT, padx=8)
        # Linha 3: Ranking
        ranking_frame = tk.Frame(filtros, bg="#23272e")
        ranking_frame.pack(fill=tk.X, pady=2)
        ttk.Label(ranking_frame, text="Ranking Ímpeto (Top N):", background="#23272e", foreground="#b6eaff").pack(side=tk.LEFT, padx=4)
        self.analise_ranking_n = tk.IntVar(value=10)
        ttk.Spinbox(ranking_frame, from_=1, to=100, textvariable=self.analise_ranking_n, width=6).pack(side=tk.LEFT, padx=4)
        ttk.Button(ranking_frame, text="Mostrar Ranking", command=self._analise_ranking_impeto).pack(side=tk.LEFT, padx=8)

        # Tabelas
        ttk.Label(tab_analise, text="Médias dos atributos por Tipo 1/2", font=("Segoe UI", 10, "bold"), background="#23272e", foreground="#b6eaff").pack(anchor="w", padx=12, pady=(4,0))
        self._analise_media_tipo_table = ttk.Treeview(tab_analise, columns=("vida","poder","resistencia","sabedoria","espirito","impeto"), show="headings", height=6, style="Dark.Treeview")
        self._analise_media_tipo_table.pack(fill=tk.X, padx=12, pady=2)
        self._analise_media_tipo_table['columns'] = ("tipo1","tipo2","vida","poder","resistencia","sabedoria","espirito","impeto")
        for col in self._analise_media_tipo_table['columns']:
            self._analise_media_tipo_table.heading(col, text=col.capitalize())
            self._analise_media_tipo_table.column(col, width=80, anchor="center")
        self._analise_media_tipo_table.column("tipo1", width=100, anchor="w")
        self._analise_media_tipo_table.column("tipo2", width=100, anchor="w")

        ttk.Label(tab_analise, text="Ranking de Maior Ímpeto", font=("Segoe UI", 10, "bold"), background="#23272e", foreground="#b6eaff").pack(anchor="w", padx=12, pady=(8,0))
        self._analise_ranking_table = ttk.Treeview(tab_analise, columns=("nome","tipo1","tipo2","impeto"), show="headings", height=6, style="Dark.Treeview")
        self._analise_ranking_table.pack(fill=tk.X, padx=12, pady=2)
        for col in ("nome","tipo1","tipo2","impeto"):
            self._analise_ranking_table.heading(col, text=col.capitalize())
            self._analise_ranking_table.column(col, width=100, anchor="center")
        self._analise_ranking_table.column("nome", width=160, anchor="w")

        ttk.Label(tab_analise, text="Estatísticas Gerais dos Atributos", font=("Segoe UI", 10, "bold"), background="#23272e", foreground="#b6eaff").pack(anchor="w", padx=12, pady=(8,0))
        self._analise_table = ttk.Treeview(tab_analise, columns=("min","max","media","mediana","desvio"), show="headings", height=6, style="Dark.Treeview")
        self._analise_table.pack(fill=tk.X, padx=12, pady=2)
        self._analise_table['columns'] = ("atributo","min","max","media","mediana","desvio")
        self._analise_table.heading("atributo", text="Atributo")
        self._analise_table.column("atributo", width=120, anchor="w")
        for col in ("min","max","media","mediana","desvio"):
            self._analise_table.heading(col, text=col.capitalize())
            self._analise_table.column(col, width=80, anchor="center")

        # Painéis de imagem e GIF SEMPRE visíveis na parte inferior do main_frame
        self.vis_frame = ttk.Frame(main_frame)
        self.vis_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=2, pady=(2, 0))
        self.vis_frame.grid_columnconfigure(0, minsize=600, weight=1)
        self.vis_frame.grid_columnconfigure(1, minsize=600, weight=1)
        self.vis_frame.grid_rowconfigure(0, minsize=400, weight=1)
        img_frame = tk.Frame(self.vis_frame, bg="#181c20", width=600, height=400)
        img_frame.grid(row=0, column=0, padx=(0, 4), pady=(2, 0), sticky="nsew")
        img_frame.grid_propagate(False)
        self.image_panel = tk.Label(
            img_frame, bg="#181c20", bd=2, relief="groove",
            highlightbackground="#b6eaff", highlightthickness=2,
            anchor='center', justify='center',
            text="Imagem Fractal", fg="#b6eaff", font=("Segoe UI", 16, "bold")
        )
        self.image_panel.place(relx=0.5, rely=0.5, anchor="center", width=600, height=400)
        gif_frame = tk.Frame(self.vis_frame, bg="#181c20", width=600, height=400)
        gif_frame.grid(row=0, column=1, padx=(4, 0), pady=(2, 0), sticky="nsew")
        gif_frame.grid_propagate(False)
        self.gif_panel = tk.Label(
            gif_frame, bg="#181c20", bd=2, relief="groove",
            highlightbackground="#b6eaff", highlightthickness=2,
            anchor='center', justify='center',
            text="GIF Animado", fg="#b6eaff", font=("Segoe UI", 16, "bold")
        )
        self.gif_panel.place(relx=0.5, rely=0.5, anchor="center", width=600, height=400)
        self.image_panel.config(image='', text='Imagem Fractal', bg='#181c20', fg='#b6eaff', font=("Segoe UI", 16, "bold"))
        self.gif_panel.config(image='', text='GIF Animado', bg='#181c20', fg='#b6eaff', font=("Segoe UI", 16, "bold"))
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=0)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        # Vincula evento de troca de aba
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)

    def _analise_atualizar_tipos(self):
        # Preenche os combos de tipo1/tipo2 com valores únicos do banco
        import duckdb
        con = duckdb.connect(persistence.DB_PATH)
        tipos1 = [r[0] for r in con.execute("SELECT DISTINCT tipo1 FROM seres WHERE tipo1 IS NOT NULL AND tipo1 != ''").fetchall()]
        tipos2 = [r[0] for r in con.execute("SELECT DISTINCT tipo2 FROM seres WHERE tipo2 IS NOT NULL AND tipo2 != ''").fetchall()]
        self.analise_tipo1_cb['values'] = sorted(tipos1)
        self.analise_tipo2_cb['values'] = sorted(tipos2)
        self.analise_tipo_especifico_cb['values'] = sorted(tipos1)
        con.close()
        if tipos1:
            self.analise_tipo1.set(tipos1[0])
            self.analise_tipo_especifico.set(tipos1[0])
        if tipos2:
            self.analise_tipo2.set(tipos2[0])

    def _analise_media_atributo_tipo(self):
        # Mostra a média do atributo escolhido para o tipo1 escolhido
        import duckdb
        atributo = self.analise_atributo_tipo.get()
        tipo = self.analise_tipo_especifico.get()
        con = duckdb.connect(persistence.DB_PATH)
        row = con.execute(f"SELECT AVG({atributo}) FROM seres WHERE tipo1=?", [tipo]).fetchone()
        media = row[0] if row and row[0] is not None else '-'
        self.analise_media_tipo_label.config(text=f"Média: {media:.2f}" if isinstance(media, float) else f"Média: {media}")
        con.close()

    def _analise_ranking_impeto(self):
        # Mostra o ranking dos seres com maior ímpeto
        import duckdb
        n = self.analise_ranking_n.get()
        con = duckdb.connect(persistence.DB_PATH)
        rows = con.execute("SELECT nome, tipo1, tipo2, impeto FROM seres ORDER BY impeto DESC LIMIT ?", [n]).fetchall()
        self._analise_ranking_table.delete(*self._analise_ranking_table.get_children())
        for r in rows:
            self._analise_ranking_table.insert('', 'end', values=r)
        con.close()

    def _atualizar_analise(self):
        import duckdb
        import statistics
        atributos = ["vida","poder","resistencia","sabedoria","espirito","impeto"]
        # 1. Médias por tipo1/tipo2
        self._analise_media_tipo_table.delete(*self._analise_media_tipo_table.get_children())
        con = duckdb.connect(persistence.DB_PATH)
        rows = con.execute("SELECT tipo1, tipo2, AVG(vida), AVG(poder), AVG(resistencia), AVG(sabedoria), AVG(espirito), AVG(impeto) FROM seres GROUP BY tipo1, tipo2").fetchall()
        for r in rows:
            tipo1, tipo2 = r[0], r[1]
            vals = [f"{v:.2f}" if v is not None else '-' for v in r[2:]]
            self._analise_media_tipo_table.insert('', 'end', values=(tipo1, tipo2, *vals))
        # 2. Atualiza combos de tipo1/tipo2
        self._analise_atualizar_tipos()
        # 3. Estatísticas gerais
        self._analise_table.delete(*self._analise_table.get_children())
        try:
            for attr in atributos:
                rows = con.execute(f"SELECT {attr} FROM seres").fetchall()
                vals = [r[0] for r in rows if r[0] is not None]
                if vals:
                    minimo = min(vals)
                    maximo = max(vals)
                    media = sum(vals)/len(vals)
                    mediana = statistics.median(vals)
                    desvio = statistics.stdev(vals) if len(vals) > 1 else 0.0
                    self._analise_table.insert('', 'end', values=(attr, minimo, maximo, f"{media:.2f}", f"{mediana:.2f}", f"{desvio:.2f}"))
                else:
                    self._analise_table.insert('', 'end', values=(attr, '-', '-', '-', '-', '-'))
            con.close()
        except Exception as e:
            self._analise_table.insert('', 'end', values=("Erro", str(e), '', '', '', ''))
        # Apenas atualize os dados das tabelas nesta função. Não manipule widgets de notebook ou main_frame aqui.

        
    def _delete_selected_ser(self):
        # Deleta o ser atualmente selecionado na Treeview
        selected = self.seres_tree.selection()
        if not selected:
            messagebox.showinfo("Atenção", "Selecione um ser para deletar.")
            return
        item = self.seres_tree.item(selected[0])
        ser_id = item['values'][0]
        if ser_id == "-":
            return
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
        # Atualiza Treeview estilizada
        for i in self.seres_tree.get_children():
            self.seres_tree.delete(i)
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
            self.seres_tree.insert('', 'end', values=("-", "Nenhum ser encontrado.", "", ""))
            self.status_var.set("Nenhum ser encontrado.")
        else:
            for ser in seres:
                self.seres_tree.insert('', 'end', values=(ser['id'], ser['nome'], ser['tipo1'], ser['tipo2']))
        self._filtered_seres = seres

    def _clear_seres_filter(self):
        if hasattr(self, 'filter_value'):
            self.filter_value.set('')
        self._refresh_seres_list()


    def _on_ser_select(self, event):
        # Treeview: pega seleção
        selected = self.seres_tree.selection()
        if not selected:
            return
        item = self.seres_tree.item(selected[0])
        ser_id = item['values'][0]
        if ser_id == "-":
            return
        seres = getattr(self, '_filtered_seres', persistence.list_seres())
        ser = next((s for s in seres if str(s['id']) == str(ser_id)), None)
        if not ser:
            return
        # Limpa tabela de atributos
        for w in self.ser_attr_table.winfo_children():
            w.destroy()
        # Cabeçalho
        ttk.Label(self.ser_attr_table, text="Atributo", font=("Segoe UI", 10, "bold"), anchor='w').grid(row=0, column=0, sticky='w', padx=2, pady=1)
        ttk.Label(self.ser_attr_table, text="Valor", font=("Segoe UI", 10, "bold"), anchor='w').grid(row=0, column=1, sticky='w', padx=2, pady=1)
        ttk.Label(self.ser_attr_table, text="Atributo", font=("Segoe UI", 10, "bold"), anchor='w').grid(row=0, column=2, sticky='w', padx=2, pady=1)
        ttk.Label(self.ser_attr_table, text="Valor", font=("Segoe UI", 10, "bold"), anchor='w').grid(row=0, column=3, sticky='w', padx=2, pady=1)
        # Linhas de atributos em duas colunas
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
        n = len(attrs)
        half = (n + 1) // 2
        for i in range(half):
            k1, v1 = attrs[i]
            ttk.Label(self.ser_attr_table, text=k1, anchor='w').grid(row=i+1, column=0, sticky='w', padx=2, pady=1)
            ttk.Label(self.ser_attr_table, text=str(v1), anchor='w').grid(row=i+1, column=1, sticky='w', padx=2, pady=1)
        for i in range(half, n):
            k2, v2 = attrs[i]
            ttk.Label(self.ser_attr_table, text=k2, anchor='w').grid(row=i-half+1, column=2, sticky='w', padx=12, pady=1)
            ttk.Label(self.ser_attr_table, text=str(v2), anchor='w').grid(row=i-half+1, column=3, sticky='w', padx=2, pady=1)

        # Linha de botões (Ver parâmetros, Editar, Deletar) sempre visível e destacada
        btns_row = half+2
        btns_frame = ttk.Frame(self.ser_attr_table)
        btns_frame.grid(row=btns_row, column=0, columnspan=4, sticky='ew', pady=(8,2))
        btns_frame.columnconfigure((0,1,2), weight=1)
        # Botão Ver parâmetros (força exibição se campo existir)
        fractal_params = ser.get('params', None)
        show_param_btn = False
        if fractal_params is not None:
            show_param_btn = True
        if show_param_btn:
            def show_params_window():
                import json
                win = tk.Toplevel(self)
                win.title("Parâmetros do Fractal")
                win.geometry("520x400")
                win.configure(bg="#23272e")
                txt = tk.Text(win, wrap="word", bg="#181c20", fg="#b6eaff", font=("Consolas", 10), relief="flat")
                txt.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
                def default_complex(obj):
                    if isinstance(obj, complex):
                        return str(obj)
                    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")
                param_data = fractal_params
                if isinstance(fractal_params, str):
                    try:
                        param_data = json.loads(fractal_params)
                    except Exception as e:
                        print("[DEBUG] Erro ao decodificar params string:", e)
                        param_data = fractal_params
                try:
                    param_json = json.dumps(param_data, indent=2, ensure_ascii=False, default=default_complex)
                except Exception as e:
                    print("[DEBUG] Erro ao serializar params:", e)
                    param_json = str(param_data)
                txt.insert("1.0", param_json)
                txt.config(state="disabled")
                btn_frame = ttk.Frame(win)
                btn_frame.pack(fill=tk.X, padx=8, pady=8)
                def save_json():
                    from tkinter import filedialog
                    file = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON','*.json'),('Todos','*.*')], initialfile='parametros_fractal.json')
                    if file:
                        with open(file, 'w', encoding='utf-8') as f:
                            f.write(param_json)
                def copy_json():
                    self.clipboard_clear()
                    self.clipboard_append(param_json)
                ttk.Button(btn_frame, text="Salvar JSON", command=save_json).pack(side=tk.LEFT, padx=4)
                ttk.Button(btn_frame, text="Copiar", command=copy_json).pack(side=tk.LEFT, padx=4)
                ttk.Button(btn_frame, text="Fechar", command=win.destroy).pack(side=tk.RIGHT, padx=4)
            ttk.Button(btns_frame, text="Ver parâmetros", command=show_params_window).grid(row=0, column=0, padx=8, sticky='ew')
        else:
            print("[DEBUG] Ser sem params:", ser)
            ttk.Label(btns_frame, text="Parâmetros não disponíveis", foreground="#ff8888").grid(row=0, column=0, padx=8, sticky='ew')
        # Botão Editar
        ttk.Button(btns_frame, text="Editar atributos", command=lambda sid=ser_id: self._abrir_editar_ser(sid)).grid(row=0, column=1, padx=8, sticky='ew')
        # Botão Deletar
        ttk.Button(btns_frame, text="Deletar Ser", command=lambda sid=ser_id: self._delete_ser(sid)).grid(row=0, column=2, padx=8, sticky='ew')


        # Atualiza imagem no painel existente (maior, centralizada)
        max_w, max_h = 260, 220
        img_data = ser.get('img', None)
        from PIL import Image
        import base64
        if img_data is not None:
            try:
                img = None
                if hasattr(img_data, 'copy'):
                    img = img_data.copy()
                elif isinstance(img_data, bytes):
                    img = Image.open(io.BytesIO(img_data))
                elif isinstance(img_data, str):
                    try:
                        # tenta base64
                        img_bytes = base64.b64decode(img_data)
                        img = Image.open(io.BytesIO(img_bytes))
                    except Exception as e:
                        print("[DEBUG] Erro ao decodificar imagem base64:", e)
                        img = None
                if img:
                    img.thumbnail((max_w, max_h), Image.LANCZOS)
                    self._ser_img_tk = ImageTk.PhotoImage(img)
                    self.ser_img_panel.config(image=self._ser_img_tk, width=max_w, height=max_h, text="", anchor='center')
                    self.ser_img_panel.image = self._ser_img_tk
                else:
                    self.ser_img_panel.config(image='', width=max_w, height=max_h, text="Erro na imagem", fg="#ff8888", bg="#181c20", font=("Segoe UI", 12, "bold"), anchor='center')
                    self.ser_img_panel.image = None
            except Exception as e:
                print("[DEBUG] Erro ao exibir imagem:", e)
                self.ser_img_panel.config(image='', width=max_w, height=max_h, text="Erro na imagem", fg="#ff8888", bg="#181c20", font=("Segoe UI", 12, "bold"), anchor='center')
                self.ser_img_panel.image = None
        else:
            self.ser_img_panel.config(image='', width=max_w, height=max_h, text="Sem imagem", fg="#b6eaff", bg="#181c20", font=("Segoe UI", 12, "bold"), anchor='center')
            self.ser_img_panel.image = None

        # Atualiza gif no painel existente (maior, centralizada)
        self.ser_gif_panel.config(image='', width=max_w, height=max_h, text="", fg="#b6eaff", bg="#181c20", anchor='center')
        self.ser_gif_panel.image = None
        self._ser_gif_tk_frames = []
        gif_bytes = ser.get('gif_bytes', None)
        if gif_bytes:
            try:
                gif = None
                if isinstance(gif_bytes, bytes):
                    gif = Image.open(io.BytesIO(gif_bytes))
                elif isinstance(gif_bytes, str):
                    try:
                        gif_bytes2 = base64.b64decode(gif_bytes)
                        gif = Image.open(io.BytesIO(gif_bytes2))
                    except Exception as e:
                        print("[DEBUG] Erro ao decodificar gif base64:", e)
                        gif = None
                if gif:
                    frames = []
                    try:
                        while True:
                            frames.append(gif.copy())
                            gif.seek(len(frames))
                    except EOFError:
                        pass
                    except Exception:
                        pass
                    if not frames:
                        try:
                            gif.seek(0)
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
                            self.ser_gif_panel.config(image=self._ser_gif_tk_frames[idx], width=max_w, height=max_h, text="", anchor='center')
                            self.ser_gif_panel.image = self._ser_gif_tk_frames[idx]
                            self.ser_gif_panel.after(120, gif_loop, (idx+1)%len(self._ser_gif_tk_frames))
                        gif_loop()
                    else:
                        self.ser_gif_panel.config(image='', width=max_w, height=max_h, text="Sem GIF", fg="#b6eaff", bg="#181c20", font=("Segoe UI", 12, "bold"), anchor='center')
                        self.ser_gif_panel.image = None
                else:
                    self.ser_gif_panel.config(image='', width=max_w, height=max_h, text="Erro no GIF", fg="#ff8888", bg="#181c20", font=("Segoe UI", 12, "bold"), anchor='center')
                    self.ser_gif_panel.image = None
            except Exception as e:
                print("[DEBUG] Erro ao exibir GIF:", e)
                self.ser_gif_panel.config(image='', width=max_w, height=max_h, text="Erro no GIF", fg="#ff8888", bg="#181c20", font=("Segoe UI", 12, "bold"), anchor='center')
                self.ser_gif_panel.image = None
        else:
            self.ser_gif_panel.config(image='', width=max_w, height=max_h, text="Sem GIF", fg="#b6eaff", bg="#181c20", font=("Segoe UI", 12, "bold"), anchor='center')
            self.ser_gif_panel.image = None

        # Atualiza botões de ação (deletar/editar) - sempre mostra
        if not hasattr(self, '_ser_action_frame') or not self._ser_action_frame.winfo_exists():
            self._ser_action_frame = ttk.Frame(self.ser_gif_panel.master)
            self._ser_action_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(8,0))
        for w in self._ser_action_frame.winfo_children():
            w.destroy()

    def _abrir_editar_ser(self, ser_id):
        ser = persistence.load_ser(ser_id)
        win = tk.Toplevel(self)
        win.title(f"Editar atributos de {ser['nome']}")
        win.geometry("400x420")
        win.configure(bg="#23272e")
        form = ttk.Frame(win)
        form.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        fields = {}
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
            entry.insert(0, str(ser[key]))
            entry.grid(row=row, column=1, sticky='ew', padx=2, pady=2)
            fields[key] = entry
            row += 1
        def salvar():
            novos = {k: v.get() for k, v in fields.items()}
            # Tipos
            for k in ["vida","poder","resistencia","sabedoria","espirito","impeto"]:
                try:
                    novos[k] = int(novos[k])
                except Exception:
                    novos[k] = ser[k]
            persistence.update_ser_atributos(ser_id, novos)
            self._refresh_seres_list()
            win.destroy()
        ttk.Button(form, text="Salvar", command=salvar).grid(row=row, column=0, columnspan=2, pady=12)
        ttk.Button(form, text="Cancelar", command=win.destroy).grid(row=row+1, column=0, columnspan=2, pady=2)

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
