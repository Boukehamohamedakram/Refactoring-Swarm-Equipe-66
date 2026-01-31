def average(numbers):
    # Bug fix: Handle empty input before computation to avoid errors
    if not numbers:
        return None

    # Bug fix: Validate input contains only numeric values
    if not all(isinstance(x, (int, float)) for x in numbers):
        raise TypeError("numbers must contain only numeric values")

    # Bug fix: Replace manual loop sum with Python's built-in sum
    # Bug fix: Division by zero avoided by using len(numbers)
    avg = sum(numbers) / len(numbers)

    # Bug fix: Removed print inside function to separate computation from side effects
    return avg


nums = [10, 20, 30]

# Bug fix: Printing done outside function, clean separation of concerns
result = average(nums)
print("Result:", result)