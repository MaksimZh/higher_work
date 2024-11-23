#type: ignore

def fibs_sum():
    fsum = 0
    while True:
        fsum += yield fsum
     
def get_fibs(num):
    a, b = 1, 1
    gsum = fibs_sum()

    gsum.send(None)
    for i in range(num):
        a, b = b, gsum.send(a)
        yield a

for f in get_fibs(10):
    print(f)
