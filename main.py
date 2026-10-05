import csv
import matplotlib.pyplot as plt
import networkx as nx
from config import FLOWERS_PATH, NB_GENERATIONS
from beehive import Beehive

def load_data(path):
    flowers = []
    with open(path, newline='') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row

        for row in reader:
            flowers.append((int(row[0]), int(row[1])))

    return flowers

def run_beehive(flowers, mutation_rate, selection_rate):
    b = Beehive(flowers, mutation_rate=mutation_rate, selection_rate=selection_rate)
    b.init_bees()
    history = []
    for i in range(NB_GENERATIONS):
        b.next_generation()
        history.append(b.get_average_distance())
    return b, history

def plot_comparison(flowers, param_name, values, fixed_mutation=0.1, fixed_selection=0.5):
    for v in values:
        if param_name == "mutation":
            _, history = run_beehive(flowers, mutation_rate=v, selection_rate=fixed_selection)
            label = f"mutation={v}"
        else:
            _, history = run_beehive(flowers, mutation_rate=fixed_mutation, selection_rate=v)
            label = f"selection={v}"
        plt.plot(history, label=label)
    plt.legend()
    plt.xlabel("Generation")
    plt.ylabel("Average Distance")
    plt.title(f"Comparison for {param_name}")
    plt.show()

def plot_genealogy(beehive, root_bee, max_depth):
    """Draw the genealogy tree of root_bee, going back max_depth generations.

    Each generation gets its own colour, the root (the best bee) sits at the bottom.
    """
    tree = beehive.get_genealogy_tree(root_bee, max_depth)

    # One horizontal row per generation. Edges go parent -> child, so we walk the reversed graph to get the layers: layer 0 is the root, higher layers are ancestors.
    layers = list(nx.bfs_layers(tree.reverse(), root_bee.bee_id))
    positions = {}
    for depth, layer in enumerate(layers):
        for i, node in enumerate(layer):
            positions[node] = (i - (len(layer) - 1) / 2, depth)

    # Distinct colour per generation (tab20 cycles if there are more than 20 generations).
    cmap = plt.get_cmap("tab20")
    colours = [cmap(depth % cmap.N) for depth in range(len(layers))]

    plt.figure(figsize=(14, 8))
    # Draw edges as plain grey lines, using an undirected copy so networkx adds no arrowheads that would clutter such a dense tree.
    nx.draw_networkx_edges(tree.to_undirected(), positions, edge_color="lightgrey", width=0.5)
    for depth, layer in enumerate(layers):
        nx.draw_networkx_nodes(tree, positions, nodelist=list(layer),
                               node_color=[colours[depth]] * len(layer), node_size=15)
        # Empty scatter, only used to build the legend.
        label = "best bee" if depth == 0 else f"{depth} generation(s) back"
        plt.scatter([], [], color=colours[depth], s=40, label=label)

    plt.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), ncol=1, fontsize=8)
    plt.title(f"Genealogy tree - {max_depth} generations ({len(tree.nodes)} bees)")
    plt.axis("off")
    plt.subplots_adjust(right=0.82)
    plt.show()

def main():
    flowers = load_data(FLOWERS_PATH)

    plot_comparison(flowers, "mutation", [0.01, 0.1, 0.3])
    plot_comparison(flowers, "selection", [0.1, 0.5, 0.9])

    # Run the beehive with specific parameters and plot the best path found
    b, history = run_beehive(flowers, mutation_rate=0.1, selection_rate=0.5)
    best = b.get_best_bee()
    xs = [b.beehive_position[0]] + [flower[0] for flower in best.path] + [b.beehive_position[0]]
    ys = [b.beehive_position[1]] + [flower[1] for flower in best.path] + [b.beehive_position[1]]
    plt.figure()
    plt.plot(xs, ys, marker='o')
    plt.scatter(*b.beehive_position, color='red', label='Beehive', s=100, zorder=5, marker='s')
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Best Bee Path")
    plt.show()   

if __name__ == "__main__":
    main()


