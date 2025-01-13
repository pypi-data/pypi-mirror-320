# Dolphin Models

`dolphin_models` is a Python package that provides implementations of popular machine learning models, including:

- Linear Regression
- Logistic Regression
- Multivariate Regression
- Decision Tree
- Random Forest
- K-Nearest Neighbors (KNN)

Each model includes two core methods:

- `scr_fit()`: Used to train the model on the given data.
- `scr_predict()`: Used to make predictions using the trained model.

## Installation

To install the `dolphin_models` package, use the following command:

```bash
pip install dolphin_models
```

---

## Usage

### Importing Models

You can import specific models from the package as follows:

```python
from dolphin_models import LinearRegression, LogisticRegression, MultivariateRegression
from dolphin_models import DecisionTree, RandomForest, KNN
```

### Example Usage

#### 1. Linear Regression

```python
from dolphin_models import LinearRegression

# Initialize the model
model = LinearRegression()

# Train the model
X_train = [[1], [2], [3], [4], [5]]
y_train = [2, 4, 6, 8, 10]
model.scr_fit(X_train, y_train)

# Make predictions
X_test = [[6], [7]]
predictions = model.scr_predict(X_test)
print("Linear Regression Predictions:", predictions)
```

#### 2. Logistic Regression

```python
from dolphin_models import LogisticRegression

# Initialize the model
model = LogisticRegression()

# Train the model
X_train = [[1], [2], [3], [4], [5]]
y_train = [0, 0, 0, 1, 1]
model.scr_fit(X_train, y_train)

# Make predictions
X_test = [[3], [6]]
predictions = model.scr_predict(X_test)
print("Logistic Regression Predictions:", predictions)
```

#### 3. Multivariate Regression

```python
from dolphin_models import MultivariateRegression

# Initialize the model
model = MultivariateRegression()

# Train the model
X_train = [[1, 2], [2, 3], [3, 4]]
y_train = [3, 5, 7]
model.scr_fit(X_train, y_train)

# Make predictions
X_test = [[4, 5], [6, 7]]
predictions = model.scr_predict(X_test)
print("Multivariate Regression Predictions:", predictions)
```

#### 4. Decision Tree

```python
from dolphin_models import DecisionTree

# Initialize the model
model = DecisionTree()

# Train the model
X_train = [[1], [2], [3], [4], [5]]
y_train = [0, 1, 0, 1, 0]
model.scr_fit(X_train, y_train)

# Make predictions
X_test = [[3], [6]]
predictions = model.scr_predict(X_test)
print("Decision Tree Predictions:", predictions)
```

#### 5. Random Forest

```python
from dolphin_models import RandomForest

# Initialize the model
model = RandomForest()

# Train the model
X_train = [[1], [2], [3], [4], [5]]
y_train = [1, 2, 1, 2, 1]
model.scr_fit(X_train, y_train)

# Make predictions
X_test = [[2], [5]]
predictions = model.scr_predict(X_test)
print("Random Forest Predictions:", predictions)
```

#### 6. K-Nearest Neighbors (KNN)

```python
from dolphin_models import KNN

# Initialize the model
model = KNN()

# Train the model
X_train = [[1], [2], [3], [4], [5]]
y_train = [1, 0, 1, 0, 1]
model.scr_fit(X_train, y_train)

# Make predictions
X_test = [[3], [4]]
predictions = model.scr_predict(X_test)
print("KNN Predictions:", predictions)
```

---

## Contributing

Contributions are welcome! If you'd like to improve the package or add new features, feel free to fork the repository and submit a pull request.

---

## License

This package is licensed under the MIT License. See the `LICENSE` file for details.

