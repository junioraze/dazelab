# COMO MODULARIZAR E ADICIONAR NOVAS OPÇÕES

Este projeto está organizado em módulos para facilitar a manutenção e expansão.

- **fractal_core.py**: Funções de fractais. Para adicionar um novo fractal, crie uma função e registre no FRACTAL_REGISTRY.
- **palettes.py**: Funções de paletas de cor. Para adicionar uma nova paleta, crie uma função e registre no PALETTE_REGISTRY.
- **fractal_animations.py**: Funções de animação para GIF. Para adicionar uma nova animação, crie uma função e registre no ANIMATION_REGISTRY.
- **fractal_ui.py**: Interface Tkinter. As opções de fractal, paleta e animação são carregadas dinamicamente dos módulos acima.

## Exemplo para adicionar um novo fractal
1. Abra `fractal_core.py`.
2. Crie uma função:
   ```python
   def meu_fractal(c, max_iterations=100, power=2.0, bailout=2.0, **kwargs):
       # lógica
       return iter_count
   FRACTAL_REGISTRY["meu_fractal"] = meu_fractal
   ```
3. Ele aparecerá automaticamente na UI.

## Exemplo para adicionar uma nova paleta
1. Abra `palettes.py`.
2. Crie uma função:
   ```python
   def minha_paleta(t, intensity=1.0):
       # lógica
       return (r, g, b)
   PALETTE_REGISTRY["minha_paleta"] = minha_paleta
   ```
3. Ela aparecerá automaticamente na UI.

## Exemplo para adicionar uma nova animação
1. Abra `fractal_animations.py`.
2. Crie uma função:
   ```python
   def anim_meu_tipo(params, frame_idx, num_frames):
       # lógica
       return PIL.Image
   ANIMATION_REGISTRY["meu_tipo"] = anim_meu_tipo
   ```
3. Ela aparecerá automaticamente na UI.

## Observações
- Não é necessário alterar a UI para novas opções aparecerem.
- Siga o padrão de assinatura das funções para garantir compatibilidade.
- Consulte os arquivos de exemplo para mais detalhes.
