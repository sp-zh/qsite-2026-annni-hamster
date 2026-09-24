from __future__ import annotations

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from IPython.display import HTML
from matplotlib.animation import FuncAnimation

from .annni import coupling_edges, coupling_positions


def plot_coupling_graph(n_qubits: int, periodic: bool = True) -> tuple[plt.Figure, plt.Axes]:
    graph = nx.Graph()
    graph.add_nodes_from(range(n_qubits))
    edges = coupling_edges(n_qubits=n_qubits, periodic=periodic)
    graph.add_edges_from(edges["nearest"])
    positions = coupling_positions(n_qubits)

    fig, ax = plt.subplots(figsize=(5, 5))
    nx.draw_networkx_nodes(graph, positions, node_color="#d9edf7", node_size=700, ax=ax)
    nx.draw_networkx_labels(graph, positions, font_size=10, ax=ax)
    nx.draw_networkx_edges(graph, positions, edgelist=edges["nearest"], width=2.5, edge_color="#1f77b4", ax=ax)
    nx.draw_networkx_edges(
        graph,
        positions,
        edgelist=edges["next_nearest"],
        width=2.0,
        style="dashed",
        edge_color="#ff7f0e",
        ax=ax,
    )
    ax.set_title("ANNNI couplings: nearest (solid) and next-nearest (dashed)")
    ax.set_axis_off()
    return fig, ax


def plot_observable_heatmap(
    values: np.ndarray,
    kappas: np.ndarray,
    hs: np.ndarray,
    title: str,
    cmap: str = "viridis",
) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    image = ax.imshow(
        values,
        origin="lower",
        aspect="auto",
        extent=[kappas.min(), kappas.max(), hs.min(), hs.max()],
        cmap=cmap,
    )
    ax.set_xlabel(r"$\kappa$")
    ax.set_ylabel(r"$h$")
    ax.set_title(title)
    fig.colorbar(image, ax=ax, shrink=0.9)
    return fig, ax


def animate_linecut(
    kappas: np.ndarray,
    hs: np.ndarray,
    values: np.ndarray,
    ylabel: str,
    title: str,
) -> HTML:
    fig, ax = plt.subplots(figsize=(6, 4))
    line, = ax.plot(kappas, values[0], color="#1f77b4", lw=2)
    ax.set_xlim(float(kappas.min()), float(kappas.max()))
    ax.set_ylim(float(np.min(values)) - 0.05, float(np.max(values)) + 0.05)
    ax.set_xlabel(r"$\kappa$")
    ax.set_ylabel(ylabel)

    def update(frame: int):
        line.set_ydata(values[frame])
        ax.set_title(f"{title} at h={hs[frame]:.2f}")
        return (line,)

    animation = FuncAnimation(fig, update, frames=len(hs), interval=500, blit=False)
    plt.close(fig)
    return HTML(animation.to_jshtml())
