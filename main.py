import csv
import matplotlib.pyplot as plt
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


