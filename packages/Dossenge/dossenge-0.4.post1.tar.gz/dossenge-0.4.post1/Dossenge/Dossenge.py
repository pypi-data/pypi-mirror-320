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
    try:
        if sys.argv[1]=='equal':
            print(equal(eval(sys.argv[2]),eval(sys.argv[3])))
        elif sys.argv[1]=='cr':
            print(chicken_rabbit(eval(sys.argv[2]),eval(sys.argv[3])))
        else:
            print('Usage:')
            print('equal : Determine whether two numbers are equal')
            print('cr : Solving the problem of chickens and rabbits being housed in the same cage')
    except:
        print('Usage:')
        print('equal : Determine whether two numbers are equal')
        print('cr : Solving the problem of chickens and rabbits being housed in the same cage')


if __name__ == '__main__':
    pass