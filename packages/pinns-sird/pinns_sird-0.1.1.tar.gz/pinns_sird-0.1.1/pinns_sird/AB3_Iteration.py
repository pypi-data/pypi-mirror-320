import torch
import torch.nn as tn

from . import DNN_base
from .Numeric_Methods import adams_bashforth3 as AB3_SIRD



class AB3DNN_3(tn.Module):
    def __init__(self, input_dim=1, out_dim=3, hidden_layer=None, Model_name='DNN', name2actIn='relu',
                 name2actHidden='relu', name2actOut='linear', opt2regular_WB='L2', type2numeric='float32',
                 factor2freq=None, sFourier=1.0, repeat_highFreq=True, use_gpu=False, No2GPU=0):
        super(AB3DNN_3, self).__init__()
        if 'DNN' == str.upper(Model_name):
            self.BetaNN = DNN_base.Pure_DenseNet(
                indim=input_dim, outdim=out_dim, hidden_units=hidden_layer, name2Model=Model_name,
                actName2in=name2actIn, actName=name2actHidden, actName2out=name2actOut, scope2W='Ws2Beta',
                scope2B='Bs2Beta', type2float=type2numeric)
            self.GammaNN = DNN_base.Pure_DenseNet(
                indim=input_dim, outdim=out_dim, hidden_units=hidden_layer, name2Model=Model_name,
                actName2in=name2actIn, actName=name2actHidden, actName2out=name2actOut, scope2W='Ws2Gamma',
                scope2B='Bs2Gamma', type2float=type2numeric)
            self.MuNN = DNN_base.Pure_DenseNet(
                indim=input_dim, outdim=out_dim, hidden_units=hidden_layer, name2Model=Model_name,
                actName2in=name2actIn, actName=name2actHidden, actName2out=name2actOut, scope2W='Ws2Mu',
                scope2B='Bs2Mu', type2float=type2numeric)
        elif 'SCALE_DNN' == str.upper(Model_name) or 'DNN_SCALE' == str.upper(Model_name):
            self.BetaNN = DNN_base.Dense_ScaleNet(
                indim=input_dim, outdim=out_dim, hidden_units=hidden_layer, name2Model=Model_name,
                actName2in=name2actIn, actName=name2actHidden, actName2out=name2actOut, scope2W='Ws2Beta',
                scope2B='Bs2Beta', repeat_Highfreq=repeat_highFreq, type2float=type2numeric, to_gpu=use_gpu,
                gpu_no=No2GPU)
            self.GammaNN = DNN_base.Dense_ScaleNet(
                indim=input_dim, outdim=out_dim, hidden_units=hidden_layer, name2Model=Model_name,
                actName2in=name2actIn, actName=name2actHidden, actName2out=name2actOut, scope2W='Ws2Gamma',
                scope2B='Bs2Gamma', repeat_Highfreq=repeat_highFreq, type2float=type2numeric, to_gpu=use_gpu,
                gpu_no=No2GPU)
            self.MuNN = DNN_base.Dense_ScaleNet(
                indim=input_dim, outdim=out_dim, hidden_units=hidden_layer, name2Model=Model_name,
                actName2in=name2actIn, actName=name2actHidden, actName2out=name2actOut, scope2W='Ws2Mu',
                scope2B='Bs2Mu', repeat_Highfreq=repeat_highFreq, type2float=type2numeric, to_gpu=use_gpu,
                gpu_no=No2GPU)
        elif 'FOURIER_DNN' == str.upper(Model_name) or 'DNN_FOURIERBASE' == str.upper(Model_name):
            self.BetaNN = DNN_base.Dense_FourierNet(
                indim=input_dim, outdim=out_dim, hidden_units=hidden_layer, name2Model=Model_name,
                actName2in=name2actIn, actName=name2actHidden, actName2out=name2actOut, scope2W='Ws2Beta',
                scope2B='Bs2Beta', repeat_Highfreq=repeat_highFreq, type2float=type2numeric, to_gpu=use_gpu,
                gpu_no=No2GPU)
            self.GammaNN = DNN_base.Dense_FourierNet(
                indim=input_dim, outdim=out_dim, hidden_units=hidden_layer, name2Model=Model_name,
                actName2in=name2actIn, actName=name2actHidden, actName2out=name2actOut, scope2W='Ws2Gamma',
                scope2B='Bs2Gamma', repeat_Highfreq=repeat_highFreq, type2float=type2numeric, to_gpu=use_gpu,
                gpu_no=No2GPU)
            self.MuNN = DNN_base.Dense_FourierNet(
                indim=input_dim, outdim=out_dim, hidden_units=hidden_layer, name2Model=Model_name,
                actName2in=name2actIn, actName=name2actHidden, actName2out=name2actOut, scope2W='Ws2Mu',
                scope2B='Bs2Mu', repeat_Highfreq=repeat_highFreq, type2float=type2numeric, to_gpu=use_gpu,
                gpu_no=No2GPU)
        elif 'FOURIER_SUBDNN' == str.upper(Model_name) or 'SUBDNN_FOURIERBASE' == str.upper(Model_name):
            self.BetaNN = DNN_base.Fourier_SubNets3D(
                indim=input_dim, outdim=out_dim, hidden_units=hidden_layer, name2Model=Model_name,
                actName2in=name2actIn, actName=name2actHidden, actName2out=name2actOut, scope2W='Ws2Beta',
                scope2B='Bs2Beta', repeat_Highfreq=repeat_highFreq, type2float=type2numeric, to_gpu=use_gpu,
                gpu_no=No2GPU, num2subnets=len(factor2freq))
            self.GammaNN = DNN_base.Fourier_SubNets3D(
                indim=input_dim, outdim=out_dim, hidden_units=hidden_layer, name2Model=Model_name,
                actName2in=name2actIn, actName=name2actHidden, actName2out=name2actOut, scope2W='Ws2Gamma',
                scope2B='Bs2Gamma', repeat_Highfreq=repeat_highFreq, type2float=type2numeric, to_gpu=use_gpu,
                gpu_no=No2GPU, num2subnets=len(factor2freq))
            self.MuNN = DNN_base.Fourier_SubNets3D(
                indim=input_dim, outdim=out_dim, hidden_units=hidden_layer, name2Model=Model_name,
                actName2in=name2actIn, actName=name2actHidden, actName2out=name2actOut, scope2W='Ws2Mu',
                scope2B='Bs2Mu', repeat_Highfreq=repeat_highFreq, type2float=type2numeric, to_gpu=use_gpu,
                gpu_no=No2GPU, num2subnets=len(factor2freq))

        if type2numeric == 'float32':
            self.float_type = torch.float32
        elif type2numeric == 'float64':
            self.float_type = torch.float64
        elif type2numeric == 'float16':
            self.float_type = torch.float16

        if use_gpu:
            self.opt2device = 'cuda:' + str(No2GPU)
        else:
            self.opt2device = 'cpu'

        self.input_dim = input_dim
        self.factor2freq = factor2freq
        self.sFourier = sFourier
        self.opt2regular_WB = opt2regular_WB

    def AB3Iteration(self, t=None, input_size=100, s_obs=None, i_obs=None, r_obs=None, d_obs=None,
                     loss_type='ritz_loss', scale2lncosh=0.1, scale2beta=1.0, scale2gamma=0.1, scale2mu=0.05):
        assert (t is not None)
        assert (s_obs is not None)
        assert (i_obs is not None)
        assert (r_obs is not None)
        assert (d_obs is not None)

        shape2t = t.shape
        lenght2t_shape = len(shape2t)
        assert (lenght2t_shape == 2)
        assert (shape2t[-1] == 1)

        nn_beta = scale2beta * self.BetaNN(t, scale=self.factor2freq, sFourier=self.sFourier)
        nn_gamma = scale2gamma * self.GammaNN(t, scale=self.factor2freq, sFourier=self.sFourier)
        nn_mu = scale2mu * self.MuNN(t, scale=self.factor2freq, sFourier=self.sFourier)

        ParamsNN = torch.concat([nn_beta, nn_gamma, nn_mu], dim=-1)

        lsit2S_Pre, lsit2I_Pre, lsit2R_Pre, lsit2D_Pre = [], [], [], []
        for i in range(input_size-3):
            S_0 = s_obs[i + 2, 0]
            I_0 = i_obs[i + 2, 0]
            R_0 = r_obs[i + 2, 0]
            D_0 = d_obs[i + 2, 0]
            S_1 = s_obs[i + 1, 0]
            I_1 = i_obs[i + 1, 0]
            R_1 = r_obs[i + 1, 0]
            D_1 = d_obs[i + 1, 0]
            S_2 = s_obs[i, 0]
            I_2 =i_obs[i, 0]
            R_2 = r_obs[i, 0]
            D_2 = d_obs[i, 0]

            beta_param = nn_beta[i + 2, 0]
            gamma_param = nn_gamma[i + 2, 0]
            mu_param = nn_mu[i +2 , 0]

            beta1 = nn_beta[i + 1, 0]
            gamma1 = nn_gamma[i + 1, 0]
            mu1 = nn_mu[i + 1, 0]

            beta2 = nn_beta[i + 2, 0]
            gamma2 = nn_gamma[i + 2, 0]
            mu2 = nn_mu[i + 2, 0]

            s_update, i_update, r_update, d_update = AB3_SIRD(
                t=t[i], s0=S_0, i0=I_0, r0=R_0, d0=D_0,
                s_1 = S_1, i_1 = I_1, r_1 = R_1, d_1 = D_1,
                s_2 = S_2, i_2 = I_2, r_2 = R_2, d_2 = D_2, h=1.0,
                beta=beta_param, gamma=gamma_param, mu=mu_param,
                beta_1 = beta1, gamma_1 = gamma1, mu_1 = mu1,
                beta_2 = beta2, gamma_2 = gamma2, mu_2 = mu2)

            lsit2S_Pre.append(torch.reshape(s_update, shape=(1, 1)))
            lsit2I_Pre.append(torch.reshape(i_update, shape=(1, 1)))
            lsit2R_Pre.append(torch.reshape(r_update, shape=(1, 1)))
            lsit2D_Pre.append(torch.reshape(d_update, shape=(1, 1)))

        s_pre = torch.concat(lsit2S_Pre, dim=0)
        i_pre = torch.concat(lsit2I_Pre, dim=0)
        r_pre = torch.concat(lsit2R_Pre, dim=0)
        d_pre = torch.concat(lsit2D_Pre, dim=0)

        # ttt=torch.reshape(s_obs[1: input_size, 0], shape=[-1, 1])

        diff2S = torch.reshape(s_obs[3: input_size, 0], shape=[-1, 1]) - s_pre
        diff2I = torch.reshape(i_obs[3: input_size, 0], shape=[-1, 1]) - i_pre
        diff2R = torch.reshape(r_obs[3: input_size, 0], shape=[-1, 1]) - r_pre
        diff2D = torch.reshape(d_obs[3: input_size, 0], shape=[-1, 1]) - d_pre

        if str.lower(loss_type) == 'l2_loss':
            Loss2S = torch.mean(torch.square(diff2S))
            Loss2I = torch.mean(torch.square(diff2I))
            Loss2R = torch.mean(torch.square(diff2R))
            Loss2D = torch.mean(torch.square(diff2D))
        elif str.lower(loss_type) == 'lncosh_loss':
            Loss2S = (1/scale2lncosh)*torch.mean(torch.log(torch.cosh(scale2lncosh*diff2S)))
            Loss2I = (1/scale2lncosh)*torch.mean(torch.log(torch.cosh(scale2lncosh*diff2I)))
            Loss2R = (1/scale2lncosh)*torch.mean(torch.log(torch.cosh(scale2lncosh*diff2R)))
            Loss2D = (1/scale2lncosh)*torch.mean(torch.log(torch.cosh(scale2lncosh*diff2D)))

        return ParamsNN, Loss2S, Loss2I, Loss2R, Loss2D

    def get_regularSum2WB(self):
        sum_WB2Beta = self.BetaNN.get_regular_sum2WB(regular_model=self.opt2regular_WB)
        sum_WB2Gamma = self.GammaNN.get_regular_sum2WB(regular_model=self.opt2regular_WB)
        sum_WB2Mu = self.MuNN.get_regular_sum2WB(regular_model=self.opt2regular_WB)
        return sum_WB2Beta + sum_WB2Gamma + sum_WB2Mu
    def evaluate_AB3DNN(self, t=None, s_init=10.0, i_init=10.0, r_init=10.0, d_init=10.0,
                        s_1 = 10, i_1 = 10, r_1 = 10, d_1 = 10,
                        s_2 = None, i_2 = None, r_2 = None, d_2 = None,
                        size2predict=7,
                        scale2beta=1.0, scale2gamma=0.1, scale2mu=0.05):
        assert (t is not None)  # 该处的t是训练过程的时间， size2predict 是测试的规模大小
        shape2t = t.shape
        lenght2t_shape = len(shape2t)
        assert (lenght2t_shape == 2)
        assert (shape2t[-1] == 1)

        nn2beta = self.BetaNN(t, scale=self.factor2freq, sFourier=self.sFourier)
        nn2gamma = self.GammaNN(t, scale=self.factor2freq, sFourier=self.sFourier)
        nn2mu = self.MuNN(t, scale=self.factor2freq, sFourier=self.sFourier)
        ParamsNN = torch.concat([nn2beta, nn2gamma, nn2mu], dim=-1)

        s_base = s_init
        i_base = i_init
        r_base = r_init
        d_base = d_init
        S1 = s_1
        I1 = i_1
        R1 = r_1
        D1 = d_1
        S2 = s_2
        I2 = i_2
        R2 = r_2
        D2 = d_2

        lsit2S_Pre, lsit2I_Pre, lsit2R_Pre, lsit2D_Pre = [], [], [], []

        for i in range(size2predict - 2):
            nn_beta = scale2beta*nn2beta[i + 2, 0]
            nn_gamma = scale2gamma*nn2gamma[i + 2, 0]
            nn_mu = scale2mu*nn2mu[i + 2, 0]

            beta1 = scale2beta * nn2beta[i + 1, 0]
            gamma1 = scale2gamma *nn2gamma[i + 1, 0]
            mu1 = scale2mu * nn2mu[i + 1, 0]

            beta2 = scale2beta * nn2beta[i, 0]
            gamma2 = scale2gamma * nn2gamma[i, 0]
            mu2 = scale2mu * nn2mu[i, 0]

            s_update, i_update, r_update, d_update = AB3_SIRD(
                t=t[i], s0=s_base, i0=i_base, r0=r_base, d0=d_base,
                s_1 = S1, i_1 = I1, r_1 = R1, d_1 = D1,
                s_2=S2, i_2 = I2, r_2 = R2, d_2 = D2,
                h=1.0,
                beta=nn_beta, gamma=nn_gamma, mu=nn_mu,
                beta_1 = beta1, gamma_1 = gamma1, mu_1 = mu1,
                beta_2=beta2, gamma_2= gamma2, mu_2=mu2
                )
            s_base = s_update
            i_base = i_update
            r_base = r_update
            d_base = d_update

            lsit2S_Pre.append(torch.reshape(s_update, shape=(1, 1)))
            lsit2I_Pre.append(torch.reshape(i_update, shape=(1, 1)))
            lsit2R_Pre.append(torch.reshape(r_update, shape=(1, 1)))
            lsit2D_Pre.append(torch.reshape(d_update, shape=(1, 1)))

        S_Pre = torch.concat(lsit2S_Pre, dim=0)
        I_Pre = torch.concat(lsit2I_Pre, dim=0)
        R_Pre = torch.concat(lsit2R_Pre, dim=0)
        D_Pre = torch.concat(lsit2D_Pre, dim=0)

        return ParamsNN, S_Pre, I_Pre, R_Pre, D_Pre
    def evaluate_AB3DNN_FixedParas(self, t=None, s_init=10.0, i_init=10.0, r_init=10.0, d_init=10.0,
                        s_1 = 10, i_1 = 10, r_1 = 10, d_1 = 10,
                        s_2 = None, i_2 = None, r_2 = None, d_2 = None, size2predict=7,
                                   opt2fixed_paras='last2train', mean2para=3, scale2beta=1.0, scale2gamma=0.1,
                                   scale2mu=0.05):
        assert (t is not None)
        shape2t = t.shape
        lenght2t_shape = len(shape2t)
        assert (lenght2t_shape == 2)
        assert (shape2t[-1] == 1)

        nn2beta = self.BetaNN(t, scale=self.factor2freq, sFourier=self.sFourier)
        nn2gamma = self.GammaNN(t, scale=self.factor2freq, sFourier=self.sFourier)
        nn2mu = self.MuNN(t, scale=self.factor2freq, sFourier=self.sFourier)
        ParamsNN = torch.concat([nn2beta, nn2gamma, nn2mu], dim=-1)

        # 训练过程中最后一天的参数作为固定参数
        if opt2fixed_paras == 'last2train':
            nn_beta = scale2beta*nn2beta[0, 0]
            nn_gamma = scale2gamma*nn2gamma[0, 0]
            nn_mu = scale2mu*nn2mu[0, 0]
        else:  # 训练过程中最后几天的参数的均值作为固定参数，如三天的参数均值作为固定参数
            nn_beta = scale2beta*torch.mean(nn2beta, dim=0)
            nn_gamma = scale2gamma*torch.mean(nn2gamma, dim=0)
            nn_mu = scale2mu*torch.mean(nn2mu, dim=0)

        s_base = s_init
        i_base = i_init
        r_base = r_init
        d_base = d_init
        S1 = s_1
        I1 = i_1
        R1 = r_1
        D1 =d_1
        S2 = s_2
        I2 = i_2
        R2 = r_2
        D2 = d_2


        lsit2S_Pre, lsit2I_Pre, lsit2R_Pre, lsit2D_Pre = [], [], [], []

        for i in range(size2predict - 2):
            s_update, i_update, r_update, d_update = AB3_SIRD(
                t=t + i, s0=s_base, i0=i_base, r0=r_base, d0=d_base,
                s_1 = S1, i_1 = I1, r_1 = R1, d_1 = D1,
                s_2=S2, i_2 = I2, r_2 = R2, d_2 = D2,
                h=1.0,
                beta=nn_beta, gamma=nn_gamma, mu=nn_mu,
                beta_1 = nn_beta, gamma_1 = nn_gamma, mu_1 = nn_mu,
                beta_2=nn_beta, gamma_2= nn_gamma, mu_2=nn_mu
                )
            s_base = s_update
            i_base = i_update
            r_base = r_update
            d_base = d_update

            lsit2S_Pre.append(torch.reshape(s_update, shape=(1, 1)))
            lsit2I_Pre.append(torch.reshape(i_update, shape=(1, 1)))
            lsit2R_Pre.append(torch.reshape(r_update, shape=(1, 1)))
            lsit2D_Pre.append(torch.reshape(d_update, shape=(1, 1)))

        S_Pre = torch.concat(lsit2S_Pre, dim=0)
        I_Pre = torch.concat(lsit2I_Pre, dim=0)
        R_Pre = torch.concat(lsit2R_Pre, dim=0)
        D_Pre = torch.concat(lsit2D_Pre, dim=0)

        return ParamsNN, S_Pre, I_Pre, R_Pre, D_Pre
