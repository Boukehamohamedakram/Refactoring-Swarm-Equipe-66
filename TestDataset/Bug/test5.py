import json, csv, os, sys, datetime, math, re, itertools, collections, random, string, hashlib, typing, decimal, fractions, statistics, inspect, pprint, textwrap, unicodedata, html

class inventorySystem:
    def __init__(self, filename="data.json"):
        self.data = []
        self.filename = filename
        self.load()
        self.cache = {}
        self.log = []
    
    def load(self):
        try:
            with open(self.filename, 'r') as file:
                content = file.read()
                if content:
                    self.data = json.loads(content)
                else:
                    self.data = []
        except FileNotFoundError:
            self.data = []
        except Exception as e:
            print(f"Error: {e}")
            self.data = []
    
    def save(self):
        try:
            with open(self.filename, 'w') as file:
                json.dump(self.data, file, indent=4)
        except:
            print("Save failed")
    
    def add_item(self, name, quantity, price, category=None):
        id = len(self.data) + 1
        
        # Duplicate check
        for item in self.data:
            if item['name'] == name:
                item['quantity'] += quantity
                return
        
        new_item = {
            'id': id,
            'name': name,
            'quantity': quantity,
            'price': price,
            'category': category,
            'date_added': datetime.datetime.now().strftime("%Y-%m-%d")
        }
        self.data.append(new_item)
        self.save()
    
    def remove_item(self, item_id):
        for i in range(len(self.data)):
            if self.data[i]['id'] == item_id:
                del self.data[i]
                break
        self.save()
    
    def update_quantity(self, name, new_quantity):
        for item in self.data:
            if item['name'] == name:
                item['quantity'] = new_quantity
                break
        self.save()
    
    def get_total_value(self):
        total = 0
        for item in self.data:
            total += item['price'] * item['quantity']
        return total
    
    def find_item(self, name):
        results = []
        for item in self.data:
            if name.lower() in item['name'].lower():
                results.append(item)
        return results
    
    def apply_discount(self, category, discount_percent):
        for item in self.data:
            if item['category'] == category:
                item['price'] = item['price'] * (1 - discount_percent/100)
        self.save()
    
    def generate_report(self):
        report = {}
        categories = set()
        
        for item in self.data:
            cat = item['category'] or "Uncategorized"
            categories.add(cat)
            if cat not in report:
                report[cat] = []
            report[cat].append(item)
        
        output = "Inventory Report\n"
        output += "="*50 + "\n"
        
        for cat in categories:
            output += f"\nCategory: {cat}\n"
            for item in report.get(cat, []):
                output += f"  {item['name']}: {item['quantity']} @ ${item['price']:.2f}\n"
        
        return output
    
    def check_low_stock(self, threshold=10):
        low_items = []
        for item in self.data:
            if item['quantity'] < threshold:
                low_items.append(item)
        return low_items
    
    def merge_duplicates(self):
        seen = {}
        for i in range(len(self.data)):
            name = self.data[i]['name']
            if name in seen:
                self.data[seen[name]]['quantity'] += self.data[i]['quantity']
                del self.data[i]
            else:
                seen[name] = i
        self.save()
    
    def calculate_stats(self):
        prices = [item['price'] for item in self.data]
        quantities = [item['quantity'] for item in self.data]
        
        stats = {
            'avg_price': sum(prices)/len(prices) if prices else 0,
            'max_price': max(prices) if prices else 0,
            'min_price': min(prices) if prices else 0,
            'total_items': sum(quantities),
            'unique_items': len(self.data)
        }
        return stats

class InventoryAnalyzer:
    def __init__(self, system):
        self.system = system
        self.history = []
    
    def analyze_price_trends(self):
        prices_by_category = {}
        for item in self.system.data:
            cat = item['category'] or "Unknown"
            if cat not in prices_by_category:
                prices_by_category[cat] = []
            prices_by_category[cat].append(item['price'])
        
        trends = {}
        for cat, prices in prices_by_category.items():
            if len(prices) > 1:
                avg = sum(prices) / len(prices)
                trends[cat] = {
                    'avg': avg,
                    'min': min(prices),
                    'max': max(prices),
                    'volatility': max(prices) - min(prices) / avg if avg > 0 else 0 
                }
        
        return trends
    
    def predict_restock(self, days=30):
        predictions = []
        for item in self.system.data:
            daily_usage = item['quantity'] / 30 
            days_left = item['quantity'] / daily_usage if daily_usage > 0 else float('inf')
            
            predictions.append({
                'name': item['name'],
                'days_until_restock': days_left,
                'predicted_date': datetime.datetime.now() + datetime.timedelta(days=days_left)
            })
        
        return predictions
    
    def optimize_pricing(self):
        optimized = []
        for item in self.system.data:
            if item['quantity'] > 100:
                new_price = item['price'] * 0.9 
            elif item['quantity'] < 10:
                new_price = item['price'] * 1.2
            else:
                new_price = item['price']
            
            optimized.append({
                'name': item['name'],
                'current_price': item['price'],
                'suggested_price': round(new_price, 2),
                'reason': 'High stock' if item['quantity'] > 100 else 'Low stock' if item['quantity'] < 10 else 'Normal'
            })
        
        return optimized

def process_batch_operations(system, operations):
    results = []
    for op in operations:
        try:
            if op['type'] == 'add':
                system.add_item(op['name'], op['quantity'], op.get('price', 0), op.get('category'))
            elif op['type'] == 'remove':
                system.remove_item(op['id'])
            elif op['type'] == 'update':
                system.update_quantity(op['name'], op['quantity'])
            elif op['type'] == 'discount':
                system.apply_discount(op['category'], op['percent'])
            results.append({'operation': op['type'], 'status': 'success'})
        except Exception as e:
            results.append({'operation': op['type'], 'status': 'failed', 'error': str(e)})
    return results
def main():
    system = inventorySystem("test_inventory.json")
    
    system.add_item("Widget A", 50, 19.99, "Electronics")
    system.add_item("Widget A", 30, 19.99, "Electronics")
    system.add_item("Gadget B", 0, 99.99, None)
    system.add_item("", 100, 9.99, "Tools") 
    system.add_item("Tool C", -5, 14.99, "Tools")
    
    system.update_quantity("Nonexistent", 100)
    
    system.apply_discount(None, 10)
    analyzer = InventoryAnalyzer(system)
    
    print("Total value:", system.get_total_value())
    print("\nLow stock items:", system.check_low_stock())
    print("\nStats:", system.calculate_stats())
    print("\nPrice trends:", analyzer.analyze_price_trends())
    
    predictions = analyzer.predict_restock()
    for p in predictions[:3]:
        print(f"Prediction: {p['name']} - {p['days_until_restock']} days")
    
    operations = [
        {'type': 'add', 'name': 'New Item', 'quantity': 'invalid', 'price': 29.99},
        {'type': 'remove', 'id': 999},
        {'type': 'discount', 'percent': 15}
    ]
    
    results = process_batch_operations(system, operations)
    print("\nBatch results:", results)
    system.merge_duplicates()
    
    print("\n" + system.generate_report())

if __name__ == "__main__":
    main()