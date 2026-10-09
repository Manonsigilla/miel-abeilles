# 🐝 Le Miel et les Abeilles

A simulation of a **bee colony** searching for the shortest route to forage
through a field of flowers, using a **genetic algorithm**.

A bee leaves the hive, visits **every flower exactly once**, then returns to the
hive. The goal is to **minimize the total distance travelled**.

This is a concrete instance of the **Travelling Salesman Problem** (TSP), a
classic combinatorial optimization problem.

---

## 📌 The problem

| Item | Value |
|---|---|
| Hive position | `(500, 500)` |
| Number of flowers | 50 (`data/champ_pissenlit_sauge.csv`) |
| Population size | 101 bees |
| Number of generations | 1000 |

**Constraint**: every flower is visited exactly once.

**Objective function to minimize** (the *fitness*): the length of the route
`hive → flower₁ → flower₂ → … → flower₅₀ → hive`.

### Why we can't try every route

The number of possible visiting orders is `50!` ≈ **3.0 × 10⁶⁴**. Accounting for
symmetries (direction of travel and starting point), roughly `49! / 2` genuinely
distinct routes remain — an astronomical number. We therefore cannot enumerate
the solutions: we use a **heuristic method**, the genetic algorithm, which finds
a *very good* solution in a reasonable amount of time.

---

## 🧬 How the genetic algorithm works

The idea is to mimic **natural selection**: the best solutions reproduce, the
worst disappear, and mutations bring novelty.

| Biological term | Computer science term | In this project |
|---|---|---|
| Individual | Candidate solution | A bee |
| Genome (DNA) | Encoding of the solution | The **visiting order** of the 50 flowers |
| Fitness | Quality of the solution | The **inverse** of the distance (shorter = better) |
| Generation | Iteration | One full reproduction cycle |

### The 5 steps (repeated 1000 times)

1. **Initial population** — We create 101 bees, each with a **random** visiting
   order (`random.shuffle`).
2. **Evaluation** — We compute the total distance of each bee
   (`Bee.compute_path_length`).
3. **Selection** — We sort the bees from best to worst and keep the
   `n_parents = max(2, 101 × selection_rate)` best ones as parents.
   The best bee is **always** kept (*elitism*): it can never be lost.
4. **Crossover** — We pick two parents at random and build a child by combining
   their routes (see below).
5. **Mutation** — With probability `mutation_rate`, we **swap two flowers** in the
   child's visiting order.

We repeat until the population is back to 101 bees, then move on to the next
generation.

### Ordered crossover (OX1)

A naive crossover would produce invalid routes (missing or duplicated flowers).
We therefore use an **ordered crossover**:

```
Parent 1 : [A B | C D E | F G]
Parent 2 : [D E G A F B C]

1. Keep a random segment from Parent 1 :  [C D E]
2. Fill in with the flowers from Parent 2  A F B G
   that are not already present, in order.

Child    : [A F B C D E G]
```

Every flower appears **exactly once**: the route stays valid.

### Swap mutation

```
Before : [A F B C D E G]
            ↕ swap two positions
After  : [A D B C F E G]
```

The mutation is a **swap of two flowers**: the smallest perturbation that
preserves a valid order (no duplicates, no missing flower).

---

## 📂 Project structure

```
miel-abeilles/
├── config.py          # Global parameters (population, rates, paths)
├── beehive.py         # Bee and Beehive classes: the core of the algorithm
├── main.py            # Data loading + plots
├── analyse.ipynb      # Notebook: comparisons, results, genealogy tree
├── requirements.txt   # Python dependencies
└── data/
    └── champ_pissenlit_sauge.csv   # (x, y) coordinates of the 50 flowers
```

### File details

- **`config.py`** — Every setting in one place: `NB_BEES`, `NB_GENERATIONS`,
  `MUTATION_RATE`, `SELECTION_RATE`, `BEEHIVE_POSITION`, `GENEALOGY_DEPTH`.
- **`beehive.py`**
  - `Bee`: one solution (a route) and how its length is computed.
  - `Beehive`: the population and the `crossover`, `mutate`, `next_generation`
    operators.
  - `get_genealogy_tree`: rebuilds the ancestor tree of a given bee.
- **`main.py`** — `load_data`, `run_beehive`, `plot_comparison` and
  `plot_genealogy` (visualizations).
- **`analyse.ipynb`** — The full experimental workflow and the report figures.

---

## ⚙️ Installation

```bash
# From the miel-abeilles/ folder
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## ▶️ Usage

Run the main script (comparisons + best route):

```bash
python main.py
```

Or explore the full workflow in the notebook:

```bash
jupyter notebook analyse.ipynb
```

---

## 📊 Results and parameter tuning

Both key parameters were chosen **experimentally** by comparing the convergence
curves.

### Mutation rate

| Value | Observation |
|---|---|
| `0.01` | Too rare: the population stagnates at a high distance (not enough exploration). |
| `0.1`  | **Good trade-off**: fast convergence to a low, stable distance. |
| `0.3`  | No further gain, but more useless variation. |

### Selection rate

| Value | Observation |
|---|---|
| `0.1` | Low diversity: fast convergence but it stagnates too high. |
| `0.5` | **Good exploration / exploitation trade-off**. |
| `0.9` | Slower convergence but a lower final distance. |

**Chosen settings: `MUTATION_RATE = 0.1` and `SELECTION_RATE = 0.5`.**

### Typical observed magnitudes

On a typical run (`mutation = 0.1`, `selection = 0.5`, 1000 generations):

| Metric | Approximate value |
|---|---|
| Average distance, generation 0 | ≈ 24,400 |
| Average distance, generation 999 | ≈ 7,700 |
| Best bee's distance | ≈ 7,200 |

The population's average distance drops by roughly **70%** over 1000
generations. *(Figures vary from run to run — the algorithm is stochastic.)*

### Generated visualizations

- **Rate comparison** (mutation and selection): average distance per generation.
- **Best bee's route**: the best route found across the field.
- **Genealogy tree**: the best bee's ancestry over the last 10 generations (each
  colour = one generation, via `networkx`).

---

## ⚠️ Limitations and possible improvements

- **Swap mutation** is simple but weak for the TSP: a segment inversion (*2-opt*)
  or an order-based mutation would give better results.
- No **local search**: hybridizing the algorithm with *2-opt* would speed up
  convergence significantly.
- Parameters are set by hand: adaptive tuning or an automatic search
  (*grid search*) could optimize them.
- The algorithm does not guarantee the global optimum — it is a heuristic.

---

## 🎓 What this project demonstrates

- Modelling a real problem (the TSP) and solving it without brute force.
- Designing an **objective function** and optimizing it in a *gradient-free* way.
- The **exploration / exploitation** trade-off, central to data science.
- Working with **discrete, combinatorial** search spaces.

---

## 👩💻 Author

**Manon Sigaud** — project carried out as part of data science studies.

## 📦 Dependencies

`matplotlib`, `networkx`, `jupyter` (see `requirements.txt`).
