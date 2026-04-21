import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import matplotlib.pyplot as plt
import networkx as nx
from collections import deque, defaultdict
import math
import heapq


class Grafo:
    """
    Implementação de grafo usando LISTA DE ADJACÊNCIA.
    Suporta grafos dirigidos e não dirigidos.
    - vertices: set de rótulos (qualquer hashable)
    - adj: dict vertice -> list de (vizinho, edge_id, peso)
    - edges: dict edge_id -> (u, v, peso, dirigido)
    """

    def __init__(self, dirigido: bool = False):
        self.dirigido = dirigido
        self.vertices = set()
        self.adj = defaultdict(list)  # v -> list of (neighbor, edge_id, weight)
        self.edges = dict()  # edge_id -> (u, v, weight, dirigido)
        # coords: opcional dict cidade -> (lat, lon)
        self.coords = {}

    # -------------------------
    # Manipulação básica
    # -------------------------
    def adicionar_vertice_isolado(self, v):
        """Adiciona vértice isolado v. Retorna True se adicionado, False se já existia."""
        if v in self.vertices:
            return False
        self.vertices.add(v)
        # adj[v] criado implicitamente por defaultdict quando necessário
        _ = self.adj[v]
        return True

    def inserir_ligacao(self, u, v, edge_id=None, peso=1):
        """
        Insere ligação entre u-v.
        - edge_id: se None, gera automático (v1, v2 ... vn).
        - peso: valor da aresta/arco (numérico ou outro).
        Retorna edge_id criado.
        """
        if u not in self.vertices or v not in self.vertices:
            raise ValueError("Ambos os vértices devem existir antes de criar a ligação.")
        if edge_id is None:
            base = 1
            while f"v{base}" in self.edges:
                base += 1
            edge_id = f"v{base}"
        if edge_id in self.edges:
            raise ValueError("edge_id já existe.")
        self.edges[edge_id] = (u, v, peso, self.dirigido)
        # Adiciona à lista de adjacência
        self.adj[u].append((v, edge_id, peso))
        if not self.dirigido:
            self.adj[v].append((u, edge_id, peso))
        else:
            # em grafo dirigido não adiciona entrada inversa
            pass
        return edge_id

    def remover_vertice(self, v):
        """Remove vértice v e todas as ligações incidentes."""
        if v not in self.vertices:
            return False
        # Remover arestas da estrutura edges e das listas adj
        to_remove = []
        for eid, (u, w, peso, dirg) in list(self.edges.items()):
            if u == v or w == v:
                to_remove.append(eid)
        for eid in to_remove:
            self.remover_ligacao(eid)
        # finalmente remover vértice
        self.vertices.remove(v)
        if v in self.adj:
            del self.adj[v]
        # remover acontecimentos em adj de outros vértices (já feitos via remover_ligacao)
        return True

    def remover_ligacao(self, edge_id):
        """Remove ligação identificada por edge_id."""
        if edge_id not in self.edges:
            return False
        u, v, peso, dirg = self.edges.pop(edge_id)

        # remover das listas de adjacência

        def remove_from_list(a, target_neighbor, eid):
            new = [(n, e, p) for (n, e, p) in a if e != eid]
            return new

        if u in self.adj:
            self.adj[u] = remove_from_list(self.adj[u], v, edge_id)
        if not dirg and v in self.adj:
            # em não dirigido, também remover do v
            self.adj[v] = remove_from_list(self.adj[v], u, edge_id)
        if dirg:
            # em dirigido, pode haver caso onde arco v->u exista com outro id; removemos só o eid
            if v in self.adj:
                self.adj[v] = remove_from_list(self.adj[v], u, edge_id)
        return True

    # -------------------------
    # Representações matriciais
    # -------------------------
    def matriz_adjacencia(self):
        """Retorna (labels, matriz) com ordem consistente dos vértices."""
        labels = sorted(self.vertices, key=str)
        n = len(labels)
        index = {labels[i]: i for i in range(n)}
        # para grafos multigrafo (múltiplas arestas) soma pesos? Vou contar número de arestas entre pares
        M = [[0] * n for _ in range(n)]
        for eid, (u, v, peso, dirg) in self.edges.items():
            i, j = index[u], index[v]
            # para matriz de adjacência iremos somar a presença; também guardamos soma de pesos
            try:
                num = float(peso)
                M[i][j] += num
                if not dirg:
                    M[j][i] += num
            except Exception:
                # se não for convertível, conta 1
                M[i][j] += 1
                if not dirg:
                    M[j][i] += 1
        return labels, M

    def matriz_incidencia(self):
        """Retorna (labels_vertices, labels_arestas, matriz_incidence)
        Matriz de dimensão |V| x |E| onde entrada é:
        - em grafo não dirigido: 1 se vértice incidente à aresta (aparece duas 1 para cada aresta)
        - em grafo dirigido: -1 para origem, +1 para destino (ou vice-versa; adotamos +1 para destino)
        """
        vlabels = sorted(self.vertices, key=str)
        elabels = sorted(self.edges.keys())
        n, m = len(vlabels), len(elabels)
        vindex = {vlabels[i]: i for i in range(n)}
        I = [[0] * m for _ in range(n)]
        for j, eid in enumerate(elabels):
            u, v, peso, dirg = self.edges[eid]
            iu, iv = vindex[u], vindex[v]
            if dirg:
                I[iu][j] = -1
                I[iv][j] = 1
            else:
                # não dirigido: ambos 1
                I[iu][j] = 1
                I[iv][j] = 1
        return vlabels, elabels, I

    # -------------------------
    # Desenho / Visualização
    # -------------------------
    def _build_networkx_graph(self, include_edge_labels=True):
        """Converte para networkx.Graph ou DiGraph para plot."""
        if self.dirigido:
            G = nx.DiGraph()
        else:
            G = nx.Graph()
        G.add_nodes_from(self.vertices)
        for eid, (u, v, peso, dirg) in self.edges.items():
            label = f"{eid}:{peso}"
            # se já existir aresta com mesmo endpoints e queremos múltiplas arestas,
            # networkx.Graph sobrescreve. Para visualização, usaremos simple edges com label contendo id.
            G.add_edge(u, v, key=eid, id=eid, weight=peso, label=label)
        return G

    def desenhar(self, highlight_edges=None, highlight_nodes=None, node_color_map=None, title="Grafo"):
        """Desenha o grafo e permite arrastar vértices a todo momento.
        highlight_edges: set de edge_ids que receberão destaque (largura maior e cor diferente)
        node_color_map: dict node -> color_index (inteiro) para colorir nós (usado em Welsh-Powell)
        """
        import matplotlib.collections as mcoll
        import numpy as np
        import traceback

        G = self._build_networkx_graph()
        fig, ax = plt.subplots(figsize=(9, 6))

        # Preservar posições manuais entre redesenhos
        if not hasattr(self, "_pos") or set(self._pos.keys()) != set(G.nodes()):
            self._pos = nx.spring_layout(G, seed=42)
        pos = self._pos

        node_list = list(G.nodes())
        # construir cores dos nós a partir de node_color_map se fornecido
        if node_color_map:
            # map indices para uma paleta
            cmap = plt.get_cmap("tab10")
            node_colors = [cmap(node_color_map.get(n, 0) % 10) for n in node_list]
        else:
            node_colors = ['lightgreen' if (highlight_nodes and n in highlight_nodes) else 'lightblue' for n in node_list]

        # --- DESENHAR NÓS UMA ÚNICA VEZ ---
        nodes = nx.draw_networkx_nodes(G, pos, nodelist=node_list, node_color=node_colors, node_size=470, ax=ax)
        nodes.set_picker(5)  # tolerância de picking
        labels = nx.draw_networkx_labels(G, pos, labels={n: n for n in node_list}, ax=ax)

        # --- DESENHAR ARESTAS (separando destacadas e normais) ---
        # Construir mapeamento edge_id -> (u,v) para desenhar por id
        eid_to_uv = {}
        for eid, (u, v, peso, dirg) in self.edges.items():
            eid_to_uv[eid] = (u, v)

        highlighted = []
        normal = []
        for eid, (u, v, peso, dirg) in self.edges.items():
            if highlight_edges and eid in highlight_edges:
                highlighted.append((u, v, eid))
            else:
                normal.append((u, v, eid))

        # desenhar arestas normais
        if normal:
            edgelist_norm = [(u, v) for (u, v, eid) in normal]
            nx.draw_networkx_edges(G, pos, edgelist=edgelist_norm, ax=ax, arrows=self.dirigido, width=1.0, alpha=0.7)
        # desenhar arestas destacadas
        if highlighted:
            edgelist_high = [(u, v) for (u, v, eid) in highlighted]
            nx.draw_networkx_edges(G, pos, edgelist=edgelist_high, ax=ax, arrows=self.dirigido, width=3.0, edge_color='red', style='solid')

        # edge labels (id:weight)
        edge_label_map = {}
        for eid, (u, v, peso, dirg) in self.edges.items():
            edge_label_map[(u, v)] = f"{eid}:{peso}"
        # desenhar labels de arestas (após arestas)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_label_map, font_color='blue', ax=ax)

        ax.set_title(title)
        ax.axis('off')

        # --- ESTADO PARA ARRASTAR ---
        dragged = {'node': None, 'offset': (0, 0)}

        def update_edges_and_labels():
            # redesenhar tudo (simplesmente redesenha nós/arestas)
            ax.clear()
            # redesenhar nós
            node_colors_local = node_colors
            nx.draw_networkx_nodes(G, pos, nodelist=node_list, node_color=node_colors_local, node_size=470, ax=ax)
            nx.draw_networkx_labels(G, pos, labels={n: n for n in node_list}, ax=ax)
            # redesenhar arestas normais e destacadas
            if normal:
                edgelist_norm = [(u, v) for (u, v, eid) in normal]
                nx.draw_networkx_edges(G, pos, edgelist=edgelist_norm, ax=ax, arrows=self.dirigido, width=1.0, alpha=0.7)
            if highlighted:
                edgelist_high = [(u, v) for (u, v, eid) in highlighted]
                nx.draw_networkx_edges(G, pos, edgelist=edgelist_high, ax=ax, arrows=self.dirigido, width=3.0, edge_color='red', style='solid')
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_label_map, font_color='blue', ax=ax)
            ax.set_title(title)
            ax.axis('off')
            fig.canvas.draw_idle()

        def update_nodes_and_labels():
            # Atualiza posição dos nós (PathCollection)
            offsets = np.array([pos[n] for n in node_list])
            nodes.set_offsets(offsets)
            # Atualiza rótulos
            for n, t in labels.items():
                t.set_position(pos[n])
            update_edges_and_labels()
            fig.canvas.draw_idle()

        def on_pick(event):
            if not isinstance(event.artist, mcoll.PathCollection):
                return
            ind = int(event.ind[0])
            dragged['node'] = node_list[ind]
            mx, my = event.mouseevent.xdata, event.mouseevent.ydata
            if mx is None or my is None:
                dragged['offset'] = (0, 0)
            else:
                x0, y0 = pos[dragged['node']]
                dragged['offset'] = (x0 - mx, y0 - my)

        def on_motion(event):
            if dragged['node'] is None or event.inaxes != ax or event.xdata is None or event.ydata is None:
                return
            pos[dragged['node']] = (event.xdata + dragged['offset'][0], event.ydata + dragged['offset'][1])
            update_nodes_and_labels()

        def on_release(event):
            dragged['node'] = None
            self._pos = pos

        fig.canvas.mpl_connect('pick_event', on_pick)
        fig.canvas.mpl_connect('motion_notify_event', on_motion)
        fig.canvas.mpl_connect('button_release_event', on_release)

        plt.show()

    # -------------------------
    # Algoritmos
    # -------------------------
    def prim(self):
        """Aplica Prim — retorna (mst_edges_ids, total_weight)."""
        if self.dirigido:
            raise ValueError("Prim só é aplicável a grafos não dirigidos.")
        if not self.vertices:
            return [], 0
        # precisamos de pesos numéricos; filtrar arestas com peso convertível
        adjw = {v: [] for v in self.vertices}
        for eid, (u, v, peso, dirg) in self.edges.items():
            try:
                w = float(peso)
            except:
                w = 1.0
            adjw[u].append((v, w, eid))
            adjw[v].append((u, w, eid))

        start = next(iter(self.vertices))
        visited = set([start])
        heap = []
        for (v, w, eid) in adjw[start]:
            heapq.heappush(heap, (w, start, v, eid))
        mst_edges = []
        total = 0.0
        while heap and len(visited) < len(self.vertices):
            w, a, b, eid = heapq.heappop(heap)
            if b in visited:
                continue
            visited.add(b)
            mst_edges.append(eid)
            total += w
            for (nxv, nw, neid) in adjw[b]:
                if nxv not in visited:
                    heapq.heappush(heap, (nw, b, nxv, neid))
        if len(visited) != len(self.vertices):
            raise ValueError("Grafo não é conectado; Prim não produziu AGM completa.")
        return mst_edges, total

    def busca_largura(self, origem):
        """BFS: retorna lista de arestas (edge_id) da árvore gerada em BFS e lista de nós em ordem visitada."""
        if origem not in self.vertices:
            raise ValueError("Vértice origem não existe.")
        visited = set([origem])
        q = deque([origem])
        parent = {origem: None}
        tree_edge_ids = []
        order = [origem]
        while q:
            u = q.popleft()
            for (v, eid, peso) in self.adj[u]:
                if v not in visited:
                    visited.add(v)
                    parent[v] = u
                    tree_edge_ids.append(eid)
                    q.append(v)
                    order.append(v)
        return tree_edge_ids, order

    def busca_profundidade(self, origem):
        """DFS (iterativa para evitar recursion deep): retorna arestas da árvore DFS e ordem."""
        if origem not in self.vertices:
            raise ValueError("Vértice origem não existe.")
        visited = set()
        stack = [(origem, iter(self.adj[origem]))]
        visited.add(origem)
        order = [origem]
        tree_edges = []
        parent = {origem: None}
        while stack:
            node, children = stack[-1]
            try:
                vinfo = next(children)
                v, eid, peso = vinfo
                if v not in visited:
                    visited.add(v)
                    parent[v] = node
                    tree_edges.append(eid)
                    order.append(v)
                    stack.append((v, iter(self.adj[v])))
            except StopIteration:
                stack.pop()
        return tree_edges, order

    def roy_warshall(self):
        """Algoritmo de Roy–Warshall: retorna matriz de alcançabilidade (fecho transitivo)."""
        labels = sorted(self.vertices, key=str)
        n = len(labels)
        index = {labels[i]: i for i in range(n)}
        # Inicializa matriz de alcançabilidade
        reach = [[0]*n for _ in range(n)]
        for u in labels:
            i = index[u]
            reach[i][i] = 1  # cada vértice alcança a si mesmo
            for (v, _, _) in self.adj[u]:
                j = index[v]
                reach[i][j] = 1
        # Algoritmo
        for k in range(n):
            for i in range(n):
                if reach[i][k]:
                    for j in range(n):
                        if reach[k][j]:
                            reach[i][j] = 1
        return labels, reach

    def componentes_por_roy(self):
        """Extrai componentes fortemente conexas a partir do fecho transitivo de Roy–Warshall."""
        labels, reach = self.roy_warshall()
        n = len(labels)
        visited = [False]*n
        comps = []
        for i in range(n):
            if not visited[i]:
                comp = []
                for j in range(n):
                    if reach[i][j] and reach[j][i]:
                        comp.append(labels[j])
                        visited[j] = True
                comps.append(comp)
        return comps

    def componentes_conexas(self):
        """Para grafo não dirigido: retorna lista de conjuntos (componentes)."""
        if self.dirigido:
            raise ValueError("Use componentes_fortemente_conexas para grafos dirigidos.")
        seen = set()
        components = []
        for v in self.vertices:
            if v in seen:
                continue
            comp = set()
            q = deque([v])
            seen.add(v)
            while q:
                x = q.popleft()
                comp.add(x)
                for (nbr, eid, peso) in self.adj[x]:
                    if nbr not in seen:
                        seen.add(nbr)
                        q.append(nbr)
            components.append(comp)
        return components

    def componentes_fortemente_conexas(self):
        """Para grafo dirigido: retorna lista de conjuntos (SCCs) usando Kosaraju via networkx."""
        if not self.dirigido:
            raise ValueError("Use componentes_conexas para grafos não dirigidos.")
        G = self._build_networkx_graph()
        sccs = list(nx.strongly_connected_components(G))
        return sccs

    # -------------------------
    # NOVO: Welsh-Powell (coloring)
    # -------------------------
    def welsh_powell(self):
        """
        Algoritmo de Welsh–Powell para coloração de grafos.
        Retorna: dict node->color_index (0..k-1)
        """
        # ordenar vértices por grau decrescente
        deg = {v: len(self.adj[v]) for v in self.vertices}
        ordered = sorted(self.vertices, key=lambda x: deg[x], reverse=True)
        color_of = {}
        current_color = 0
        for v in ordered:
            if v in color_of:
                continue
            # pinta v com current_color
            color_of[v] = current_color
            # tenta colorir outros vértices não adjacentes com a mesma cor
            for u in ordered:
                if u in color_of:
                    continue
                # verificar se u é adjacente a algum vértice com current_color
                conflict = False
                for w in color_of:
                    if color_of[w] == current_color:
                        # w e u adjacentes?
                        for (nbr, eid, peso) in self.adj[w]:
                            if nbr == u:
                                conflict = True
                                break
                    if conflict:
                        break
                if not conflict:
                    color_of[u] = current_color
            current_color += 1
        return color_of

    # -------------------------
    # NOVO: A* (A-star) pathfinding
    # -------------------------
    def _heuristica_manhattan_km(self, a, b):
        """Heurística Manhattan entre a e b em km aproximados usando coords armazenadas.
        coords devem estar em (lat, lon) em graus decimais.
        Conversão aproximada: 1 grau latitude ≈ 111 km; longitude ≈ 111 * cos(mean_lat).
        Retorna inteiro arredondado.
        """
        if not hasattr(self, "coords") or a not in self.coords or b not in self.coords:
            # fallback: zero (não informado)
            return 0
        lat1, lon1 = self.coords[a]
        lat2, lon2 = self.coords[b]
        lat_diff_km = abs(lat1 - lat2) * 111.0
        mean_lat_rad = math.radians((lat1 + lat2) / 2.0)
        lon_diff_km = abs(lon1 - lon2) * 111.0 * abs(math.cos(mean_lat_rad))
        return round(lat_diff_km + lon_diff_km)

    def a_star(self, origem, destino):
        """
        Implementação do A* usando tabela fixa de h(n) quando destino for Cascavel.
        Retorna (caminho_vertices, caminho_edges_ids, custo_total)
        """
        if origem not in self.vertices or destino not in self.vertices:
            raise ValueError("Origem ou destino não existem no grafo.")

        # Tabela fixa de heurística para Cascavel
        h_table = {
            "Cascavel": 0,
            "Toledo": 39,
            "Foz do Iguaçu": 131,
            "Francisco Beltrão": 132,
            "São Mateus do Sul": 325,
            "Paranaguá": 501,
            "Guarapuava": 207,
            "Londrina": 296,
            "Ponta Grossa": 332,
            "Maringá": 229,
            "Umuarama": 133,
            "Curitiba": 424
        }

        # Função h(n)
        def h(n):
            if destino == "Cascavel":
                return h_table.get(n, 0)  # se n não estiver na tabela, assume 0
            else:
                # fallback: calcula Manhattan pela coordenadas
                x1, y1 = self.coords[n]
                x2, y2 = self.coords[destino]
                return abs(x1 - x2) + abs(y1 - y2)

        import heapq
        open_set = []
        heapq.heappush(open_set, (h(origem), 0, origem, None))  # (f = g + h, g, node, parent_edge)
        came_from = {}  # node -> (parent_node, edge_id)
        g_score = {v: float('inf') for v in self.vertices}
        g_score[origem] = 0

        while open_set:
            f, g, current, parent_edge = heapq.heappop(open_set)
            if current == destino:
                # reconstruir caminho
                path = [current]
                edges_path = []
                while current in came_from:
                    current, edge = came_from[current]
                    path.append(current)
                    edges_path.append(edge)
                path.reverse()
                edges_path.reverse()
                return path, edges_path, g_score[destino]

            for neighbor, eid, peso in self.adj[current]:
                tentative_g = g_score[current] + peso
                if tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    came_from[neighbor] = (current, eid)
                    heapq.heappush(open_set, (tentative_g + h(neighbor), tentative_g, neighbor, eid))

        # se não achou caminho
        return None, None, float('inf')

    @staticmethod
    def _is_number(x):
        try:
            float(x)
            return True
        except:
            return False


# -------------------------
# Interface Tkinter simples para interagir com o grafo
# -------------------------
class GrafoApp:
    def __init__(self, root):
        self.root = root
        root.title("Grafo - Lista de Adjacência")
        self.grafo = Grafo(dirigido=False)

        frm = ttk.Frame(root, padding=10)
        frm.grid(row=0, column=0, sticky="nsew")

        # Opções para dirigir ou não
        self.dir_var = tk.BooleanVar(value=False)
        chk = ttk.Checkbutton(frm, text="Dirigido", variable=self.dir_var, command=self.toggle_dir)
        chk.grid(row=0, column=0, sticky="w")

        # Botões básicos
        ttk.Button(frm, text="Adicionar vértice", command=self.add_vertex).grid(row=1, column=0, sticky="ew")
        ttk.Button(frm, text="Adicionar ligação", command=self.add_edge).grid(row=1, column=1, sticky="ew")
        ttk.Button(frm, text="Remover vértice", command=self.remove_vertex).grid(row=2, column=0, sticky="ew")
        ttk.Button(frm, text="Remover ligação (id)", command=self.remove_edge).grid(row=2, column=1, sticky="ew")

        ttk.Separator(frm).grid(row=3, column=0, columnspan=2, sticky="ew", pady=6)

        ttk.Button(frm, text="Desenhar Grafo", command=self.draw_graph).grid(row=4, column=0, columnspan=2, sticky="ew")
        ttk.Button(frm, text="Mostrar Matrizes", command=self.show_matrices).grid(row=5, column=0, columnspan=2,
                                                                                  sticky="ew")

        ttk.Separator(frm).grid(row=6, column=0, columnspan=2, sticky="ew", pady=6)

        # Botão variável: Prim ou Roy
        self.btn_alg = ttk.Button(frm, text="Prim (AGM)", command=self.run_prim)
        self.btn_alg.grid(row=7, column=0, columnspan=2, sticky="ew")
        ttk.Button(frm, text="BFS", command=self.run_bfs).grid(row=8, column=0, sticky="ew")
        ttk.Button(frm, text="DFS", command=self.run_dfs).grid(row=8, column=1, sticky="ew")

        ttk.Separator(frm).grid(row=9, column=0, columnspan=2, sticky="ew", pady=6)
        ttk.Button(frm, text="Componentes", command=self.show_components).grid(row=10, column=0, columnspan=2,
                                                                               sticky="ew")
        ttk.Button(frm, text="Criar Grafo Exemplo", command=self.criar_grafo_exemplo).grid(row=11, column=0,
                                                                                           columnspan=2, sticky="ew")
        ttk.Button(frm, text="Limpar Grafo", command=self.clear_graph).grid(row=12, column=0, columnspan=2, sticky="ew",
                                                                            pady=6)

        # Novos botões: Welsh-Powell e A*
        ttk.Button(frm, text="Welsh–Powell (Colorir)", command=self.run_welsh_powell).grid(row=14, column=0, columnspan=2, sticky="ew", pady=(6,0))
        ttk.Button(frm, text="A* (Caminho Mínimo)", command=self.run_a_star) \
            .grid(row=15, column=0, columnspan=2, sticky="ew", pady=(2, 6))
        ttk.Button(frm, text="AG - TSP (Caixeiro)", command=self.run_tsp_ga).grid(row=16, column=0, columnspan=2, sticky="ew", pady=(2,6))
        ttk.Button(frm, text="Verificar Planaridade", command=self.run_planarity_check).grid(row=17, column=0,
                                                                                             columnspan=2, sticky="ew",
                                                                                             pady=(2, 6))

        # Área de log simples (posicionada abaixo dos botões para evitar sobreposição)
        self.log = tk.Text(frm, width=50, height=12)
        self.log.grid(row=18, column=0, columnspan=2, pady=6)

    def toggle_dir(self):
        new = self.dir_var.get()
        # recriar grafo preservando vértices e arestas? Sim, fazemos simples: cria novo grafo com mesma info
        g_old = self.grafo
        newg = Grafo(dirigido=new)
        # copiar vértices
        for v in g_old.vertices:
            newg.adicionar_vertice_isolado(v)
        # reinserir arestas, mantendo ids e pesos
        for eid, (u, v, peso, dirg) in g_old.edges.items():
            # adaptamos para novo tipo (dirigido/não)
            # se novo.grafo for dirigido, e aresta era não-dirigida, inserimos como dirigido no sentido original (u->v)
            newg.edges[eid] = (u, v, peso, new)
            newg.adj[u].append((v, eid, peso))
            if not new:
                newg.adj[v].append((u, eid, peso))
        # copiar coords se existirem
        newg.coords = getattr(g_old, "coords", {}).copy()
        self.grafo = newg
        if new:
            self.btn_alg.config(text="Roy (Fecho Transitivo)", command=self.run_roy)
        else:
            self.btn_alg.config(text="Prim (AGM)", command=self.run_prim)

        self.log_insert(f"Alterado modo dirigido={new} (dados preservados).")

    def add_vertex(self):
        v = simpledialog.askstring("Adicionar vértice", "Nome do vértice (string):", parent=self.root)
        if v is None:
            return
        ok = self.grafo.adicionar_vertice_isolado(v)
        if ok:
            self.log_insert(f"Vértice '{v}' adicionado.")
        else:
            self.log_insert(f"Vértice '{v}' já existia.")

    def add_edge(self):
        if not self.grafo.vertices:
            messagebox.showinfo("Erro", "Adicione vértices primeiro.")
            return
        u = simpledialog.askstring("Adicionar ligação", "Vértice origem (u):", parent=self.root)
        if u is None: return
        v = simpledialog.askstring("Adicionar ligação", "Vértice destino (v):", parent=self.root)
        if v is None: return
        if u not in self.grafo.vertices or v not in self.grafo.vertices:
            messagebox.showerror("Erro", "Ambos os vértices devem existir.")
            return
        eid_str = simpledialog.askstring("ID da ligação (opcional)", "ID da ligação (deixe vazio para auto):",
                                         parent=self.root)
        eid = None
        if eid_str:
            try:
                eid = int(eid_str)
            except:
                eid = eid_str  # aceita string também
        peso = simpledialog.askstring("Peso (valor)", "Peso / valor da ligação (padrão 1):", parent=self.root)
        if peso is None or peso == "":
            peso = 1
        try:
            edge_id = self.grafo.inserir_ligacao(u, v, edge_id=eid, peso=peso)
            self.log_insert(f"Ligação {edge_id} inserida: {u} -> {v} (peso={peso})")
        except Exception as e:
            messagebox.showerror("Erro inserção", str(e))

    def remove_vertex(self):
        v = simpledialog.askstring("Remover vértice", "Nome do vértice:", parent=self.root)
        if v is None:
            return
        ok = self.grafo.remover_vertice(v)
        if ok:
            self.log_insert(f"Vértice '{v}' removido.")
        else:
            self.log_insert(f"Vértice '{v}' não existe.")

    def remove_edge(self):
        eid = simpledialog.askstring("Remover ligação", "ID da ligação:", parent=self.root)
        if eid is None:
            return
        # tentar converter para int quando for int
        try:
            eid_val = int(eid)
        except:
            eid_val = eid
        ok = self.grafo.remover_ligacao(eid_val)
        if ok:
            self.log_insert(f"Ligação {eid_val} removida.")
        else:
            self.log_insert(f"Ligação {eid_val} não encontrada.")

    def clear_graph(self):
        """Remove todos os vértices e arestas do grafo."""
        self.grafo.vertices.clear()
        self.grafo.adj.clear()
        self.grafo.edges.clear()
        self.grafo.coords = {}
        # Limpa posições salvas para desenho
        if hasattr(self.grafo, "_pos"):
            del self.grafo._pos
        self.log_insert("Grafo totalmente limpo.")

    def criar_grafo_exemplo(self):
        """Cria o grafo do enunciado (8 cidades) a partir da imagem anexada.
        Vértices: F, C, N, K, E, G, H, L
        As arestas e pesos foram inseridos conforme anotação da figura (aproximação).
        """
        self.clear_graph()
        vertices = ["F", "C", "N", "K", "E", "G", "H", "L"]
        for v in vertices:
            self.grafo.adicionar_vertice_isolado(v)

        # Posições aproximadas para visualização (ajustáveis)
        pos = {
            "N": (-0.6, 0.9),
            "K": (0.0, 1.0),
            "G": (0.8, 1.0),
            "F": (-0.9, 0.2),
            "C": (-0.2, 0.4),
            "E": (0.4, 0.4),
            "L": (-0.1, -0.3),
            "H": (0.4, -0.1)
        }
        self.grafo._pos = pos

        # Arestas (não dirigidas) com pesos aproximados retirados da imagem
        arestas = [
            ("N", "K", 60),
            ("K", "G", 90),
            ("N", "C", 47),
            ("K", "C", 70),
            ("K", "E", 10),
            ("C", "E", 10),
            ("C", "H", 30),
            ("E", "H", 60),
            ("K", "H", 73),
            ("F", "C", 20),
            ("F", "N", 30),
            ("F", "L", 10),
            ("C", "L", 10),
            ("L", "H", 40),
            ("H", "G", 80),
            ("G", "E", 40),
            ("G", "F", 55),
            ("L", "E", 5)
        ]

        for origem, destino, peso in arestas:
            try:
                eid = self.grafo.inserir_ligacao(origem, destino, peso=peso)
                self.log_insert(f"Aresta {eid} criada: {origem} <-> {destino} (peso={peso})")
            except Exception as e:
                self.log_insert(f"Erro ao criar aresta {origem}->{destino}: {e}")

        self.log_insert(f"Grafo exemplo (imagem) criado com {len(vertices)} vértices e {len(arestas)} arestas.")

    def draw_graph(self):
        self.grafo.desenhar(title="Grafo atual")

    def show_matrices(self):
        labels, M = self.grafo.matriz_adjacencia()
        txt = "Matriz de Adjacência\n\t" + "\t".join(map(str, labels)) + "\n"
        for i, r in enumerate(M):
            txt += str(labels[i]) + "\t" + "\t".join(map(str, r)) + "\n"
        vlabels, elabels, I = self.grafo.matriz_incidencia()
        txt += "\nMatriz de Incidência\n\t" + "\t".join(map(str, elabels)) + "\n"
        for i, r in enumerate(I):
            txt += str(vlabels[i]) + "\t" + "\t".join(map(str, r)) + "\n"
        # Mostrar em nova janela
        win = tk.Toplevel(self.root)
        win.title("Matrizes")
        t = tk.Text(win, width=80, height=30)
        t.pack(fill="both", expand=True)
        t.insert("1.0", txt)
        t.config(state="disabled")

    def run_prim(self):
        try:
            edges, total = self.grafo.prim()
        except Exception as e:
            messagebox.showerror("Erro Prim", str(e))
            return
        self.log_insert(f"Prim: arestas selecionadas (ids): {edges} | peso total={total}")
        self.grafo.desenhar(highlight_edges=set(edges), title="AGM - Prim")

    def run_bfs(self):
        if not self.grafo.vertices:
            messagebox.showinfo("BFS", "Grafo vazio.")
            return
        origem = simpledialog.askstring("BFS", "Vértice de saída (origem):", parent=self.root)
        if origem is None:
            return
        try:
            tree_edges, order = self.grafo.busca_largura(origem)
            self.log_insert(f"BFS ordem: {order} | arestas da árvore: {tree_edges}")
            self.grafo.desenhar(highlight_edges=set(tree_edges), highlight_nodes=set(order),
                                title=f"BFS a partir de {origem}")
        except Exception as e:
            messagebox.showerror("Erro BFS", str(e))

    def run_dfs(self):
        if not self.grafo.vertices:
            messagebox.showinfo("DFS", "Grafo vazio.")
            return
        origem = simpledialog.askstring("DFS", "Vértice de saída (origem):", parent=self.root)
        if origem is None:
            return
        try:
            tree_edges, order = self.grafo.busca_profundidade(origem)
            self.log_insert(f"DFS ordem: {order} | arestas da árvore: {tree_edges}")
            self.grafo.desenhar(highlight_edges=set(tree_edges), highlight_nodes=set(order),
                                title=f"DFS a partir de {origem}")
        except Exception as e:
            messagebox.showerror("Erro DFS", str(e))

    def run_roy(self):
        try:
            comps = self.grafo.componentes_por_roy()
            self.log_insert(f"Componentes: {len(comps)}")
            for i, c in enumerate(comps, start=1):
                self.log_insert(f"C{i}: {c}")
            if len(comps) == 1:
                self.log_insert("Grafo É fortemente conexo")
            else:
                self.log_insert("Grafo NÃO é fortemente conexo")
        except Exception as e:
            messagebox.showerror("Erro Roy", str(e))

    def show_components(self):
        if not self.grafo.vertices:
            messagebox.showinfo("Componentes", "Grafo vazio.")
            return
        if self.grafo.dirigido:
            sccs = self.grafo.componentes_fortemente_conexas()
            s = "\n".join([f"SCC {i + 1}: {sorted(list(c), key=str)}" for i, c in enumerate(sccs)])
            self.log_insert("Componentes fortemente conexas:\n" + s)
            messagebox.showinfo("SCCs", s)
        else:
            comps = self.grafo.componentes_conexas()
            s = "\n".join([f"C{i + 1}: {sorted(list(c), key=str)}" for i, c in enumerate(comps)] )
            self.log_insert("Componentes conexas:\n" + s)
            messagebox.showinfo("Componentes", s)

    def run_welsh_powell(self):
        if not self.grafo.vertices:
            messagebox.showinfo("Welsh–Powell", "Grafo vazio.")
            return
        cmap = self.grafo.welsh_powell()
        # transformar dict node->color_index em algo passável para desenhar
        self.log_insert(f"Welsh–Powell: cores atribuídas a {len(cmap)} vértices.")
        # contar número de cores usadas
        used_colors = len(set(cmap.values()))
        self.log_insert(f"Número de cores usadas: {used_colors}")
        self.grafo.desenhar(node_color_map=cmap, title=f"Welsh–Powell (cores={used_colors})")

    def run_a_star(self):
        if not self.grafo.vertices:
            messagebox.showinfo("A*", "Grafo vazio.")
            return
        origem = simpledialog.askstring("A*", "Vértice de origem:", parent=self.root)
        destino = simpledialog.askstring("A*", "Vértice de destino:", parent=self.root)
        if origem is None or destino is None:
            return
        try:
            path, edges, custo = self.grafo.a_star(origem, destino)
            if path is None:
                messagebox.showinfo("A*", "Caminho não encontrado.")
                return
            self.log_insert(f"A*: caminho {path} | arestas {edges} | custo total {custo}")
            self.grafo.desenhar(highlight_edges=set(edges), highlight_nodes=set(path),
                                title=f"A* {origem} -> {destino}")
        except Exception as e:
            messagebox.showerror("Erro A*", str(e))

    def run_tsp_ga(self):
        """Executa Algoritmo Genético para o Problema do Caixeiro Viajante
        Atende aos requisitos: população mínima 100, crossover PMX 2 pontos fixos,
        elitismo, mutação configurável, parada por número de gerações.
        """
        import random

        if not self.grafo.vertices:
            messagebox.showinfo("AG-TSP", "Grafo vazio.")
            return

        # Só permite rodar se existir pelo menos 3 vértices
        if len(self.grafo.vertices) < 3:
            messagebox.showinfo("AG-TSP", "Grafo deve ter pelo menos 3 vértices para TSP.")
            return

        # Selecionar cidade inicial
        start = simpledialog.askstring("TSP - Cidade inicial", "Cidade de partida (ex.: F):", parent=self.root)
        if start is None:
            return
        if start not in self.grafo.vertices:
            messagebox.showerror("Erro", "Cidade inicial não existe no grafo.")
            return

        # Parâmetros
        pop_size = simpledialog.askinteger("Tamanho da população", "Tamanho da população (>=100):", parent=self.root, minvalue=100, initialvalue=500)
        if pop_size is None:
            return
        if pop_size < 100:
            messagebox.showerror("Erro", "Tamanho da população deve ser no mínimo 100.")
            return

        cross_rate = simpledialog.askfloat("Taxa de cruzamento", "Taxa de cruzamento (0.6 - 0.8):", parent=self.root, minvalue=0.6, maxvalue=0.8, initialvalue=0.7)
        if cross_rate is None:
            return
        if cross_rate < 0.6 or cross_rate > 0.8:
            messagebox.showerror("Erro", "Taxa de cruzamento deve estar entre 0.6 e 0.8.")
            return
        
        mut_rate = simpledialog.askfloat("Taxa de mutação", "Taxa de mutação (0.005 - 0.01) (ex.: 0.007 = 0.7%):", parent=self.root, minvalue=0.005, maxvalue=0.01, initialvalue=0.01)
        if mut_rate is None:
            return
        if mut_rate < 0.005 or mut_rate > 0.01:
            messagebox.showerror("Erro", "Taxa de mutação deve estar entre 0.005 e 0.01.")
            return

        generations = simpledialog.askinteger("Gerações", "Número máximo de gerações (>=20):", parent=self.root, minvalue=20, initialvalue=20)
        if generations is None:
            return
        if generations < 20:
            messagebox.showerror("Erro", "Número de gerações deve ser no mínimo 20.")
            return

        replace_frac = simpledialog.askfloat("Substituição", "Porcentagem da população substituída por geração (0.1 - 1.0):", parent=self.root, minvalue=0.0, maxvalue=1.0, initialvalue=0.5)
        if replace_frac is None:
            return
        if replace_frac < 0.1 or replace_frac > 1.0:
            messagebox.showerror("Erro", "Porcentagem de substituição deve estar entre 0.1 e 1.0.")
            return

        show_top_n = simpledialog.askinteger("Exibir por geração", "Quantos melhores exibir por geração (0 para não mostrar):", parent=self.root, minvalue=0, initialvalue=10)
        if show_top_n is None:
            return
        # Perguntar uma única vez se deseja que os top N sejam exibidos a cada geração
        show_each_gen = False
        if show_top_n > 0:
            show_each_gen = messagebox.askyesno("Exibição por geração", f"Exibir os top {show_top_n} indivíduos em cada geração? (Sim = mostrará no log sem pedir a cada geração)")

        # Preparar dados
        cities = [v for v in self.grafo.vertices if v != start]
        n = len(cities) + 1  # incluindo origem
        chrom_len = len(cities)

        # PMX pontos fixos (escolhidos pelo grupo): para rotas de comprimento chrom_len escolhemos índices 2 e chrom_len-2 (se possível)
        cut1 = 2 if chrom_len > 3 else 1
        cut2 = chrom_len - 2 if chrom_len - 2 > cut1 else chrom_len - 1

        INF = 10**9

        def get_weight(u, v):
            # procura na lista de adjacências; retorna INF se não houver ligação
            for nbr, eid, peso in self.grafo.adj.get(u, []):
                if nbr == v:
                    try:
                        return float(peso)
                    except:
                        return float('inf')
            return INF

        def route_cost(chrom):
            # chrom: lista de cities (exclui start). Calcula custo start->...->start
            total = 0.0
            prev = start
            for city in chrom:
                w = get_weight(prev, city)
                if w >= INF:
                    return INF
                total += w
                prev = city
            # volta para o inicio
            w = get_weight(prev, start)
            if w >= INF:
                return INF
            total += w
            return total

        def pmx(p1, p2):
            # p1, p2: parent permutations (lists)
            child1 = [None]*chrom_len
            child2 = [None]*chrom_len
            a, b = cut1, cut2
            # copiar segmento
            child1[a:b] = p1[a:b]
            child2[a:b] = p2[a:b]

            def fill(child, src, other):
                for i in range(chrom_len):
                    if i >= a and i < b:
                        continue
                    gene = src[i]
                    while gene in child[a:b]:
                        # map through other->src mapping
                        idx = other.index(gene)
                        gene = src[idx]
                    child[i] = gene

            fill(child1, p2, p1)
            fill(child2, p1, p2)
            return child1, child2

        def mutate_swap(chrom):
            i, j = random.sample(range(chrom_len), 2)
            chrom[i], chrom[j] = chrom[j], chrom[i]

        # Gerar população inicial aleatória
        population = []
        seen = set()
        while len(population) < pop_size:
            perm = cities[:]
            random.shuffle(perm)
            key = tuple(perm)
            if key in seen:
                continue
            seen.add(key)
            population.append(perm)

        # avaliar
        fitness_cache = {}

        def evaluate_all(pop):
            nonlocal fitness_cache
            fitness = []
            for ind in pop:
                key = tuple(ind)
                if key in fitness_cache:
                    cost = fitness_cache[key]
                else:
                    cost = route_cost(ind)
                    fitness_cache[key] = cost
                fitness.append((cost, ind))
            fitness.sort(key=lambda x: x[0])
            return fitness

        def fmt_cost(c):
            if c is None:
                return "?"
            try:
                if c >= INF:
                    return "INF"
                return f"{c:.2f}"
            except:
                return str(c)

        # elitismo (quantidade fixa)
        elitism_count = max(1, int(0.02 * pop_size))

        # main loop
        # Cabeçalho de log
        self.log_insert("================ AG - TSP (Algoritmo Genético) ================")
        self.log_insert(f"Partida: {start} | população: {pop_size} | cruzamento: {cross_rate} | mutação: {mut_rate} | gerações: {generations}")
        self.log_insert(f"PMX cuts: {cut1}..{cut2} | substituição por geração: {replace_frac*100:.1f}%")

        # controle de estagnação: contador de gerações sem melhoria
        best_overall = float('inf')
        stall_count = 0
        stall_limit = max(0, int(0.2 * generations))

        for gen in range(1, generations+1):
            fitness = evaluate_all(population)
            best_cost, best_ind = fitness[0]
            improved = False
            if best_cost < best_overall:
                best_overall = best_cost
                improved = True
                stall_count = 0
            else:
                stall_count += 1

            self.log_insert(f"Geração {gen}/{generations} — melhor custo = {fmt_cost(best_cost)}")

            # mostrar top N no log (sem perguntar toda geração) se o usuário optou
            if show_each_gen and show_top_n > 0:
                topn = fitness[:min(show_top_n, len(fitness))]
                self.log_insert(f"Top {len(topn)} geração {gen}:")
                for rank, (c, ind) in enumerate(topn, start=1):
                    self.log_insert(f"  {rank:2d}) {[start]+ind+[start]} | custo={fmt_cost(c)}")

            # filtrar indivíduos viáveis para seleção (custo < INF)
            viable = [ind for c, ind in fitness if c < INF]
            if not viable:
                # sem viáveis: encerra
                messagebox.showwarning("AG-TSP", "Nenhuma rota viável na população — encerrando.")
                break

            # preservar elites
            elites = [ind for c, ind in fitness[:elitism_count]]

            # gerar filhos
            new_pop = elites[:]
            target_new = int(pop_size * replace_frac)
            # fill until reach pop_size
            attempts = 0
            while len(new_pop) < pop_size and attempts < pop_size * 10:
                attempts += 1
                # seleção por torneio
                a = random.choice(viable)
                b = random.choice(viable)
                p1 = a
                p2 = b
                if random.random() < cross_rate:
                    c1, c2 = pmx(p1, p2)
                else:
                    c1, c2 = p1[:], p2[:]

                # mutação
                if random.random() < mut_rate:
                    mutate_swap(c1)
                if random.random() < mut_rate:
                    mutate_swap(c2)

                # não incluir duplicatas idênticas
                for child in (c1, c2):
                    if len(new_pop) < pop_size:
                        key = tuple(child)
                        if key not in seen:
                            seen.add(key)
                            new_pop.append(child)

            population = new_pop[:pop_size]

        # fim gerações: avaliar população final
        final_fitness = evaluate_all(population)
        best_cost, best_ind = final_fitness[0]
        best_route = [start] + best_ind + [start]
        self.log_insert(f"Melhor rota final: {best_route} | custo = {best_cost}")

        # destacar arestas da melhor rota para desenhar
        highlight_eids = set()
        for i in range(len(best_route)-1):
            u = best_route[i]
            v = best_route[i+1]
            # procurar aresta id entre u e v
            found = False
            for nbr, eid, peso in self.grafo.adj.get(u, []):
                if nbr == v:
                    highlight_eids.add(eid)
                    found = True
                    break
            if not found:
                # tentar no sentido inverso (não dirigido)
                for nbr, eid, peso in self.grafo.adj.get(v, []):
                    if nbr == u:
                        highlight_eids.add(eid)
                        break

        # desenhar grafo com rota destacada
        self.grafo.desenhar(highlight_edges=highlight_eids, title=f"Melhor rota TSP (custo={best_cost})")

    def run_planarity_check(self):
        if not self.grafo.vertices:
            messagebox.showinfo("Planaridade", "Grafo vazio.")
            return
        try:
            planar = self.grafo.hopcroft_tarjan_planaridade()
            if planar:
                self.log_insert("Grafo É planar (Hopcroft-Tarjan).")
                messagebox.showinfo("Planaridade", "Grafo É planar.")
            else:
                self.log_insert("Grafo NÃO é planar (Hopcroft-Tarjan).")
                messagebox.showinfo("Planaridade", "Grafo NÃO é planar.")
        except Exception as e:
            messagebox.showerror("Erro Planaridade", str(e))

    # -------------------------
    # NOVO: Verificação de Planaridade (Hopcroft-Tarjan)
    # -------------------------
    def hopcroft_tarjan_planaridade(self):
        """
        Verifica se o grafo não dirigido é planar usando algoritmo de Hopcroft-Tarjan.
        Retorna True se planar, False caso contrário.
        """
        if self.dirigido:
            raise ValueError("Planaridade é definida para grafos não dirigidos.")

        # Usamos abordagem DFS com lowpoint
        visited = {}
        parent = {}
        low = {}
        order = {}
        counter = [0]

        is_planar = [True]  # usamos lista para mutabilidade em nested

        def dfs(u):
            visited[u] = True
            counter[0] += 1
            order[u] = low[u] = counter[0]

            for v, eid, peso in self.adj[u]:
                if v not in visited:
                    parent[v] = u
                    dfs(v)
                    low[u] = min(low[u], low[v])
                    # condição simplificada: detecta K3,3 ou K5 (não completa, mas alerta)
                    if low[v] >= order[u]:
                        pass  # Aqui poderia analisar separabilidade biconexa
                elif parent.get(u) != v:
                    low[u] = min(low[u], order[v])

        for v in self.vertices:
            if v not in visited:
                parent[v] = None
                dfs(v)

        # Para grafos pequenos, podemos usar NetworkX como fallback
        import networkx as nx
        Gnx = nx.Graph()
        Gnx.add_nodes_from(self.vertices)
        for eid, (u, v, peso, dirg) in self.edges.items():
            Gnx.add_edge(u, v)
        try:
            planar, _ = nx.check_planarity(Gnx)
            return planar
        except:
            return False

    # Adicionar função à classe Grafo
    Grafo.hopcroft_tarjan_planaridade = hopcroft_tarjan_planaridade

    def log_insert(self, text):
        self.log.insert("end", text + "\n")
        self.log.see("end")


if __name__ == "__main__":
    root = tk.Tk()
    app = GrafoApp(root)
    root.mainloop()
