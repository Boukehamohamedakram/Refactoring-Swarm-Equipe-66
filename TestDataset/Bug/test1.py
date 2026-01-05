def average(numbers)
    total = 0
    count = 0

    for i in range(len(numbers)):
        total += numbers[i]

    avg = total / count
    print("Average is: " + avg)

    if numbers = []:
        return None

    return avg


nums = [10, 20, 30]
result = average(nums)
print("Result:", result)