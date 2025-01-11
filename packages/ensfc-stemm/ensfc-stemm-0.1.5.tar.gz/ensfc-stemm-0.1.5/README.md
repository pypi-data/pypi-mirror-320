# ENSFC STEMM Python Package
## Table of Contents

- [ENSFC STEMM Python Package](#ensfc-stemm-python-package)
    - [Installation](#installation)
    - [Usage](#usage)
        - [Functions](#functions)
            - [`calculate_mean`](#calculate_mean)
            - [`solve_quadratic`](#solve_quadratic)
            - [`nth_term`](#nth_term)
        - [Classes](#classes)
            - [`Student`](#student)
            - [`Experiment`](#experiment)
    - [Contributing](#contributing)
    - [License](#license)
    - [Contact](#contact)

Welcome to the ENSFC STEMM Python Package! This package is designed to provide tools and utilities for students and professionals in the fields of Science, Technology, Engineering, Mathematics, and Medicine.

## Installation

You can install the package using pip:

```bash
pip install ensfc-stemm
```

## Usage

Below are some examples of how to use the functions and classes provided by this package.

### Functions

#### `calculate_mean`

Calculates the mean of a list of numbers.

```python
from ensfc_stemm import calculate_mean

numbers = [1, 2, 3, 4, 5]
mean = calculate_mean(numbers)
print(f"The mean is: {mean}")
```

#### `solve_quadratic`

Solves a quadratic equation of the form ax^2 + bx + c = 0.

```python
from ensfc_stemm import solve_quadratic

a, b, c = 1, -3, 2
roots = solve_quadratic(a, b, c)
print(f"The roots are: {roots}")
```

#### `nth_term

Finds the nth term formula for a given sequence, provided the function is given enough terms to compute a formula

```python
from ensfc_stemm import nth_term

terms1 = [1, 4, 9, 16, 25]
print(nth_term(*terms1)) # Output: n^2

print(nth_term(50, 325, 1168, 3059, 6622, 12625)) # Output: 6n^4 + 10n^3 + 14n^2 + 3n + 7
```

### Classes

#### `Student`

Represents a student with a name and a list of grades.

```python
from ensfc_stemm import Student

student = Student(name="John Doe", grades=[90, 85, 92])
print(f"Student Name: {student.name}")
print(f"Average Grade: {student.average_grade()}")
```

#### `Experiment`

Represents a scientific experiment with a name and a list of results.

```python
from ensfc_stemm import Experiment

experiment = Experiment(name="Physics Experiment", results=[9.8, 9.7, 9.9])
print(f"Experiment Name: {experiment.name}")
print(f"Average Result: {experiment.average_result()}")
```

## Contributing

We welcome contributions! Please read our [contributing guidelines](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For any questions or suggestions, please contact me at concise_sparsity287626@outlook.com.