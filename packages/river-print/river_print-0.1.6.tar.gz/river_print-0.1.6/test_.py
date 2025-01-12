import time

n1 = 0
n2 = 1
count = 0
until = 2000

print(f"These are the first {until} numbers in the Fibonacci sequence:")
start = time.perf_counter()
while count < until:
    n1, n2 = n2, n1 + n2
    count += 1
cost = time.perf_counter() - start
print(f"cost:{cost}")
