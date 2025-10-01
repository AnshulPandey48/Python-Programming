#n  = input("enter the number of fibinahci termss you want")
n = 10

a, b = 0 , 1
print(a,end = " ")
for i in range(n-1):
    print(f"{b} ")
    a,b = b, a + b