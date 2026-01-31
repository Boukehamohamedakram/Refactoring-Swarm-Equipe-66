import json
import math

class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, a: float, b: float) -> float:
        result = a + b
        self.history.append(('add', a, b, result))
        return result
    
    def sub(self, a: float, b: float) -> float:
        result = a - b
        self.history.append(('sub', a, b, result))  # FIX: Added history tracking
        return result
    
    def mul(self, a: float, b: float) -> float:
        result = a * b
        self.history.append(('mul', a, b, result))
        return result
    
    def div(self, a: float, b: float) -> float:
        if b == 0:  # FIX: Added division by zero check
            raise ValueError("Cannot divide by zero")
        result = a / b
        self.history.append(('div', a, b, result))
        return result
    
    def pow(self, a: float, b: float) -> float:
        try:
            result = math.pow(a, b)
        except (ValueError, OverflowError) as e:  # FIX: Handle math errors
            raise ValueError(f"Power calculation error: {e}")
        self.history.append(('pow', a, b, result))  # FIX: Added history tracking
        return result
    
    def avg(self, nums: list) -> float:
        if not nums:  # FIX: Check for empty list
            raise ValueError("Cannot calculate average of empty list")
        return sum(nums) / len(nums)
    
    def stats(self):
        return {
            'total_ops': len(self.history),
            'last_op': self.history[-1] if self.history else None
        }


class DataProcessor:
    def __init__(self, calculator=None):
        self.calc = calculator or Calculator()  # FIX: Allow passing existing calculator
    
    def process(self, data):
        if not data:  # FIX: Check for empty data
            return []
        
        results = []
        
        for item in data:
            # FIX: Validate required fields exist
            if not all(key in item for key in ['x', 'y', 'op']):
                raise ValueError("Missing required fields in data item")
            
            a = item['x']
            b = item['y']
            op = item['op']
            
            try:
                # FIX: Validate input types
                a = float(a)
                b = float(b)
                
                if op == 'add':
                    result = self.calc.add(a, b)
                elif op == 'sub':
                    result = self.calc.sub(a, b)
                elif op == 'mul':
                    result = self.calc.mul(a, b)
                elif op == 'div':
                    result = self.calc.div(a, b)
                elif op == 'pow':
                    result = self.calc.pow(a, b)
                else:
                    raise ValueError(f"Unknown operation: {op}")  # FIX: Better error handling
                
                item['result'] = result
                results.append(item)
                
            except Exception as e:
                # FIX: Handle errors and continue processing other items
                item['result'] = None
                item['error'] = str(e)
                results.append(item)
        
        return results


def load_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:  # FIX: Added encoding
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filename}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON in file: {filename}")


def save_results(data, filename):
    # FIX: Handle NaN/Inf values for JSON serialization
    def json_serializer(obj):
        if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
            return str(obj)
        raise TypeError(f"Type {type(obj)} not serializable")
    
    with open(filename, 'w', encoding='utf-8') as f:  # FIX: Added encoding
        json.dump(data, f, indent=2, default=json_serializer)


def analyze_dataset(dataset):
    if not dataset:  # FIX: Check for empty dataset
        return {'error': 'Empty dataset'}
    
    calc = Calculator()
    values = []
    
    for item in dataset:
        # FIX: Check if result exists and is valid
        if 'result' in item and item['result'] is not None:
            try:
                value = float(item['result'])
                if not math.isnan(value) and not math.isinf(value):
                    values.append(value)
            except (ValueError, TypeError):
                continue  # Skip invalid values
    
    if not values:  # FIX: Check if we have any valid values
        return {'error': 'No valid results to analyze'}
    
    try:
        return {
            'mean': calc.avg(values),
            'min': min(values),
            'max': max(values),
            'total': sum(values),
            'count': len(values)  # FIX: Added count for clarity
        }
    except Exception as e:
        return {'error': f'Analysis failed: {str(e)}'}


# Usage example with fixes
def main():
    # FIX: Use a single calculator instance to preserve history
    calc = Calculator()
    processor = DataProcessor(calc)
    
    data = [
        {'x': 10, 'y': 5, 'op': 'add'},
        {'x': 10, 'y': 0, 'op': 'div'},
        {'x': 10, 'y': 2, 'op': 'mul'},
        {'x': 10, 'y': -5, 'op': 'sub'},
        {'x': 2, 'y': 3, 'op': 'pow'},
        {'x': -2, 'y': 0.5, 'op': 'pow'},  # Test case for complex result
        {'x': 10, 'y': 5, 'op': 'unknown'}
    ]
    
    try:
        results = processor.process(data)
        stats = analyze_dataset(results)
        print("Analysis results:", stats)
        
        # Save results with proper error handling
        try:
            save_results(results, 'output.json')
            print("Results saved to output.json")
        except Exception as e:
            print(f"Failed to save results: {e}")
        
        # FIX: Use the same calculator instance for stats
        print("Calculator stats:", calc.stats())
        
    except Exception as e:
        print(f"Error during processing: {e}")


if __name__ == "__main__":
    main()