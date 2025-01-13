# Neutrosophic Calculator

A Python library for performing operations on neutrosophic sets. This library supports basic arithmetic and algebraic operations, scalar multiplication, and logical operations on neutrosophic sets.

## Installation

```bash
pip install neutrosophic
# netrosophic
```

## Usage Instructions

### Creating Neutrosophic Sets

You can create a neutrosophic set using truth, indeterminacy, and falsity values.

```python
from netrosophic import NetrosophicSet

# Create a neutrosophic set
ns = NetrosophicSet(0.5, 0.3, 0.2)
print("Neutrosophic Set:", ns)
```

### Arithmetic Operations on Neutrosophic Sets

You can perform basic arithmetic operations such as addition, subtraction, multiplication, and division on neutrosophic sets.

```python
from netrosophic import NetrosophicSet

ns1 = NetrosophicSet(0.5, 0.3, 0.2)
ns2 = NetrosophicSet(0.4, 0.2, 0.1)

# Addition
result_add = ns1 + ns2
print("Addition:", result_add)

# Subtraction
result_sub = ns1 - ns2
print("Subtraction:", result_sub)

# Multiplication
result_mul = ns1 * ns2
print("Multiplication:", result_mul)

# Division by a scalar
result_div = ns1 / 0.5
print("Division:", result_div)
```

### Scalar Multiplication

You can multiply a neutrosophic set by a scalar.

```python
scalar = 2.0
result_scalar_mul = ns1.scalar_mul(scalar)
print("Scalar Multiplication:", result_scalar_mul)
```

### Logical Operations

Logical operations such as conjunction, disjunction, and negation can be performed using the `NetrosophicLogic` class.

```python
from netrosophic import NetrosophicLogic

logic = NetrosophicLogic()
result_conj = logic.conjunction(ns1, ns2)
print("Conjunction:", result_conj)

result_disj = logic.disjunction(ns1, ns2)
print("Disjunction:", result_disj)

result_neg = logic.negation(ns1)
print("Negation:", result_neg)
```

### Analyzing a Neutrosophic Set

You can analyze a neutrosophic set to get a detailed breakdown of its truth, indeterminacy, falsity, and overall certainty.

```python
from netrosophic import NetrosophicAnalyzer

analyzer = NetrosophicAnalyzer()
analysis = analyzer.analyze(ns1)
print("Analysis:\n", analysis)
```

### Creating Neutrosophic Sets from Tuples

You can create a neutrosophic set from a tuple and also convert a neutrosophic set back to a tuple.

```python
# Creating from tuple
ns3 = NetrosophicSet.from_tuple((0.6, 0.5, 0.4))
print("From tuple:", ns3)

# Converting to tuple
print("To tuple:", ns1.to_tuple())
```

## Features

- **Basic Arithmetic Operations**: Add, subtract, multiply, and divide neutrosophic sets.
- **Scalar Multiplication**: Multiply a neutrosophic set by a scalar.
- **Logical Operations**: Perform conjunction, disjunction, and negation on neutrosophic sets.
- **Analysis**: Analyze a neutrosophic set to understand its components.
- **Tuple Conversion**: Create neutrosophic sets from tuples and convert them back to tuples.

## License

This project is licensed under the MIT License.

