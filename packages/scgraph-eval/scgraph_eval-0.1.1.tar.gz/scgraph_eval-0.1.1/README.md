# scgraph-eval

A tool for evaluating single-cell embeddings using graph-based relationships. This package helps analyze the consistency of cell type relationships across different batches in single-cell data.

## Features

- Calculate trimmed means for cell type centroids
- Compute pairwise distances between cell types
- Process multiple batches to assess embedding consistency
- Support for both PCA and custom embeddings
- Built-in handling for highly variable genes (HVG)

## Installation

You can install the package via pip:

```bash
pip install scgraph-eval
```

## Usage

### Python API

```python
from scgraph import scGraph

# Initialize the graph analyzer
graph = scGraph(
    adata_path="path/to/your/data.h5ad",   # Path to AnnData object
    batch_key="batch",                     # Column name for batch information
    label_key="cell_type",                 # Column name for cell type labels
    trim_rate=0.05,                        # Trim rate for robust mean calculation
    thres_batch=100,                       # Minimum number of cells per batch
    thres_celltype=10                      # Minimum number of cells per cell type
)

# Run the analysis
results = graph.main()

# Save results
results.to_csv("embedding_evaluation_results.csv")
```

### Command Line Interface

```bash
scgraph-eval --adata_path path/to/data.h5ad \
             --batch_key batch \
             --label_key cell_type \
             --trim_rate 0.05 \
             --thres_batch 100 \
             --thres_celltype 10 \
             --savename results
```

## Output

The package outputs comparison metrics between different embeddings:
- Rank-PCA: Spearman correlation with PCA-based relationships
- Corr-PCA: Pearson correlation with PCA-based relationships
- Corr-Weighted: Weighted correlation considering distance-based importance

## Requirements

- numpy
- pandas
- scanpy
- tqdm
- scipy

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this package in your research, please cite:
[Citation information to be added]

## Contact

For questions and feedback:
- Hanchen Wang
- Email: hanchen.wang.sc@gmail.com