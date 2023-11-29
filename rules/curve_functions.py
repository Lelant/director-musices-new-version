import math

def power_fn_dec(x, power):
    return x**power

def power_fn_acc(x, power):
    return abs(((x - 1))**power)

def runrit_fn_dec(x, power):
    base = (((0.5**power) - 1.0) * x) + 1.0
    powerTo = 1.0 / power
    return (1.0 / (base**powerTo)) - 1

def runrit_fn_acc(x, power):
    return runrit_fn_dec(1.0 - x, power)

def accum_fn_dec(x, power):
    return math.exp(((x - 1)**1) / 0.1)

def accum_fn_acc(x, power):
    return accum_fn_dec(1 - x, 0)

def accumslow_fn_dec(x, power):
    return math.exp(((x - 1)**1) / 1.5)

def accumslow_fn_acc(x, power):
    return accumslow_fn_dec(1 - x, 0)

def accumfast_fn_dec(x, power):
    return math.exp(((x - 1)**1) / 0.08)

def accumfast_fn_acc(x, power):
    return accumfast_fn_dec(1 - x, 0)

def gauss_fn_dec(x, power):
    return math.exp(((x - 1)**2) / -0.1)

def gauss_fn_acc(x, power):
    return gauss_fn_dec(1 - x, 0)

def cos_fn_dec(x, power):
    return (math.cos((x * math.pi) - math.pi) + 1) / 2.0

def cos_fn_acc(x, power):
    return cos_fn_dec(1 - x, 0)

curve_functions = {
    'power_fn_dec': power_fn_dec,
    'power_fn_acc': power_fn_acc,
    'runrit_fn_dec': runrit_fn_dec,
    'runrit_fn_acc': runrit_fn_acc,
    'accum_fn_dec': accum_fn_dec,
    'accum_fn_acc': accum_fn_acc,
    'accumslow_fn_dec': accumslow_fn_dec,
    'accumslow_fn_acc': accumslow_fn_acc,
    'accumfast_fn_dec': accumfast_fn_dec,
    'accumfast_fn_acc': accumfast_fn_acc,
    'gauss_fn_dec': gauss_fn_dec,
    'gauss_fn_acc': gauss_fn_acc,
    'cos_fn_dec': cos_fn_dec,
    'cos_fn_acc': cos_fn_acc,
}
