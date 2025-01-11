# Information Retrieval Evaluation with numba

[![image](https://img.shields.io/pypi/v/ir_eval_numba.svg)](https://pypi.python.org/pypi/ir_eval_numba)
[![Actions status](https://github.com/plurch/ir_eval_numba/actions/workflows/ci-tests.yml/badge.svg)](https://github.com/plurch/ir_eval_numba/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/plurch/ir_eval_numba/blob/main/LICENSE)

This project provides simple and tested [numba](https://github.com/numba/numba) implementations of popular information retrieval metrics. The source code is clear and easy to understand. All functions have pydoc help strings.

The metrics can be used to determine the quality of rankings that are returned by a retrieval or recommender system.

## Alternative library

If you don't need numba and want a library that is written in pure python, check out [plurch/ir_evaluation](https://github.com/plurch/ir_evaluation)

## Installation

Requirements:
Python 3.11 or 3.12
numba>=0.60.0

`ir_eval_numba` can be installed from pypi with:

```
pip install ir_eval_numba
```

## Usage

Metric functions will generally accept the following arguments:

`actual` (npt.NDArray[IntType]): An array of integer ground truth relevant items.

`predicted` (npt.NDArray[IntType]): An array of integer predicted items, ordered by relevance.

`k` (int): The number of top predictions to consider.

Functions will return a `float` value as the computed metric value.

## Unit tests

Unit tests with easy to follow scenarios and sample data are included.

### Run unit tests
```
uv run pytest
```

## Metrics
- [Recall](#recall)
- [Precision](#precision)
- [Average Precision (AP)](#average-precision-ap)
- [Mean Average Precision (MAP)](#mean-average-precision-map)
- [Normalized Discounted Cumulative Gain (nDCG)](#normalized-discounted-cumulative-gain-ndcg)
- [Reciprocal Rank (RR)](#reciprocal-rank-rr)
- [Mean Reciprocal Rank (MRR)](#mean-reciprocal-rank-mrr)


### Recall

Recall is defined as the ratio of the total number of relevant items retrieved within the top-k predictions to the total number of relevant items in the entire database.

Usage scenario: Prioritize returning all relevant items from database. Early retrieval stages where many candidates are returned should focus on this metric.

```
from ir_eval_numba.metrics import recall
```

### Precision

Precision is defined as the ratio of the total number of relevant items retrieved within the top-k predictions to the total number of returned items (k).

Usage scenario: Minimize false positives in predictions. Later ranking stages should focus on this metric.

```
from ir_eval_numba.metrics import precision
```

### Average Precision (AP)

Average Precision is calculated as the mean of precision values at  each rank where a relevant item is retrieved within the top `k` predictions.

Usage scenario: Evaluates how well relevant items are ranked within the top-k returned list.

```
from ir_eval_numba.metrics import average_precision
```

### Mean Average Precision (MAP)

MAP is the mean of the Average Precision (AP - see above) scores computed for multiple queries.

Usage scenario: Reflects overall performance of AP for multiple queries. A good holistic metric that balances the tradeoff between recall and precision.

```
from ir_eval_numba.metrics import mean_average_precision
```

### Normalized Discounted Cumulative Gain (nDCG)

nDCG evaluates the quality of a predicted ranking by comparing it to an ideal ranking (i.e., perfect ordering of relevant items). It accounts for the position of relevant items in the ranking, giving higher weight to items appearing earlier.

Usage scenario: Prioritize returning relevant items higher in the returned top-k list. A good holistic metric. 

```
from ir_eval_numba.metrics import ndcg
```

### Reciprocal Rank (RR)

Reciprocal Rank (RR) assigns a score based on the reciprocal of the rank at which the first relevant item is found.

Usage scenario: Useful when the topmost recommendation holds siginificant value. Use this when users are presented with one or very few returned results.

```
from ir_eval_numba.metrics import reciprocal_rank
```

### Mean Reciprocal Rank (MRR)

MRR calculates the mean of the Reciprocal Rank (RR) scores for a set of queries.

Usage scenario: Reflects overall performance of RR for multiple queries.

```
from ir_eval_numba.metrics import mean_reciprocal_rank
```

## Online Resources

[Pinecone - Evaluation Measures in Information Retrieval
](https://www.pinecone.io/learn/offline-evaluation/)

[Spot Intelligence - Mean Average Precision](https://spotintelligence.com/2023/09/07/mean-average-precision/)

[Spot Intelligence - Mean Reciprocal Rank](https://spotintelligence.com/2024/08/02/mean-reciprocal-rank-mrr/)

[google-research/ials](https://github.com/google-research/google-research/blob/943fffe2522da9e58667fb129eda84bd6c088035/ials/ncf_benchmarks/ials.py#L83)
