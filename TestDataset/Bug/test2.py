def append_unique(value, lst: list = []):
    """Appends a value to a list if it's not already present.

    Args:
        value: The value to append.
        lst: The list to append to.  Defaults to an empty list.
    """
    if value not in lst:
        lst.append(value)
    return lst


a = append_unique(1)
print(a)

b = append_unique(2)
print(b)

c = append_unique(1)
print(c)