# 🔗 Simulador de Grafos

Aplicação desktop interativa para criação, visualização e análise de grafos, desenvolvida em Python com interface gráfica Tkinter e renderização via Matplotlib/NetworkX.

> Desenvolvido por **Leandro Rodrigues** e **Lucas Bitencourt** — Módulo 3

---

## 📸 Funcionalidades

### Estrutura do Grafo
- Suporte a grafos **dirigidos** e **não dirigidos**
- Implementação por **lista de adjacência**
- Adição e remoção de **vértices** e **arestas** com IDs e pesos customizáveis
- Alternância entre modo dirigido/não dirigido com **preservação dos dados**

### Visualização
- Desenho interativo com **arrastar e soltar** de vértices
- Exibição de **IDs e pesos** nas arestas
- **Destaque visual** de arestas em resultados de algoritmos
- Visualização de **matrizes de adjacência e incidência**

### Algoritmos Implementados

| Algoritmo | Descrição |
|---|---|
| **Prim** | Árvore Geradora Mínima (AGM) para grafos não dirigidos |
| **Roy-Warshall** | Fecho transitivo (alcançabilidade) para grafos dirigidos |
| **BFS** | Busca em Largura com árvore de cobertura |
| **DFS** | Busca em Profundidade com árvore de cobertura |
| **Welsh-Powell** | Coloração de grafos com número cromático mínimo |
| **A\*** | Caminho mínimo com heurística (otimizado para cidades paranaenses) |
| **AG-TSP** | Problema do Caixeiro Viajante via Algoritmo Genético (PMX + mutação swap) |
| **Hopcroft-Tarjan** | Verificação de planaridade (com fallback NetworkX) |

### Análise Estrutural
- Detecção de **componentes conexas** (grafos não dirigidos)
- Detecção de **componentes fortemente conexas** via Kosaraju (grafos dirigidos)
- Grafo de **exemplo pré-definido** com 8 cidades e 18 arestas

---

## 🛠️ Tecnologias

- **Python 3.x**
- `tkinter` — Interface gráfica
- `matplotlib` — Renderização e interação com o grafo
- `networkx` — Suporte a estruturas de grafos e algoritmos auxiliares
- `heapq`, `collections` — Estruturas de dados para os algoritmos

---

## ⚙️ Instalação

**1. Clone o repositório:**
```bash
git clone https://github.com/leandro-wad/simulador-de-grafos-em-python
cd simulador-grafos
```

**2. Instale as dependências:**
```bash
pip install matplotlib networkx
```

> `tkinter` já vem incluso na instalação padrão do Python. Se não estiver disponível, instale com:
> ```bash
> sudo apt-get install python3-tk  # Linux
> ```

---

## ▶️ Como Executar

```bash
python grafos-app.py
```

---

## 🖥️ Como Usar

1. **Escolha o modo** — marque ou desmarque "Dirigido" no topo da janela
2. **Adicione vértices** — clique em "Adicionar vértice" e informe o nome
3. **Adicione arestas** — clique em "Adicionar ligação" e informe origem, destino, ID (opcional) e peso
4. **Visualize** — clique em "Desenhar Grafo"; arraste os nós para reorganizar o layout
5. **Execute algoritmos** — use os botões da interface para BFS, DFS, Prim, A*, etc.
6. **Grafo exemplo** — clique em "Criar Grafo Exemplo" para carregar um grafo de 8 cidades pré-configurado

---

## 📁 Estrutura do Código

```
simulador-grafos/
│
├── grafos-app.py
│   ├── class Grafo              # Estrutura principal (lista de adjacência)
│   │   ├── Manipulação básica   # adicionar/remover vértices e arestas
│   │   ├── Matrizes             # adjacência e incidência
│   │   ├── Visualização         # desenho com drag-and-drop
│   │   └── Algoritmos           # Prim, BFS, DFS, Roy-Warshall, Welsh-Powell, A*, TSP, Planaridade
│   │
│   └── class GrafoApp           # Interface Tkinter
│       ├── Painel de controle   # botões e log
│       └── Handlers             # ações de cada botão
│
└── README.md
```

---

## 👥 Autores

| Nome | GitHub |
|---|---|
| Leandro Rodrigues | [@leandro](https://github.com/leandro-wad) |
| Lucas Bitencourt | [@lucas](https://github.com/Bitencourt9) |

---

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos. Consulte os autores para uso e distribuição.
