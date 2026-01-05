def append_unique(value, lst=None):
    # Fix mutable default argument
    if lst is None:
        lst = []

    # Optionally: ensure lst is a list
    if not isinstance(lst, list):
        raise TypeError("lst must be a list")

    # Append value if not already present
    if value not in lst:
        lst.append(value)

    return lst


a = append_unique(1)
b = append_unique(2)
c = append_unique(1)

print(a)  # [1]
print(b)  # [2]
print(c)  # [1]