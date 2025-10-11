k = 7
# generating fibo nachi series up to 7
l = 0
r = 7
start = 0
nextt = 1
for i in range(7):
    start = start + nextt
    nextt = nextt + start
    print(start)
    print(nextt)