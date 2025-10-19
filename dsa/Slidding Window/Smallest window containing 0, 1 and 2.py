def smallestsubstring(s):
    n , i , j , k , cnt , min_len = len(s), 0 , 0 , 0 , 0 , float("inf")

    #frequency array
    freq = [0]*3
    