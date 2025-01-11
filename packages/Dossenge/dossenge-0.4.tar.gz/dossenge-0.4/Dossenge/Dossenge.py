import sys
def equal(x, y, roundnum=3):
    num = -roundnum
    rounder = 10**num
    if abs(x-y) < rounder:
        return True
    return False

def chicken_rabbit(head,foot):
    chicken = head
    rabbit = 0
    solutions = []
    for i in range(1,head+2):
        if chicken*2+rabbit*4 == foot:
            solutions.append((chicken, rabbit))
        chicken -= 1
        rabbit += 1
    return solutions

def dossenge():
    if sys.argv[1]=='equal':
        print(equal(eval(sys.argv[2]),eval(sys.argv[3])))
    elif sys.argv[1]=='cr':
        print(chicken_rabbit(eval(sys.argv[2]),eval(sys.argv[3])))

if __name__ == '__main__':
    pass