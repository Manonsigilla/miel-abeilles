import csv
import matplotlib.pyplot as plt
from config import FLOWERS_PATH, NB_GENERATIONS
from beehive import Beehive, Bee

def load_data(path):
    flowers = []
    with open(path, newline='') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row

        for row in reader:
            flowers.append((int(row[0]), int(row[1])))

    return flowers

def main():
    flowers = load_data(FLOWERS_PATH)
    b = Beehive(flowers)
    b.init_bees()

    history = []
    
    for i in range(NB_GENERATIONS):
        b.next_generation()
        history.append(b.get_average_distance())

    plt.plot(history)
    plt.xlabel("Generation")
    plt.ylabel("Average Distance")
    plt.title("Average Distance Evolution Over Generations")
    plt.show()

if __name__ == "__main__":
    main()


