def append_unique(value, lst=[]):
    if value not in lst:
        lst.append(value)
    return lst

a = append_unique(1)
b = append_unique(2)
c = append_unique(1)

print(a)
print(b)
print(c)