# Extended Dictionary Python Package

This Python package that defines the `Table` class, which represents a table with content, read-only indices, and size constraints. It provides various methods and properties to manage a table with content, enforce size limits, and support operations such as adding, removing, and retrieving items.

## Features

- **Table Class**: A class to represent and manage tables with content and size constraints.
- **Size Constraints**: Supports properties for setting minimum and maximum size limits.
- **Read-Only Indices**: Manages indices in a read-only manner.

## Installation

To install this package, simply use `pip`:

```bash
pip install extdict
```

## Example Usage

```Python
from extdict import Table

new_table = Table({0: 2}) + Table({1: 2, 2: 3})
new_table.minimum_size = 3

print(new_table) # {0: 2, 1: 2, 2: 3}
print(new_table.find_index(2)) # (0, 1)

try:
    print(new_table - Table({2: 3}))
except KeyError: # Minimum size has been reached
    new_table.minimum_size = 2
    print(new_table - Table({2: 3})) # {0: 2, 1: 2}

new_table.read_only_indices = {0}
new_table[1] = 0

try:
    new_table[0] = False
except KeyError: # Index 0 is read-only
    new_table.read_only_indices.remove(0)
    new_table[0] = True

print(new_table) # {0: True, 1: 0, 2: 3}
```