import torch
import numpy as np
import matplotlib.pyplot as plt
from .Compartment_Models import dsdt_func, dddt_func, didt_func, drdt_func

# AB2----------------------------------------------
# y_{n+2} = y_{n+1} + \frac{3}{2}hf(t_{n+1},y_{n+1}) - \frac{1}{2}hf(t_{n},y_{n})
# 定义方程

# ----------------显示多步方法----------------


def adams_bashforth2(t = None, s0 = None, i0 = None, r0 = None, d0 = None,
                     s_1 = None, i_1 = None, r_1 = None, d_1 = None,h = None,
                     beta=None, gamma=None, mu=None,
                     beta_1 = None, gamma_1 = None, mu_1 = None):
    deltaS = (3*dsdt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu) -
              dsdt_func(t=t - h, s=s_1, i=i_1, r=r_1, d=d_1, beta=beta_1, gamma=gamma_1, mu=mu_1)) * h / 2
    deltaI = (3 * didt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu) -
              didt_func(t=t - h, s=s_1, i=i_1, r=r_1, d=d_1, beta=beta_1, gamma=gamma_1, mu=mu_1)) * h / 2
    deltaR = (3 * drdt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu) -
              drdt_func(t=t - h, s=s_1, i=i_1, r=r_1, d=d_1, beta=beta_1, gamma=gamma_1, mu=mu_1)) * h / 2
    deltaD = (3 * dddt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu) -
              dddt_func(t=t - h, s=s_1, i=i_1, r=r_1, d=d_1, beta=beta_1, gamma=gamma_1, mu=mu_1)) * h / 2

    s = s0 + deltaS
    i = i0 + deltaI
    r = r0 + deltaR
    d = d0 + deltaD

    return s, i, r, d
def adams_bashforth3(t = None, s0 = None, i0 = None, r0 = None, d0 = None,
                     s_1 = None, i_1 = None, r_1 = None, d_1 = None,
                     s_2 = None, i_2 = None, r_2 = None, d_2 = None,h = None,
                     beta=None, gamma=None, mu=None,
                     beta_1 = None, gamma_1 = None, mu_1 = None,
                     beta_2 = None, gamma_2 = None, mu_2 = None
                     ):
    deltaS = (23 * dsdt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu) -
              16 * dsdt_func(t=t - h, s=s_1, i=i_1, r=r_1, d=d_1, beta=beta_1, gamma=gamma_1, mu=mu_1) +
              5 * dsdt_func(t=t - 2 * h, s=s_2, i=i_2, r=r_2, d=d_2, beta=beta_2, gamma=gamma_2, mu=mu_2)) * h / 12
    deltaI = (23 * didt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu) -
              16 * didt_func(t=t - h, s=s_1, i=i_1, r=r_1, d=d_1, beta=beta_1, gamma=gamma_1, mu=mu_1) +
              5 * didt_func(t=t - 2 * h, s=s_2, i=i_2, r=r_2, d=d_2, beta=beta_2, gamma=gamma_2, mu=mu_2)) * h / 12
    deltaR = (23 * drdt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu) -
              16 * drdt_func(t=t - h, s=s_1, i=i_1, r=r_1, d=d_1, beta=beta_1, gamma=gamma_1, mu=mu_1) +
              5 * drdt_func(t=t - 2 * h, s=s_2, i=i_2, r=r_2, d=d_2, beta=beta_2, gamma=gamma_2, mu=mu_2)) * h / 12
    deltaD = (23 * dddt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu) -
              16 * dddt_func(t=t - h, s=s_1, i=i_1, r=r_1, d=d_1, beta=beta_1, gamma=gamma_1, mu=mu_1) +
              5 * dddt_func(t=t - 2 * h, s=s_2, i=i_2, r=r_2, d=d_2, beta=beta_2, gamma=gamma_2, mu=mu_2)) * h / 12

    s = s0 + deltaS
    i = i0 + deltaI
    r = r0 + deltaR
    d = d0 + deltaD

    return s, i, r, d

def adams_bashforth4(t = None, s0 = None, i0 = None, r0 = None, d0 = None,
                     s_1 = None, i_1 = None, r_1 = None, d_1 = None,
                     s_2 = None, i_2 = None, r_2 = None, d_2 = None,
                     s_3 = None, i_3 = None, r_3 = None, d_3 = None,
                     h = None, beta=None, gamma=None, mu=None):
    deltaS = (55 * dsdt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu) -
              59 * dsdt_func(t=t - h, s=s_1, i=i_1, r=r_1, d=d_1, beta=beta, gamma=gamma, mu=mu) +
              37 * dsdt_func(t=t - 2 * h, s=s_2, i=i_2, r=r_2, d=d_2, beta=beta, gamma=gamma, mu=mu) -
              9 * dsdt_func(t=t - 3 * h, s=s_3, i=i_3, r=r_3, d=d_3, beta=beta, gamma=gamma, mu=mu)) * h / 24
    deltaI = (55 * didt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu) -
              59 * didt_func(t=t - h, s=s_1, i=i_1, r=r_1, d=d_1, beta=beta, gamma=gamma, mu=mu) +
              37 * didt_func(t=t - 2 * h, s=s_2, i=i_2, r=r_2, d=d_2, beta=beta, gamma=gamma, mu=mu) -
              9 * didt_func(t=t - 3 * h, s=s_3, i=i_3, r=r_3, d=d_3, beta=beta, gamma=gamma, mu=mu)) * h / 24
    deltaR = (55 * drdt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu) -
              59 * drdt_func(t=t - h, s=s_1, i=i_1, r=r_1, d=d_1, beta=beta, gamma=gamma, mu=mu) +
              37 * drdt_func(t=t - 2 * h, s=s_2, i=i_2, r=r_2, d=d_2, beta=beta, gamma=gamma, mu=mu) -
              9 * drdt_func(t=t - 3 * h, s=s_3, i=i_3, r=r_3, d=d_3, beta=beta, gamma=gamma, mu=mu)) * h / 24
    deltaD = (55 * dddt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu) -
              59 * dddt_func(t=t - h, s=s_1, i=i_1, r=r_1, d=d_1, beta=beta, gamma=gamma, mu=mu) +
              37 * dddt_func(t=t - 2 * h, s=s_2, i=i_2, r=r_2, d=d_2, beta=beta, gamma=gamma, mu=mu) -
              9 * dddt_func(t=t - 3 * h, s=s_3, i=i_3, r=r_3, d=d_3, beta=beta, gamma=gamma, mu=mu)) * h / 24

    s = s0 + deltaS
    i = i0 + deltaI
    r = r0 + deltaR
    d = d0 + deltaD

    return s, i, r, d

def milne4(t = None, s0 = None, i0 = None, r0 = None, d0 = None,
           s_1 = None, i_1 = None, r_1 = None, d_1 = None,
           s_2 = None, i_2 = None, r_2 = None, d_2 = None,
           s_3=None, i_3=None, r_3=None, d_3=None,
           h=None,
           beta=None, gamma=None, mu=None,
           beta_1=None, gamma_1=None, mu_1=None,
           beta_2=None, gamma_2=None, mu_2=None,
           ):
    deltaS = (2 * dsdt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu) -
              dsdt_func(t=t - h, s=s_1, i=i_1, r=r_1, d=d_1, beta=beta_1, gamma=gamma_1, mu=mu_1) +
              2 * dsdt_func(t=t - 2 * h, s=s_2, i=i_2, r=r_2, d=d_2, beta=beta_2, gamma=gamma_2, mu=mu_2)) * 4 * h / 3

    deltaI = (2 * didt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu) -
              didt_func(t=t - h, s=s_1, i=i_1, r=r_1, d=d_1, beta=beta_1, gamma=gamma_1, mu=mu_1) +
              2 * didt_func(t=t - 2 * h, s=s_2, i=i_2, r=r_2, d=d_2, beta=beta_2, gamma=gamma_2, mu=mu_2)) * 4 * h / 3

    deltaR = (2 * drdt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu) -
              drdt_func(t=t - h, s=s_1, i=i_1, r=r_1, d=d_1, beta=beta_1, gamma=gamma_1, mu=mu_1) +
              2 * drdt_func(t=t - 2 * h, s=s_2, i=i_2, r=r_2, d=d_2, beta=beta_2, gamma=gamma_2, mu=mu_2)) * 4 * h / 3

    deltaD = (2 * dddt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu) -
              dddt_func(t=t - h, s=s_1, i=i_1, r=r_1, d=d_1, beta=beta_1, gamma=gamma_1, mu=mu_1) +
              2 * dddt_func(t=t - 2 * h, s=s_2, i=i_2, r=r_2, d=d_2, beta=beta_2, gamma=gamma_2, mu=mu_2)) * 4 * h / 3

    s = s_3 + deltaS
    i = i_3 + deltaI
    r = r_3 + deltaR
    d = d_3 + deltaD

    return s, i, r, d

# -----------------单步迭代方法-------------------
# 使用Runge-Kutta 更新微分方程的值。输入当前值和当前时刻，以及时间步长，得到下一时刻的值
def SIRD_RK4(t=None, s0=20, i0=10, r0=5, d0=4, h=None, beta=None, gamma=None, mu=None):
    """
    Args:
        t: 时间点
        s0: s的当前值
        i0: i的当前值
        r0: r的当前值
        d0: d的当前值
        h: t的步长
        beta:
        gamma:
        mu:
    Returns:
        迭代更新后的值
    """
    # t += h
    Ks_1 = dsdt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu)
    Ki_1 = didt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu)
    Kr_1 = drdt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu)
    Kd_1 = dddt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu)

    Ks_2 = dsdt_func(t=t+h/2, s=s0+h/2*Ks_1, i=i0+h/2*Ks_1, r=r0+h/2*Ks_1, d=d0+h/2*Ks_1, beta=beta, gamma=gamma, mu=mu)
    Ki_2 = didt_func(t=t+h/2, s=s0+h/2*Ki_1, i=i0+h/2*Ki_1, r=r0+h/2*Ki_1, d=d0+h/2*Ki_1, beta=beta, gamma=gamma, mu=mu)
    Kr_2 = drdt_func(t=t+h/2, s=s0+h/2*Kr_1, i=i0+h/2*Kr_1, r=r0+h/2*Kr_1, d=d0+h/2*Kr_1, beta=beta, gamma=gamma, mu=mu)
    Kd_2 = dddt_func(t=t+h/2, s=s0+h/2*Kd_1, i=i0+h/2*Kd_1, r=r0+h/2*Kd_1, d=d0+h/2*Kd_1, beta=beta, gamma=gamma, mu=mu)

    Ks_3 = dsdt_func(t=t+h/2, s=s0+h/2*Ks_2, i=i0+h/2*Ks_2, r=r0+h/2*Ks_2, d=d0+h/2*Ks_2, beta=beta, gamma=gamma, mu=mu)
    Ki_3 = didt_func(t=t+h/2, s=s0+h/2*Ki_2, i=i0+h/2*Ki_2, r=r0+h/2*Ki_2, d=d0+h/2*Ki_2, beta=beta, gamma=gamma, mu=mu)
    Kr_3 = drdt_func(t=t+h/2, s=s0+h/2*Kr_2, i=i0+h/2*Kr_2, r=r0+h/2*Kr_2, d=d0+h/2*Kr_2, beta=beta, gamma=gamma, mu=mu)
    Kd_3 = dddt_func(t=t+h/2, s=s0+h/2*Kd_2, i=i0+h/2*Kd_2, r=r0+h/2*Kd_2, d=d0+h/2*Kd_2, beta=beta, gamma=gamma, mu=mu)

    Ks_4 = dsdt_func(t=t+h, s=s0+h*Ks_3, i=i0+h*Ks_3, r=r0+h*Ks_3, d=d0+h*Ks_3, beta=beta, gamma=gamma, mu=mu)
    Ki_4 = didt_func(t=t+h, s=s0+h*Ki_3, i=i0+h*Ki_3, r=r0+h*Ki_3, d=d0+h*Ki_3, beta=beta, gamma=gamma, mu=mu)
    Kr_4 = drdt_func(t=t+h, s=s0+h*Kr_3, i=i0+h*Kr_3, r=r0+h*Kr_3, d=d0+h*Kr_3, beta=beta, gamma=gamma, mu=mu)
    Kd_4 = dddt_func(t=t+h, s=s0+h*Kd_3, i=i0+h*Kd_3, r=r0+h*Kd_3, d=d0+h*Kd_3, beta=beta, gamma=gamma, mu=mu)

    s = s0 + (Ks_1 + 2 * Ks_2 + 2 * Ks_3 + Ks_4) * h / 6
    i = i0 + (Ki_1 + 2 * Ki_2 + 2 * Ki_3 + Ki_4) * h / 6
    r = r0 + (Kr_1 + 2 * Kr_2 + 2 * Kr_3 + Kr_4) * h / 6
    d = d0 + (Kd_1 + 2 * Kd_2 + 2 * Kd_3 + Kd_4) * h / 6

    return s, i, r, d

def SIRD_RK6(t=None, s0=20, i0=10, r0=5, d0=4, h=None, beta=None, gamma=None, mu=None):

    Ks_1 = dsdt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu)
    Ki_1 = didt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu)
    Kr_1 = drdt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu)
    Kd_1 = dddt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu)

    Ks_2 = dsdt_func(t=t+h/2, s=s0+h/2*Ks_1, i=i0+h/2*Ks_1, r=r0+h/2*Ks_1, d=d0+h/2*Ks_1, beta=beta, gamma=gamma, mu=mu)
    Ki_2 = didt_func(t=t+h/2, s=s0+h/2*Ki_1, i=i0+h/2*Ki_1, r=r0+h/2*Ki_1, d=d0+h/2*Ki_1, beta=beta, gamma=gamma, mu=mu)
    Kr_2 = drdt_func(t=t+h/2, s=s0+h/2*Kr_1, i=i0+h/2*Kr_1, r=r0+h/2*Kr_1, d=d0+h/2*Kr_1, beta=beta, gamma=gamma, mu=mu)
    Kd_2 = dddt_func(t=t+h/2, s=s0+h/2*Kd_1, i=i0+h/2*Kd_1, r=r0+h/2*Kd_1, d=d0+h/2*Kd_1, beta=beta, gamma=gamma, mu=mu)

    Ks_3 = dsdt_func(t=t+h/2, s=s0+h/2*Ks_2, i=i0+h/2*Ks_2, r=r0+h/2*Ks_2, d=d0+h/2*Ks_2, beta=beta, gamma=gamma, mu=mu)
    Ki_3 = didt_func(t=t+h/2, s=s0+h/2*Ki_2, i=i0+h/2*Ki_2, r=r0+h/2*Ki_2, d=d0+h/2*Ki_2, beta=beta, gamma=gamma, mu=mu)
    Kr_3 = drdt_func(t=t+h/2, s=s0+h/2*Kr_2, i=i0+h/2*Kr_2, r=r0+h/2*Kr_2, d=d0+h/2*Kr_2, beta=beta, gamma=gamma, mu=mu)
    Kd_3 = dddt_func(t=t+h/2, s=s0+h/2*Kd_2, i=i0+h/2*Kd_2, r=r0+h/2*Kd_2, d=d0+h/2*Kd_2, beta=beta, gamma=gamma, mu=mu)

    Ks_4 = dsdt_func(t=t+h, s=s0+h*Ks_3, i=i0+h*Ks_3, r=r0+h*Ks_3, d=d0+h*Ks_3, beta=beta, gamma=gamma, mu=mu)
    Ki_4 = didt_func(t=t+h, s=s0+h*Ki_3, i=i0+h*Ki_3, r=r0+h*Ki_3, d=d0+h*Ki_3, beta=beta, gamma=gamma, mu=mu)
    Kr_4 = drdt_func(t=t+h, s=s0+h*Kr_3, i=i0+h*Kr_3, r=r0+h*Kr_3, d=d0+h*Kr_3, beta=beta, gamma=gamma, mu=mu)
    Kd_4 = dddt_func(t=t+h, s=s0+h*Kd_3, i=i0+h*Kd_3, r=r0+h*Kd_3, d=d0+h*Kd_3, beta=beta, gamma=gamma, mu=mu)

    Ks_5 = dsdt_func(t=t + 2*h / 3, s = s0 + 7 * Ks_1 / 27 + 10 * Ks_2 / 27 + Ks_4 / 27,
                     i=i0 + 7 * Ki_1 / 27 + 10 * Ki_2 / 27 + Ki_4 / 27,
                     r=r0 + 7 * Kr_1 / 27 + 10 * Kr_2 / 27 + Kr_4 / 27,
                     d=d0 + 7 * Kd_1 / 27 + 10 * Kd_2 / 27 + Kd_4 / 27, beta=beta, gamma=gamma, mu=mu)
    Ki_5 = didt_func(t=t + 2 * h / 3, s=s0 + 7 * Ks_1 / 27 + 10 * Ks_2 / 27 + Ks_4 / 27,
                     i=i0 + 7 * Ki_1 / 27 + 10 * Ki_2 / 27 + Ki_4 / 27,
                     r=r0 + 7 * Kr_1 / 27 + 10 * Kr_2 / 27 + Kr_4 / 27,
                     d=d0 + 7 * Kd_1 / 27 + 10 * Kd_2 / 27 + Kd_4 / 27, beta=beta, gamma=gamma, mu=mu)
    Kr_5 = drdt_func(t=t + 2 * h / 3, s=s0 + 7 * Ks_1 / 27 + 10 * Ks_2 / 27 + Ks_4 / 27,
                     i=i0 + 7 * Ki_1 / 27 + 10 * Ki_2 / 27 + Ki_4 / 27,
                     r=r0 + 7 * Kr_1 / 27 + 10 * Kr_2 / 27 + Kr_4 / 27,
                     d=d0 + 7 * Kd_1 / 27 + 10 * Kd_2 / 27 + Kd_4 / 27, beta=beta, gamma=gamma, mu=mu)
    Kd_5 = dddt_func(t=t + 2 * h / 3, s=s0 + 7 * Ks_1 / 27 + 10 * Ks_2 / 27 + Ks_4 / 27,
                     i=i0 + 7 * Ki_1 / 27 + 10 * Ki_2 / 27 + Ki_4 / 27,
                     r=r0 + 7 * Kr_1 / 27 + 10 * Kr_2 / 27 + Kr_4 / 27,
                     d=d0 + 7 * Kd_1 / 27 + 10 * Kd_2 / 27 + Kd_4 / 27, beta=beta, gamma=gamma, mu=mu)

    Ks_6 = dsdt_func(t=t + h / 5, s=s0 + (28 * Ks_1 - 125 * Ks_2 + 546*Ks_3 + 54*Ks_4 - 378*Ks_5) / 625,
                     i=i0 + (28 * Ki_1 - 125 * Ki_2 + 546 * Ki_3 + 54 * Ki_4 - 378 * Ki_5) / 625,
                     r=r0 + (28 * Kr_1 - 125 * Kr_2 + 546 * Kr_3 + 54 * Kr_4 - 378 * Kr_5) / 625,
                     d=d0 + (28 * Kd_1 - 125 * Kd_2 + 546 * Kd_3 + 54 * Kd_4 - 378 * Kd_5) / 625,
                     beta=beta, gamma=gamma, mu=mu)
    Ki_6 = didt_func(t=t + h / 5, s=s0 + (28 * Ks_1 - 125 * Ks_2 + 546 * Ks_3 + 54 * Ks_4 - 378 * Ks_5) / 625,
                     i=i0 + (28 * Ki_1 - 125 * Ki_2 + 546 * Ki_3 + 54 * Ki_4 - 378 * Ki_5) / 625,
                     r=r0 + (28 * Kr_1 - 125 * Kr_2 + 546 * Kr_3 + 54 * Kr_4 - 378 * Kr_5) / 625,
                     d=d0 + (28 * Kd_1 - 125 * Kd_2 + 546 * Kd_3 + 54 * Kd_4 - 378 * Kd_5) / 625,
                     beta=beta, gamma=gamma, mu=mu)

    Kr_6 = drdt_func(t=t + h / 5, s=s0 + (28 * Ks_1 - 125 * Ks_2 + 546 * Ks_3 + 54 * Ks_4 - 378 * Ks_5) / 625,
                     i=i0 + (28 * Ki_1 - 125 * Ki_2 + 546 * Ki_3 + 54 * Ki_4 - 378 * Ki_5) / 625,
                     r=r0 + (28 * Kr_1 - 125 * Kr_2 + 546 * Kr_3 + 54 * Kr_4 - 378 * Kr_5) / 625,
                     d=d0 + (28 * Kd_1 - 125 * Kd_2 + 546 * Kd_3 + 54 * Kd_4 - 378 * Kd_5) / 625,
                     beta=beta, gamma=gamma, mu=mu)

    Kd_6 = dddt_func(t=t + h / 5, s=s0 + (28 * Ks_1 - 125 * Ks_2 + 546 * Ks_3 + 54 * Ks_4 - 378 * Ks_5) / 625,
                     i=i0 + (28 * Ki_1 - 125 * Ki_2 + 546 * Ki_3 + 54 * Ki_4 - 378 * Ki_5) / 625,
                     r=r0 + (28 * Kr_1 - 125 * Kr_2 + 546 * Kr_3 + 54 * Kr_4 - 378 * Kr_5) / 625,
                     d=d0 + (28 * Kd_1 - 125 * Kd_2 + 546 * Kd_3 + 54 * Kd_4 - 378 * Kd_5) / 625,
                     beta=beta, gamma=gamma, mu=mu)

    s = s0 + (Ks_1 / 24 + 5 * Ks_4 / 48 + 27 * Ks_5 / 56 + 125 * Ks_6 / 336) * h
    i = i0 + (Ki_1 / 24 + 5 * Ki_4 / 48 + 27 * Ki_5 / 56 + 125 * Ki_6 / 336) * h
    r = r0 + (Kr_1 / 24 + 5 * Kr_4 / 48 + 27 * Kr_5 / 56 + 125 * Kr_6 / 336) * h
    d = d0 + (Kd_1 / 24 + 5 * Kd_4 / 48 + 27 * Kd_5 / 56 + 125 * Kd_6 / 336) * h

    return s, i, r, d

# --------------多步预测矫正方法--------------
def X_hamming(t = None, s0 = None, i0 = None, r0 = None, d0 = None,
             s_3=None, i_3=None, r_3=None, d_3=None,
             s_2=None, i_2=None, r_2=None, d_2=None,
             s_1 = None, i_1 = None, r_1 = None, d_1 = None,
             h=None, beta=None, gamma=None, mu=None,
             beta_1=None, gamma_1=None, mu_1=None,
             beta_2=None, gamma_2=None, mu_2=None,
             Beta_1 = None, Gamma_1 = None, Mu_1 = None):
    Sp1, Ip1, Rp1, Dp1 = milne4(t = t, s0 = s0, i0 = i0, r0 = r0, d0 = d0,
                                s_1 = s_1, i_1 = i_1, r_1 = r_1, d_1 = d_1,
                                s_2 = s_2, i_2 = i_2, r_2 = r_2, d_2 = d_2,
                                s_3 = s_3, i_3 = i_3, r_3 = r_3, d_3 = d_3,
                                h = h, beta = beta, gamma = gamma, mu = mu,
                                beta_1=beta_1, gamma_1= gamma_1, mu_1 = mu_1,
                                beta_2= beta_2, gamma_2= gamma_2, mu_2= mu_2,
                                )
    s = (9 * s0 - s_2) / 8 + 3 * h * (dsdt_func(t=t + h, s=Sp1, i=Ip1, r = Rp1, d = Dp1, beta = Beta_1, gamma = Gamma_1, mu = Mu_1)
                                      + 2 * dsdt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu) -
                                      dsdt_func(t=t - h, s=s_1, i=i_1, r=r_1, d=d_1, beta=beta_1, gamma=gamma_1, mu=mu_1))/8
    i = (9 * i0 - i_2) / 8 + 3 * h * (didt_func(t=t + h, s=Sp1, i=Ip1, r = Rp1, d = Dp1, beta = Beta_1, gamma = Gamma_1, mu = Mu_1)+
                                      2*didt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu) -
                                      didt_func(t=t - h, s=s_1, i=i_1, r=r_1, d=d_1, beta=beta_1, gamma=gamma_1, mu=mu_1))/8
    r = (9 * r0 - r_2) / 8 + 3 * h * (drdt_func(t=t + h, s=Sp1, i=Ip1, r = Rp1, d = Dp1, beta = Beta_1, gamma = Gamma_1, mu = Mu_1)+
                                      2*drdt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu) -
                                      drdt_func(t=t - h, s=s_1, i=i_1, r=r_1, d=d_1, beta=beta_1, gamma=gamma_1, mu=mu_1))/8
    d = (9 * d0 - d_2) / 8 + 3 * h * (dddt_func(t=t + h, s=Sp1, i=Ip1, r = Rp1, d = Dp1, beta = Beta_1, gamma = Gamma_1, mu = Mu_1)+
                                      2*dddt_func(t=t, s=s0, i=i0, r=r0, d=d0, beta=beta, gamma=gamma, mu=mu) -
                                      dddt_func(t=t - h, s=s_1, i=i_1, r=r_1, d=d_1, beta=beta_1, gamma=gamma_1, mu=mu_1))/8

    return s, i, r, d
def test_RK4_SIRD():
    n = 100
    t_temp = np.arange(1, n)
    t_arr = np.concatenate([[0], t_temp], axis=-1)
    s_init = 1000
    i_init = 500
    r_init = 2
    d_init = 1
    s_list = []
    i_list = []
    r_list = []
    d_list = []
    beta = 0.075
    gamma = 0.01
    mu = 0.0025
    # s_list.append(s_init)
    # i_list.append(i_init)
    # r_list.append(r_init)
    # d_list.append(d_list)
    for i in range(n):
        # temp = t_arr[i]
        s, i, r, d = SIRD_RK4(t=t_arr[i], s0=s_init, i0=i_init, r0=r_init, d0=d_init,
                              h=1.0, beta=beta, gamma=gamma, mu=mu)
        s_init = s
        i_init = i
        r_init = r
        d_init = d
        s_list.append(s)
        i_list.append(i)
        r_list.append(r)
        d_list.append(d)

    print('sshshsshkda')

    ax = plt.gca()
    ax.plot(t_arr, s_list, 'b-.', label='s')
    ax.plot(t_arr, i_list, 'r-*', label='i')
    ax.plot(t_arr, r_list, 'k:', label='r')
    ax.plot(t_arr, d_list, 'c--', label='d')
    # box = ax.get_position()
    # ax.set_position([box.x0, box.y0, box.width, box.height * 0.8])
    ax.legend(loc='right', bbox_to_anchor=(0.9, 1.05), ncol=4, fontsize=12)
    ax.set_xlabel('t', fontsize=14)
    ax.set_ylabel('s', fontsize=14)

    plt.show()


if __name__ == '__main__':
    test_RK4_SIRD()