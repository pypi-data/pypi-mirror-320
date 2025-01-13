# InnoML

## Overview

This package is a custom-built implementation of several foundational machine learning algorithms developed entirely from scratch, without reliance on libraries like scikit-learn. It provides an educational and practical resource for understanding and applying machine learning techniques at a granular level.

### Implemented Algorithms
1. **Linear Regression**
2. **Multiple Linear Regression**
3. **Logistic Regression**
4. **K-Nearest Neighbors (KNN)**
5. **Decision Tree**
6. **Random Forest**

---

## Features

- **Custom Implementation**: All algorithms are implemented from first principles, ensuring transparency and understanding of the underlying mechanics.
- **Versatile**: Supports both regression and classification tasks.
- **No External Dependencies**: Built without using pre-existing ML libraries, providing full control over model behavior and implementation details.
- **Educational Resource**: Ideal for those who want to learn the inner workings of machine learning algorithms.

---

## Installation

Clone the repository to your local machine:

```bash
git clone https://github.com/SriramR123/InnoML.git
cd InnoML
```

No additional libraries are required beyond Python's standard libraries.

---

## Usage

### Example: Linear Regression

```python
from InnoML.linear_regression import LinearRegression

# Example data
X = [[1], [2], [3], [4], [5]]
y = [2, 4, 6, 8, 10]

# Initialize and fit the model
model = LinearRegression()
model.fit(X, y)

# Make predictions
predictions = model.predict([[6], [7]])
print(predictions)  # Output: [12, 14]
```

### Available Modules
Each algorithm is implemented in a separate module for clarity and modularity:

- `linear_regression.py`: Implementation of simple and multiple linear regression.
- `logistic_regression.py`: Logistic regression for binary classification.
- `knn.py`: K-Nearest Neighbors for classification and regression.
- `decision_tree.py`: Decision tree for classification and regression.
- `random_forest.py`: Ensemble learning using Random Forest.

---

## Contributing

Contributions are welcome! If you find a bug or have a feature request, feel free to open an issue or submit a pull request.

### Steps to Contribute:
1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`.
3. Commit your changes: `git commit -m 'Add feature name'`.
4. Push to the branch: `git push origin feature-name`.
5. Open a pull request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contact

For questions or feedback, feel free to reach out:

- **Email**: sriramachandranram@gmail.com
- **GitHub**: [SriramR123](https://github.com/SriramR123)

---

## Acknowledgements

This project is inspired by the desire to understand and implement machine learning algorithms at a foundational level. Special thanks to the open-source community for their resources and support.
