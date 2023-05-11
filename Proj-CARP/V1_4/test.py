import multiprocessing

def add(a, b):
    return a + b

if __name__ == "__main__":
    pool = multiprocessing.Pool(3).starmap(add, [(1, 2), (3, 4)])
    print(pool)