def read(n, s = "", func = lambda s: s):
	return [func(input(s)) for i in range(n)]
def read_split(s = "", spl = " ", func = lambda s: s):
	return [func(i) for i in input(s).split(spl)]
