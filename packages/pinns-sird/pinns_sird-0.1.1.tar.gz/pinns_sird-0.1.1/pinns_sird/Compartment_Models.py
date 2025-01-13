def dsdt_func(t=None, s=None, i=None, r=None, d=None, beta=None, gamma=None, mu=None):
    ds_dt = - beta * s * i / (s + i)
    return ds_dt


def didt_func(t=None, s=None, i=None, r=None, d=None, beta=None, gamma=None, mu=None):
    di_dt = beta * s * i/(s + i) - gamma * i - mu * i
    return di_dt


def drdt_func(t=None, s=None, i=None, r=None, d=None, beta=None, gamma=None, mu=None):
    dr_dt = gamma * i
    return dr_dt


def dddt_func(t=None, s=None, i=None, r=None, d=None, beta=None, gamma=None, mu=None):
    dd_dt = mu * i
    return dd_dt