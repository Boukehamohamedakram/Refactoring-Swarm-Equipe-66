import json, math

class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        result = a + b
        self.history.append(('add', a, b, result))
        return result
    
    def sub(self, a, b):
        return a - b
    
    def mul(self, a, b):
        self.history.append(('mul', a, b, a * b))
        return a * b
    
    def div(self, a, b):
        self.history.append(('div', a, b, a / b))
        return a / b
    
    def pow(self, a, b):
        return math.pow(a, b)
    
    def avg(self, nums):
        return sum(nums) / len(nums)
    
    def stats(self):
        return {
            'total_ops': len(self.history),
            'last_op': self.history[-1] if self.history else None
        }

class DataProcessor:
    def process(self, data):
        calc = Calculator()
        results = []
        
        for item in data:
            a = item['x']
            b = item['y']
            op = item['op']
            
            if op == 'add':
                result = calc.add(a, b)
            elif op == 'sub':
                result = calc.sub(a, b)
            elif op == 'mul':
                result = calc.mul(a, b)
            elif op == 'div':
                result = calc.div(a, b)
            elif op == 'pow':
                result = calc.pow(a, b)
            else:
                result = None
            
            item['result'] = result
            results.append(item)
        
        return results

def load_data(filename):
    with open(filename) as f:
        return json.load(f)

def save_results(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)

def analyze_dataset(dataset):
    calc = Calculator()
    
    values = []
    for item in dataset:
        if 'result' in item:
            values.append(item['result'])
    
    return {
        'mean': calc.avg(values),
        'min': min(values),
        'max': max(values),
        'total': sum(values)
    }

# Usage
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