def countstr(st):
    output = {}
    for i in st:
        if i in output:
            output[i] += 1
        else:
            output[i] = 1
