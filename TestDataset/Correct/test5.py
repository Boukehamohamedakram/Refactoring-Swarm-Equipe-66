import json
import datetime
import sys
from typing import List, Dict, Any, Optional

class InventorySystem:
    def __init__(self, filename="data.json"):
        self.data = []
        self.filename = filename
        self.cache = {}
        self.log = []
        self.load()
    
    def load(self) -> None:
        """Load inventory data from file."""
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                content = file.read()
                if content.strip():
                    self.data = json.loads(content)
                else:
                    self.data = []
        except FileNotFoundError:
            self.data = []
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {self.filename}: {e}")
            self.data = []
        except Exception as e:
            print(f"Error loading file: {e}")
            self.data = []
    
    def save(self) -> None:
        """Save inventory data to file."""
        try:
            with open(self.filename, 'w', encoding='utf-8') as file:
                json.dump(self.data, file, indent=4, default=self._json_serializer)
        except (IOError, PermissionError) as e:
            print(f"Save failed: {e}")
            raise
    
    @staticmethod
    def _json_serializer(obj: Any) -> Any:
        """Handle JSON serialization for datetime objects."""
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    def add_item(self, name: str, quantity: int, price: float, category: Optional[str] = None) -> None:
        """Add a new item or update existing item quantity."""
        # Input validation
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Item name must be a non-empty string")
        if not isinstance(quantity, int) or quantity < 0:
            raise ValueError("Quantity must be a non-negative integer")
        if not isinstance(price, (int, float)) or price < 0:
            raise ValueError("Price must be a non-negative number")
        
        # Check for existing item
        for item in self.data:
            if item.get('name') == name and item.get('category') == category:
                item['quantity'] += quantity
                item['last_updated'] = datetime.datetime.now().isoformat()
                self.save()
                return
        
        # Create new item
        new_item = {
            'id': len(self.data) + 1,
            'name': name.strip(),
            'quantity': quantity,
            'price': float(price),
            'category': category,
            'date_added': datetime.datetime.now().isoformat(),
            'last_updated': datetime.datetime.now().isoformat()
        }
        self.data.append(new_item)
        self.save()
    
    def remove_item(self, item_id: int) -> bool:
        """Remove item by ID. Returns True if item was removed."""
        if not isinstance(item_id, int) or item_id < 1:
            raise ValueError("Item ID must be a positive integer")
        
        for i, item in enumerate(self.data):
            if item.get('id') == item_id:
                del self.data[i]
                self.save()
                return True
        return False
    
    def update_quantity(self, name: str, new_quantity: int) -> bool:
        """Update item quantity. Returns True if successful."""
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Item name must be a non-empty string")
        if not isinstance(new_quantity, int) or new_quantity < 0:
            raise ValueError("Quantity must be a non-negative integer")
        
        found = False
        for item in self.data:
            if item.get('name') == name:
                item['quantity'] = new_quantity
                item['last_updated'] = datetime.datetime.now().isoformat()
                found = True
        
        if found:
            self.save()
        return found
    
    def get_total_value(self) -> float:
        """Calculate total value of all inventory items."""
        total = 0.0
        for item in self.data:
            # Ensure both values exist and are numbers
            quantity = item.get('quantity', 0)
            price = item.get('price', 0.0)
            if isinstance(quantity, (int, float)) and isinstance(price, (int, float)):
                total += float(quantity) * float(price)
        return total
    
    def find_item(self, name: str) -> List[Dict[str, Any]]:
        """Find items by name (case-insensitive partial match)."""
        if not isinstance(name, str):
            return []
        
        search_name = name.lower()
        results = []
        for item in self.data:
            item_name = item.get('name', '')
            if isinstance(item_name, str) and search_name in item_name.lower():
                results.append(item)
        return results
    
    def apply_discount(self, category: Optional[str], discount_percent: float) -> None:
        """Apply discount to items in a specific category."""
        if not isinstance(discount_percent, (int, float)) or discount_percent < 0 or discount_percent > 100:
            raise ValueError("Discount percent must be between 0 and 100")
        
        updated = False
        discount_factor = 1.0 - (discount_percent / 100.0)
        
        for item in self.data:
            item_category = item.get('category')
            if (category is None and item_category is None) or item_category == category:
                current_price = item.get('price', 0.0)
                if isinstance(current_price, (int, float)):
                    item['price'] = float(current_price) * discount_factor
                    item['last_updated'] = datetime.datetime.now().isoformat()
                    updated = True
        
        if updated:
            self.save()
    
    def generate_report(self) -> str:
        """Generate inventory report."""
        if not self.data:
            return "Inventory is empty"
        
        # Group by category
        report_dict = {}
        for item in self.data:
            category = item.get('category', 'Uncategorized')
            if category not in report_dict:
                report_dict[category] = []
            report_dict[category].append(item)
        
        # Build report string
        output = "Inventory Report\n"
        output += "=" * 50 + "\n"
        
        for category, items in report_dict.items():
            output += f"\nCategory: {category if category else 'Uncategorized'}\n"
            for item in items:
                name = item.get('name', 'Unknown')
                quantity = item.get('quantity', 0)
                price = item.get('price', 0.0)
                output += f"  {name}: {quantity} @ ${float(price):.2f}\n"
        
        return output
    
    def check_low_stock(self, threshold: int = 10) -> List[Dict[str, Any]]:
        """Get items with quantity below threshold."""
        if not isinstance(threshold, int) or threshold < 0:
            raise ValueError("Threshold must be a non-negative integer")
        
        low_items = []
        for item in self.data:
            quantity = item.get('quantity', 0)
            if isinstance(quantity, (int, float)) and float(quantity) < threshold:
                low_items.append(item)
        return low_items
    
    def merge_duplicates(self) -> Dict[str, List[int]]:
        """Merge duplicate items (same name and category)."""
        seen = {}
        merged_info = {}
        items_to_remove = []
        
        # First pass: identify duplicates
        for i, item in enumerate(self.data):
            name = item.get('name')
            category = item.get('category')
            key = (name, category)
            
            if key in seen:
                original_idx = seen[key]
                # Merge quantities
                original_quantity = self.data[original_idx].get('quantity', 0)
                current_quantity = item.get('quantity', 0)
                if isinstance(original_quantity, (int, float)) and isinstance(current_quantity, (int, float)):
                    self.data[original_idx]['quantity'] = float(original_quantity) + float(current_quantity)
                    self.data[original_idx]['last_updated'] = datetime.datetime.now().isoformat()
                
                # Track merged items
                item_id = item.get('id')
                if item_id:
                    if original_idx not in merged_info:
                        original_id = self.data[original_idx].get('id')
                        merged_info[original_id] = [item_id]
                    else:
                        merged_info[original_id].append(item_id)
                
                items_to_remove.append(i)
            else:
                seen[key] = i
        
        # Remove duplicates in reverse order to maintain indices
        for i in sorted(items_to_remove, reverse=True):
            del self.data[i]
        
        if items_to_remove:
            self.save()
        
        return merged_info
    
    def calculate_stats(self) -> Dict[str, Any]:
        """Calculate inventory statistics."""
        if not self.data:
            return {
                'avg_price': 0.0,
                'max_price': 0.0,
                'min_price': 0.0,
                'total_items': 0,
                'unique_items': 0
            }
        
        valid_prices = []
        total_quantity = 0
        
        for item in self.data:
            price = item.get('price')
            quantity = item.get('quantity', 0)
            
            if isinstance(price, (int, float)):
                valid_prices.append(float(price))
            
            if isinstance(quantity, (int, float)):
                total_quantity += int(quantity)
        
        if not valid_prices:
            return {
                'avg_price': 0.0,
                'max_price': 0.0,
                'min_price': 0.0,
                'total_items': total_quantity,
                'unique_items': len(self.data)
            }
        
        return {
            'avg_price': sum(valid_prices) / len(valid_prices),
            'max_price': max(valid_prices),
            'min_price': min(valid_prices),
            'total_items': total_quantity,
            'unique_items': len(self.data)
        }


class InventoryAnalyzer:
    def __init__(self, system: InventorySystem):
        self.system = system
        self.history = []
    
    def analyze_price_trends(self) -> Dict[str, Dict[str, float]]:
        """Analyze price statistics by category."""
        if not self.system.data:
            return {}
        
        prices_by_category = {}
        for item in self.system.data:
            cat = item.get('category', 'Unknown')
            price = item.get('price')
            
            if isinstance(price, (int, float)):
                if cat not in prices_by_category:
                    prices_by_category[cat] = []
                prices_by_category[cat].append(float(price))
        
        trends = {}
        for cat, prices in prices_by_category.items():
            if len(prices) > 1:
                avg = sum(prices) / len(prices)
                price_range = max(prices) - min(prices)
                volatility = price_range / avg if avg > 0 else 0
                
                trends[cat] = {
                    'avg': avg,
                    'min': min(prices),
                    'max': max(prices),
                    'range': price_range,
                    'volatility': volatility
                }
        
        return trends
    
    def predict_restock(self, daily_usage: Dict[str, float] = None, days: int = 30) -> List[Dict[str, Any]]:
        """Predict when items need restocking based on daily usage."""
        if not isinstance(days, int) or days <= 0:
            raise ValueError("Days must be a positive integer")
        
        predictions = []
        current_date = datetime.datetime.now()
        
        for item in self.system.data:
            item_name = item.get('name', 'Unknown')
            quantity = item.get('quantity', 0)
            
            if not isinstance(quantity, (int, float)) or float(quantity) <= 0:
                continue
            
            # Get daily usage estimate
            if daily_usage and item_name in daily_usage:
                usage = daily_usage[item_name]
            else:
                # Default: 1% of current stock per day
                usage = float(quantity) * 0.01
            
            if usage <= 0:
                days_left = float('inf')
            else:
                days_left = float(quantity) / usage
            
            predictions.append({
                'name': item_name,
                'current_stock': quantity,
                'daily_usage_estimate': usage,
                'days_until_restock': days_left,
                'predicted_date': current_date + datetime.timedelta(days=days_left)
            })
        
        return predictions
    
    def optimize_pricing(self, demand_data: Dict[str, float] = None) -> List[Dict[str, Any]]:
        """Suggest optimized pricing based on stock levels and demand."""
        optimized = []
        
        for item in self.system.data:
            name = item.get('name', 'Unknown')
            quantity = item.get('quantity', 0)
            current_price = item.get('price', 0.0)
            
            if not isinstance(quantity, (int, float)) or not isinstance(current_price, (int, float)):
                continue
            
            quantity = float(quantity)
            current_price = float(current_price)
            
            # Get demand factor if available
            demand = demand_data.get(name, 1.0) if demand_data else 1.0
            
            # Pricing logic with demand consideration
            if quantity > 100:
                # High stock: discount if low demand
                if demand < 0.8:
                    new_price = current_price * 0.85  # 15% discount
                    reason = 'High stock, low demand'
                else:
                    new_price = current_price * 0.95  # 5% discount
                    reason = 'High stock'
            elif quantity < 10:
                # Low stock: increase price if high demand
                if demand > 1.2:
                    new_price = current_price * 1.25  # 25% increase
                    reason = 'Low stock, high demand'
                else:
                    new_price = current_price * 1.1  # 10% increase
                    reason = 'Low stock'
            else:
                # Normal stock: adjust based on demand
                if demand > 1.5:
                    new_price = current_price * 1.15
                    reason = 'High demand'
                elif demand < 0.7:
                    new_price = current_price * 0.9
                    reason = 'Low demand'
                else:
                    new_price = current_price
                    reason = 'Normal demand'
            
            optimized.append({
                'name': name,
                'current_price': current_price,
                'suggested_price': round(new_price, 2),
                'price_change_percent': round(((new_price / current_price) - 1) * 100, 1),
                'reason': reason,
                'current_stock': quantity,
                'demand_factor': demand
            })
        
        return optimized


def process_batch_operations(system: InventorySystem, operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Process batch operations with error handling."""
    results = []
    
    for i, op in enumerate(operations):
        try:
            if 'type' not in op:
                raise ValueError("Operation missing 'type' field")
            
            if op['type'] == 'add':
                # Validate required fields
                required = ['name', 'quantity', 'price']
                for field in required:
                    if field not in op:
                        raise ValueError(f"Add operation missing '{field}' field")
                
                # Convert and validate types
                name = str(op['name'])
                quantity = int(op['quantity'])
                price = float(op['price'])
                category = op.get('category')
                
                system.add_item(name, quantity, price, category)
                results.append({'operation_index': i, 'type': 'add', 'status': 'success'})
            
            elif op['type'] == 'remove':
                if 'id' not in op:
                    raise ValueError("Remove operation missing 'id' field")
                
                success = system.remove_item(int(op['id']))
                status = 'success' if success else 'failed (item not found)'
                results.append({'operation_index': i, 'type': 'remove', 'status': status})
            
            elif op['type'] == 'update':
                if 'name' not in op or 'quantity' not in op:
                    raise ValueError("Update operation missing 'name' or 'quantity' field")
                
                success = system.update_quantity(str(op['name']), int(op['quantity']))
                status = 'success' if success else 'failed (item not found)'
                results.append({'operation_index': i, 'type': 'update', 'status': status})
            
            elif op['type'] == 'discount':
                if 'category' not in op or 'percent' not in op:
                    raise ValueError("Discount operation missing 'category' or 'percent' field")
                
                system.apply_discount(op['category'], float(op['percent']))
                results.append({'operation_index': i, 'type': 'discount', 'status': 'success'})
            
            else:
                raise ValueError(f"Unknown operation type: {op['type']}")
                
        except Exception as e:
            results.append({
                'operation_index': i,
                'type': op.get('type', 'unknown'),
                'status': 'failed',
                'error': str(e)
            })
    
    return results


def main():
    """Example usage of the corrected inventory system."""
    print("=== Inventory System Demo ===\n")
    
    # Initialize system
    system = InventorySystem("test_inventory.json")
    
    # Clear existing data for demo
    system.data = []
    
    try:
        # Add items with proper data
        print("Adding items...")
        system.add_item("Widget A", 50, 19.99, "Electronics")
        system.add_item("Widget A", 30, 19.99, "Electronics")  # Should update quantity
        system.add_item("Gadget B", 25, 99.99, "Electronics")
        system.add_item("Hammer", 15, 24.99, "Tools")
        system.add_item("Stapler", 5, 12.49, "Office Supplies")
        
        # These should fail with validation errors
        try:
            system.add_item("", 100, 9.99, "Tools")
        except ValueError as e:
            print(f"Expected error (empty name): {e}")
        
        try:
            system.add_item("Invalid", -5, 14.99, "Tools")
        except ValueError as e:
            print(f"Expected error (negative quantity): {e}")
        
        # Update quantity
        print("\nUpdating quantities...")
        success = system.update_quantity("Widget A", 25)
        print(f"Updated Widget A: {'Success' if success else 'Failed'}")
        
        # Try to update non-existent item
        success = system.update_quantity("Nonexistent", 100)
        print(f"Updated Nonexistent item: {'Success' if success else 'Failed (expected)'}")
        
        # Apply discount
        print("\nApplying discount...")
        system.apply_discount("Electronics", 10)  # 10% discount
        
        # Generate and display report
        print("\n" + system.generate_report())
        
        # Calculate statistics
        stats = system.calculate_stats()
        print(f"\nStatistics:")
        print(f"  Average price: ${stats['avg_price']:.2f}")
        print(f"  Total items: {stats['total_items']}")
        print(f"  Unique items: {stats['unique_items']}")
        
        # Check low stock
        low_stock = system.check_low_stock()
        print(f"\nLow stock items (threshold: 10): {len(low_stock)} items")
        for item in low_stock:
            print(f"  {item.get('name')}: {item.get('quantity')}")
        
        # Analyze price trends
        analyzer = InventoryAnalyzer(system)
        trends = analyzer.analyze_price_trends()
        print("\nPrice trends by category:")
        for category, data in trends.items():
            print(f"  {category}: Avg=${data['avg']:.2f}, Volatility={data['volatility']:.2f}")
        
        # Predict restock needs
        daily_usage = {"Widget A": 2.0, "Gadget B": 1.0}
        predictions = analyzer.predict_restock(daily_usage)
        print("\nRestock predictions:")
        for pred in predictions[:2]:  # Show first 2
            print(f"  {pred['name']}: Restock in {pred['days_until_restock']:.1f} days")
        
        # Optimize pricing
        demand_data = {"Widget A": 1.5, "Gadget B": 0.8, "Hammer": 1.2}
        optimized = analyzer.optimize_pricing(demand_data)
        print("\nPricing optimization suggestions:")
        for opt in optimized[:2]:  # Show first 2
            print(f"  {opt['name']}: ${opt['current_price']:.2f} -> ${opt['suggested_price']:.2f} ({opt['reason']})")
        
        # Process batch operations
        print("\nProcessing batch operations...")
        operations = [
            {'type': 'add', 'name': 'New Item', 'quantity': 20, 'price': 29.99, 'category': 'Tools'},
            {'type': 'remove', 'id': 999},  # Non-existent ID
            {'type': 'update', 'name': 'Widget A', 'quantity': 40},
            {'type': 'discount', 'category': 'Tools', 'percent': 15}
        ]
        
        batch_results = process_batch_operations(system, operations)
        print("Batch results:")
        for result in batch_results:
            print(f"  Operation {result['operation_index']} ({result['type']}): {result['status']}")
        
        # Merge duplicates
        print("\nMerging duplicates...")
        merged = system.merge_duplicates()
        if merged:
            print(f"Merged items: {merged}")
        
        print("\n=== Demo Complete ===")
        
    except Exception as e:
        print(f"\nError in demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()