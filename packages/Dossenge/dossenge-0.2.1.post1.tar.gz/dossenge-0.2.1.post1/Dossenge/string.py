def countstr(st):
    output = {}
    for i in st:
        if i in output:
            output[i] += 1
        else:
            output[i] = 1
    return output

def save_add(filepath,string):
    with open(filepath,'a') as f:
        f.write(string)
    with open(filepath,'r') as f:
        content = f.readlines()
    return content