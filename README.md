# NetworkAnalysis

A comprehensive Python toolkit for analyzing complex networks and graphs. This project implements various graph metrics, diameter estimation heuristics, estimates shortest-path distances via landmark methods, and network robustness simulations.

## Features

### Basic Graph Metrics
- **Connected Components**: Find all connected components, largest CC size, and its vertices.
- **Degree Analysis**: Degree statistics and degree distribution plotting.
- **Clustering**: Average and global clustering coefficients.
- **Triangle Counting**: Efficient counting of triangles in the graph.

### Diameter Estimation
Heuristics for estimating the diameter of large graphs:
- Double Sweep algorithm
- Sampled diameter with percentiles
- Snowball diameter percentile estimation

### Strongly Connected Components
- Implementation of **Kosaraju's algorithm** to find the number of SCCs and the largest strongly connected component.

### Landmark-Based Distance Estimation
Estimate distances between nodes using a set of landmarks:
- **Landmarks-Basic**: Basic landmark distance estimation.
- **Landmarks-SC**: Advanced estimation using Shortest Path Trees (SPT) and Lowest Common Ancestor (LCA).
- **Selection Strategies**: 
  - Random selection
  - Degree-based selection
  - Best coverage selection

### Network Robustness
Simulate node removal to evaluate network resilience:
- **Random Removal**: Nodes are removed uniformly at random.
- **Degree-Based Removal**: Targeted removal of high-degree nodes.
- **Evaluation**: Metrics to track how the network structure degrades under attack.

## Project Structure

```text
src/                    # Core library modules
    analysis.py         # Graph metrics, SCC, clustering, triangles
    graph.py            # Graph data structure
    landmarks.py        # Landmark-based estimation and selection strategies
    robustness.py       # Network robustness simulations
    utils.py            # BFS utilities
experiments/            # Scripts to run experiments on datasets
    run_analysis.py     # Run basic graph metrics analysis
    run_landmarks.py    # Run landmark estimation experiments
    run_robustness.py   # Run robustness simulations
    plot_results.py     # Visualization utilities
tests/                  # Unit tests for all modules
cli.py                  # Command-line interface
requirements.txt        # Python dependencies
pyproject.toml          # Project configuration
check_all.sh            # Script to run linters and tests
```

## Usage

### Command-Line Interface (CLI)
You can use the CLI to quickly analyze a graph and display its metrics:
```bash
python cli.py
```

### Running Experiments
To run specific experiments on your datasets:
```bash
# Run basic analysis
python experiments/run_analysis.py

# Run landmark experiments
python experiments/run_landmarks.py

# Run robustness simulation
python experiments/run_robustness.py
```

### Testing and Linting
Run all unit tests and checks:
```bash
./check_all.sh
```

### License
MIT 