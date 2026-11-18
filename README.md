<div align="center">

# COMP7104 Advanced Database Systems — Assignments

**Analytical SQL. Query optimisation. Concurrency control.**

A collection of three practical assignments completed for **HKU COMP7104 / DASC7104**, covering DuckDB, PostgreSQL, and database execution internals.

[![HKU COMP7104](https://img.shields.io/badge/HKU-COMP7104-6E56CF)](https://github.com/junjiacaohku-ai/COMP7014-Assignment)
[![Assignments](https://img.shields.io/badge/Assignments-3-0072B2)](#assignments)
[![DuckDB](https://img.shields.io/badge/DuckDB-Analytical_SQL-FFF000?logo=duckdb&logoColor=black)](https://duckdb.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebooks-F37626?logo=jupyter&logoColor=white)](https://jupyter.org/)
[![GitHub stars](https://img.shields.io/github/stars/junjiacaohku-ai/COMP7014-Assignment?style=social)](https://github.com/junjiacaohku-ai/COMP7014-Assignment/stargazers)

[Overview](#overview) · [Assignments](#assignments) · [Repository Structure](#repository-structure) · [Reproduction Notes](#reproduction-notes)

</div>

---

<a id="overview"></a>
## 1. Overview

This repository archives my completed notebooks, reports, assignment handouts, and supporting data for three individual practical assignments in **Advanced Database Systems**.

The coursework moves from writing analytical SQL to understanding how database engines execute queries and manage concurrent transactions. Each assignment includes both implementation and written analysis, with query results, execution plans, measurements, and explanations preserved in the submitted files.

**Course:** COMP7104 / DASC7104, 2026–27 Semester 1, Subclass B  
**Instructor:** Prof. Bogdan Cautis  
**Author:** Cao Junjia

<a id="assignments"></a>
## 2. Assignments

| Assignment | Topic | Main work | Submission |
|---|---|---|---|
| **PA1** | Analytical SQL with DuckDB | CTEs, window functions, conditional aggregation, `ROLLUP`, anti-joins, query plans, cardinality estimates, and performance measurements | [Notebook](Assignment1/pa1-data/pa1_3036790730.ipynb) · [PDF](Assignment1/pa1-data/pa1_3036790730.pdf) |
| **PA2** | Query optimisation and execution | PostgreSQL and DuckDB plan analysis, join algorithms, memory and hash batches, threading, optimizer experiments, and column statistics | [Notebook](Assignment2/pa2_3036790730/pa2_3036790730.ipynb) · [PDF](Assignment2/pa2_3036790730/pa2_3036790730.pdf) |
| **PA3** | Transactions and concurrency control | Isolation, atomicity, row locks, deadlocks, explicit locking, phantom reads, write skew, serializability, and optimistic concurrency in DuckDB | [Report](Assignment3/PA3_3036790730.pdf) · [DuckDB notebook](Assignment3/PA3_Lesson12.ipynb) |

### PA1 — Analytical SQL with DuckDB

- Analysis of a movie–director dataset using modern analytical SQL.
- Larger-scale experiments on synthetic `actor`, `movie`, and `casting` tables.
- Comparison of estimated and actual cardinalities through `EXPLAIN` and `EXPLAIN ANALYZE`.
- Measured investigation of database performance and execution behavior.

### PA2 — Query Optimisation and Execution

- Inspection of join order, build sides, predicate pushdown, and operator costs.
- Experiments with join algorithms, `work_mem`, DuckDB threads, and the optimizer.
- Analysis of distinct-value estimates and extended statistics for dependent columns.
- Median-of-three timing methodology after warm-up runs.

### PA3 — Transactions and Concurrency Control

- Controlled multi-session experiments in PostgreSQL.
- Observation of blocking, lost updates, deadlocks, phantom records, and write skew.
- Comparison of `READ COMMITTED`, `REPEATABLE READ`, and `SERIALIZABLE` behavior.
- DuckDB transaction conflicts and a retry-based booking function.

## 3. Repository Structure

```text
COMP7014-Assignment/
├── Assignment1/
│   ├── COMP7104-DASC7104-B-PA1-DuckDB-2026.pdf
│   └── pa1-data/
│       ├── pa1_3036790730.ipynb       # Completed PA1 notebook
│       ├── pa1_3036790730.pdf         # Submitted PA1 report
│       ├── pa1_starter.ipynb          # Original starter notebook
│       ├── make_dataset.py            # Synthetic data generator
│       ├── pa1.duckdb                 # DuckDB database (Git LFS)
│       └── pa1data/                   # CSV and Parquet data (Git LFS)
├── Assignment2/
│   ├── COMP7104-DASC7104-PA2-Optimisation-2026.pdf
│   ├── pa2_3036790730/
│   │   ├── pa2_3036790730.ipynb       # Completed PA2 notebook
│   │   └── pa2_3036790730.pdf         # Submitted PA2 report
│   └── pa2_starter.ipynb              # Original starter notebook
├── Assignment3/
│   ├── PA3_3036790730.pdf             # Submitted PA3 report
│   ├── PA3_3036790730.docx            # Editable report
│   ├── PA3_Lesson12.ipynb             # DuckDB concurrency experiments
│   └── PA3_<University Number>.pdf    # Original assignment handout
└── README.md
```

<a id="reproduction-notes"></a>
## 4. Reproduction Notes

### Requirements

- Python with Jupyter Notebook or JupyterLab
- DuckDB, pandas, and psycopg
- PostgreSQL 17 for the server-based experiments
- The COMP7104 course Docker environment for the original database setup
- Git LFS for the large PA1 database and data files

### Clone with large files

```bash
git lfs install
git clone https://github.com/junjiacaohku-ai/COMP7014-Assignment.git
cd COMP7014-Assignment
git lfs pull
```

Open the completed notebooks with the course Python environment. PA2 reuses the scale-10 `pa1data` tables and `make_dataset.py` associated with PA1. Timing results are machine-dependent; the notebooks record the environment and measurements used for the original submissions.

The original course setup archive is not duplicated in this repository. Credentials should be supplied through local environment configuration and never committed.

## 5. Notes

- These files are individual coursework submissions and are shared as a learning portfolio.
- Assignment handouts and starter materials remain subject to the course's original terms.
- Generative-AI declarations are included in the submitted assignments where required.
- Please do not reuse these answers as your own coursework.

---

<div align="center">

**COMP7104 — From SQL queries to the systems that execute them.**

HKU · Advanced Database Systems · DuckDB + PostgreSQL + Jupyter

</div>
