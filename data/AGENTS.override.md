# Data

Based on the [Cookiecutter Data Science directory structure](https://cookiecutter-data-science.drivendata.org/#directory-structure):

```text
data/
├── external/       # Data from third party sources; reimport if lost.
│   └── inventory/  # Customer, team, or uploaded inventory workbooks.
├── interim/        # Intermediate data that has been transformed.
├── processed/      # The final, canonical data sets for modeling.
│   └── tables/     # Project-generated summaries; reproducible from external inputs.
└── raw/            # The original, immutable data dump.
```

- Treat `external/` as imported source data, not app output.
- Write recreatable project output under `processed/`.
