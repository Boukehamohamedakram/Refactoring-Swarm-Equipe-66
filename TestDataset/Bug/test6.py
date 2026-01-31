import json
import math

def _calculate(a, b, op):
    """Calculates the result of an operation on two numbers."""
    if op == 'add':
        return a + b
    elif op == 'sub':
        return a - b
    elif op == 'mul':
        return a * b
    elif op == 'div':
        if b == 0:
            return None  # Handle division by zero
        return a / b
    elif op == 'pow':
        return math.pow(a, b)
    else:
        return None


class Calculator:
    """Represents a calculator with basic arithmetic operations."""
    def __init__(self):
        """Initializes the calculator with an empty history."""
        self._history: list[tuple[str, float, float, float]] = []
    
    def _perform_operation(self, a, b, op):
        """Performs a single operation and records it in the history."""
        result = _calculate(a, b, op)
        if result is not None:
            self._history.append((op, a, b, result))
        return result
    
    def add(self, a, b):
        """Adds two numbers and records the operation in the history."""
        return self._perform_operation(a, b, 'add')
    
    def sub(self, a, b):
        """Subtracts two numbers and records the operation in the history."""
        return self._perform_operation(a, b, 'sub')
    
    def mul(self, a, b):
        """Multiplies two numbers and records the operation in the history."""
        return self._perform_operation(a, b, 'mul')
    
    def div(self, a, b):
        """Divides two numbers and records the operation in the history."""
        return self._perform_operation(a, b, 'div')
    
    def pow(self, a, b):
        """Calculates a to the power of b and records the operation in the history."""
        return self._perform_operation(a, b, 'pow')
    
    def avg(self, nums):
        """Calculates the average of a list of numbers."""
        if not nums:
            return None
        return sum(nums) / len(nums)
    
    def stats(self):
        """Returns statistics about the calculator's history."""
        if not self._history:
            return None
        return {
            'total_ops': len(self._history),
            'last_op': self._history[-1]
        }


class DataProcessor:
    """Processes a dataset of operations and their results."""
    def process(self, data):
        """Processes the input data, applying operations and storing results."""
        calc = Calculator()
        results = []
        
        for item in data:
            try:
                a = item['x']
                b = item['y']
                op = item['op']
                result = calc._calculate(a, b, op)
                item['result'] = result
                results.append(item)
            except KeyError as e:
                print(f"Missing key in data: {e}")  # Handle missing keys
                item['result'] = None
                results.append(item)
            except Exception as e:
                print(f"An error occurred: {e}")
                item['result'] = None
                results.append(item)
        
        return results



def load_data(filename):
    """Loads data from a JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)


def save_results(data, filename):
    """Saves the processed data to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def analyze_dataset(dataset):
    """Analyzes the dataset to calculate statistics."""
    calc = Calculator()
    values = []
    for item in dataset:
        if 'result' in item:
            values.append(item['result'])
    
    if not values:
        return None
    
    return {
        'mean': calc.avg(values),
        'min': min(values),
        'max': max(values),
        'total': sum(values)
    }


# Usage
if __name__ == '__main__':
    data = [
        {'x': 10, 'y': 5, 'op': 'add'},
        {'x': 10, 'y': 0, 'op': 'div'},
        {'x': 10, 'y': 2, 'op': 'mul'},
        {'x': 10, 'y': -5, 'op': 'sub'},
        {'x': 2, 'y': 3, 'op': 'pow'},
        {'x': 10, 'y': 5, 'op': 'unknown'}
    ]

    processor = DataProcessor()
    results = processor.process(data)
    stats = analyze_dataset(results)
    print(stats)
    save_results(results, 'output.json')
    print(Calculator().stats())
