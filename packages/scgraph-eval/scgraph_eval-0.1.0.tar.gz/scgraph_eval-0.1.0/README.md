# scGraph (minimal)

A tool for analyzing single-cell data using graph-based approaches.

## Installation

```bash
pip install scgraph
```

## Usage

```python
from scgraph import scGraph

# Initialize the graph
graph = scGraph(
    adata_path="path/to/your/data.h5ad",
    batch_key="batch",
    label_key="cell_type",
    trim_rate=0.05
)

# Run analysis
results = graph.main()
print(results)
```

## Command Line Interface

```bash
scgraph --adata_path path/to/data.h5ad --batch_key batch --label_key cell_type
```

## Requirements

- numpy
- pandas
- scanpy
- tqdm

## License

This project is licensed under the MIT License - see the LICENSE file for details.
