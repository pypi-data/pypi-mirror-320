# GraphiteInter

GraphiteInter é uma estrutura simples para a criação de interfaces gráficas interativas usando o tkinter em Python.

## Como Usar

```python
from graphite import Graphite

Graphite.create_window()
Graphite.inserttext('hello', 'Olá Mundo!', 20, (10, 10), 'black')
Graphite.run()
