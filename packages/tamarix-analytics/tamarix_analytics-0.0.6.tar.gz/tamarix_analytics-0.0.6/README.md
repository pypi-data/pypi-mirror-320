# Tamarix Analytics

A Python package for row matching and F1 score calculations using the Hungarian algorithm.

## Installation

```bash
pip install tamarix-analytics
```

## Usage

```python
from tamarix_analytics import match_rows, f1_score_unordered, f1_score_ordered, get_row_score
```

## Methods

### 1. `def match_rows(tentative_data: list[BaseModel], ground_truth: list[BaseModel]) -> Sequence[Tuple[int, int]]`

Finds the optimal assignment of rows between two objects using the Hungarian algorithm.
The optimal assignment is invariant to the order of the objects in the lists.
This allows to make a comparison between tables even if the order/number of rows is different.

**Input**:
- `tentative_data: list[BaseModel]` - list of arbitrary objects for comparison
- `ground_truth: list[BaseModel]` - ground truth list of objects to match `tentative_data` against.

**Output**:
A list of 2-tuples where the first item is the index of an object in the ground truth list and the second item is the index of an object in the tentative list.

### 2. `def f1_score_unordered(tentative_data: list[BaseModel], ground_truth: list[BaseModel]) -> float`

Calculates the F1 score between two list of arbitrary objects, without penalizing the wrong order of objects in the list. Internally uses the `match_rows` function to find the best mapping between the rows.

**Input**:
- `tentative_data: list[BaseModel]` - list of arbitrary objects for comparison
- `ground_truth: list[BaseModel]` - ground truth list of objects.

**Output**:
F1 score as float

### 3. `def f1_score_ordered(tentative_data: list[BaseModel], ground_truth: list[BaseModel]) -> float`

Caluclates the F1 score where values are checked with consideration to the structure and order of the tables being compared.

**Input**:
- `tentative_data: list[BaseModel]` - list of arbitrary objects for comparison
- `ground_truth: list[BaseModel]` - ground truth list of objects.

**Output**:
F1 score as float

### 4. `def row_score(tentative_data: list[BaseModel], ground_truth: list[BaseModel]) -> float`

The ratio between the number of items in the `ground_truth` list over the number of items in `tentative_data`.

**Input**:
- `tentative_data: list[BaseModel]` - list of arbitrary objects for comparison
- `ground_truth: list[BaseModel]` - ground truth list of objects.

**Output**:
Row score ratio as float
