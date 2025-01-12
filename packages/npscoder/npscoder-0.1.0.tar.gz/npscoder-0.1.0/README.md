# Non-Parametric Supervised Coder

This project demonstrates a method for encoding input variables using the target variable without making assumptions about the distribution of either. The target variable can be binary, ordinal, or continuous. The encoding is achieved by ranking variables based on their ability to explain a business question robustly. This is inspired by the Kxen.ConsistentCoder library from SAP.

### Encoding Principle

The encoding process involves computing statistics for each category of a nominal variable. For example, for a nominal variable 'Color' with categories 'Red', 'Blue', and 'Green', the average target value for each category is calculated:

| Category | Target Average |
|----------|----------------|
| Red      | .75           |
| Green    | .35           |
| Blue     | .50           |

Then, the most simple coding scheme is to encode each category with its target average. But this technique has some drawbacks.

First you can lose some information when two categories have the same target average (or very close).
Second, for the target average to have any meaning at all, you must have enough cases for the category.
To counter the first issue, the coder codes the category not directly with the target average, but with the *uniform coding* of the category *ranked by the target mean*:

| Category | Frequency | Target Average | Rank | Coded Value |
|----------|-----------|----------------|------|-------------|
| Red      | 0.24       | .75           | 3    | -0.76    |
| Blue     | 0.61       | .50           | 2    | 0.09    |
| Green    | 0.15       | .35           | 1    | 0.85    |

Additionally, categories with insufficient representation are grouped into a miscellaneous class "Other".

### Installation

```bash
pip install npscoder
```

### Example

```python
import pandas as pd
from npscoder import Coder, Variable

# Load the description file
description_file = "desc.json"
coder = Coder(description_file)

data = pd.read_csv("data.csv")
# Set the data
coder.set_data(data)
# Build the statistics
coder.build()

# Encode the data
encoded_data = coder.encode()
# save the encoded data
encoded_data.to_csv("encoded_data.csv", index=False)
```

### Description file

The description file is a JSON file that defines the target and input variables. It is used to initialize the Coder class. See the adult census[description file](datasets/adult/desc.json) for an example.

### API Overview

#### `Coder` Class

The `Coder` class is responsible for managing the encoding process. It initializes with a description file that defines the target and input variables. The class provides methods to set data, build statistics, encode data, and display information about the variables.

- `Initialization`: Loads variable definitions from a JSON file.
- `set_data`: Prepares data for encoding by setting up statistics for each variable.
- `build`: Constructs statistics and encodes the target and input variables.
- `encode`: Encodes the data based on the prepared statistics.
- `display_description`: Shows a summary of the target and input variables.
- `display_ginis`: Displays Gini scores for the input variables.

#### `Variable` Class

The `Variable` class represents an individual variable with attributes like name, type, storage, and statistics. It provides methods to determine the variable type, build statistics, compute Gini scores, and encode the variable.

- `is_nominal`, `is_continuous`, `is_ordinal`: Check the type of the variable.
- `build_statistics`: Creates statistics for the variable, optionally using a target variable.
- `compute_gini`: Calculates the Gini score for the variable.
- `encode`: Encodes the variable using the prepared statistics.
- `plot_lorenz_curve, plot_encoding`: Visualizes the variable's encoding and distribution.

This project provides a robust framework for encoding variables in a non-parametric supervised manner, making it suitable for various machine learning tasks where the target variable's influence on input variables needs to be quantified and utilized effectively.


### TODOs

- [ ] handle unseen values during estimation
- [ ] use cross-validation to estimate the best encoding
- [ ] handle continuous target


