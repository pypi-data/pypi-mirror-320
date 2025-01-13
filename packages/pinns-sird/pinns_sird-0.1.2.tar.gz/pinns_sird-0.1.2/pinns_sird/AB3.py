"""
@author: LXA
 Date: 2022 年 9 月 10 日
"""
import os
import sys
import torch
import numpy as np
import matplotlib
import platform
import shutil
import pandas as pd
import math

from .AB3_solveSIRD import solve_SIRD


if __name__ == "__main__":
    R = {}
    R['gpuNo'] = 0
    if platform.system() == 'Windows':
        os.environ["CDUA_VISIBLE_DEVICES"] = "%s" % (R['gpuNo'])
    else:
        print('-------------------------------------- linux -----------------------------------------------')
        # Linux终端没有GUI, 需要添加如下代码，而且必须添加在 import matplotlib.pyplot 之前，否则无效。
        matplotlib.use('Agg')

    if torch.cuda.is_available():
        os.environ["CUDA_VISIBLE_DEVICES"] = "0,1,2,3"  # 设置当前使用的GPU设备仅为第 0,1,2,3 块GPU, 设备名称为'/gpu:0'
    else:
        os.environ["CUDA_VISIBLE_DEVICES"] = "1"

    # The path of saving files
    store_file = 'SIRD_AB3'
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(BASE_DIR)
    OUT_DIR = os.path.join(BASE_DIR, store_file)
    if not os.path.exists(OUT_DIR):
        print('---------------------- OUT_DIR ---------------------:', OUT_DIR)
        os.mkdir(OUT_DIR)

    R['seed'] = np.random.randint(1e5)
    seed_str = str(R['seed'])  # int 型转为字符串型
    FolderName = os.path.join(OUT_DIR, seed_str)  # 路径连接
    R['FolderName'] = FolderName
    if not os.path.exists(FolderName):
        print('--------------------- FolderName -----------------:', FolderName)
        os.mkdir(FolderName)

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  Copy and save this file to given path %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    if platform.system() == 'Windows':
        shutil.copy(__file__, '%s/%s' % (FolderName, os.path.basename(__file__)))
    else:
        shutil.copy(__file__, '%s/%s' % (FolderName, os.path.basename(__file__)))

    # if the value of step_stop_flag is not 0, it will activate stop condition of step to kill program
    # step_stop_flag = input('please input an  integer number to activate step-stop----0:no---!0:yes--:')
    # R['activate_stop'] = int(step_stop_flag)
    R['activate_stop'] = int(0)
    # if the value of step_stop_flag is not 0, it will activate stop condition of step to kill program
    R['max_epoch'] = 15000
    # R['max_epoch'] = 20000
    # R['max_epoch'] = 200000
    if 0 != R['activate_stop']:
        epoch_stop = input('please input a stop epoch:')
        R['max_epoch'] = int(epoch_stop)

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Setups of problem %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    R['input_dim'] = 1  # 输入维数，即问题的维数(几元问题)
    R['output_dim'] = 1  # 输出维数

    R['ODE_type'] = 'SIRD'
    R['equa_name'] = 'simulated_SIRD3'
    R['opt2AB3'] = 'AB3_iter'
    # R['opt2AB2'] = 'AB2_vector'

    # R['total_population'] = 3450000  # 总的“人口”数量
    R['total_population'] = 100000
    # R['normalize_population'] = 3450000                # 归一化时使用的“人口”数值
    R['normalize_population'] = 10000
    # R['normalize_population'] = 5000
    # R['normalize_population'] = 2000
    # R['normalize_population'] = 1000
    # R['normalize_population'] = 1

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Setup of DNN %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    filename = 'data/simulated_SIRD3.csv'
    temp_df = pd.read_csv(filename)
    Total_observations = len(temp_df)
    R['size2train'] = math.floor(Total_observations * (14 / 15))  # 训练集的大小
    R['batch_size2train'] = math.floor(Total_observations * (1 / 15))  # 训练数据的批大小
    # R['size2train'] = 280                               # 训练集的大小
    # R['batch_size2train'] = 30                        # 训练数据的批大小
    # R['batch_size2train'] = 80                        # 训练数据的批大小
    # R['batch_size2train'] = 280  # 训练数据的批大小
    R['batch_size2test'] = 10      # 训练数据的批大小
    # 修改批大小
    # R['opt2sample'] = 'random_sample'                 # 训练集的选取方式--随机采样
    # R['opt2sample'] = 'rand_sample_sort'              # 训练集的选取方式--随机采样后按时间排序
    R['opt2sample'] = 'windows_rand_sample'  # 训练集的选取方式--随机窗口采样(以随机点为基准，然后滑动窗口采样)

    # The types of loss function
    R['loss_type'] = 'L2_loss'
    # R['loss_type'] = 'lncosh_loss'
    # R['lambda2lncosh'] = 0.01
    R['lambda2lncosh'] = 0.05  # 这个因子效果很好
    # R['lambda2lncosh'] = 0.075
    # R['lambda2lncosh'] = 0.1
    # R['lambda2lncosh'] = 0.5
    # R['lambda2lncosh'] = 1.0
    # R['lambda2lncosh'] = 50.0

    # The options of optimizers, learning rate, the decay of learning rate and the model of training network
    R['optimizer_name'] = 'Adam'  # 优化器

    # R['learning_rate'] = 1e-2                          # 学习率

    R['learning_rate'] = 4e-3 # 学习率
    # 改为0.01
    # 0.005
    # R['learning_rate'] = 2e-4                          # 学习率

    R['train_model'] = 'union_training'

    # 正则化权重和偏置的模式
    R['regular_wb_model'] = 'L0'
    # R['regular_wb_model'] = 'L1'
    # R['regular_wb_model'] = 'L2'
    # R['penalty2weight_biases'] = 0.000                # Regularization parameter for weights
    R['penalty2weight_biases'] = 0.00001                # Regularization parameter for weights
    # R['penalty2weight_biases'] = 0.00005                # Regularization parameter for weights
    # R['penalty2weight_biases'] = 0.0001               # Regularization parameter for weights
    # R['penalty2weight_biases'] = 0.0005               # Regularization parameter for weights
    # R['penalty2weight_biases'] = 0.001                # Regularization parameter for weights
    # R['penalty2weight_biases'] = 0.0025               # Regularization parameter for weights

    # 边界的惩罚处理方式,以及边界的惩罚因子
    R['activate_penalty2pt_increase'] = 1
    # R['init_penalty2predict_true'] = 1000             # Regularization factor for the  prediction and true
    # R['init_penalty2predict_true'] = 100              # Regularization factor for the  prediction and true
    R['init_penalty2predict_true'] = 10                 # Regularization factor for the  prediction and true

    # &&&&&&& The option fo Network model, the setups of hidden-layers and the option of activation function &&&&&&&&&&&
    # R['model2NN'] = 'DNN'
    # R['model2NN'] = 'Scale_DNN'
    R['model2NN'] = 'Fourier_DNN'

    if R['model2NN'] == 'Fourier_DNN':
        R['hidden_layers'] = (40, 50, 25, 25, 10)
        # (70, ...)
    else:
        R['hidden_layers'] = (90, 50, 25, 25, 10)

    # R['name2act_in'] = 'relu'
    # R['name2act_in'] = 'leaky_relu'
    # R['name2act_in'] = 'elu'
    # R['name2act_in'] = 'gelu'
    # R['name2act_in'] = 'mgelu'
    R['name2act_in'] = 'tanh'
    # R['name2act_in'] = 'sin'
    # R['name2act_in'] = 'sinAddcos'
    # R['name2act_in'] = 's2relu'
    # 用tanh，sinAddcos结果太高频

    # R['name2act_hidden'] = 'relu'
    # R['name2act_hidden'] = 'tanh'
    # R['name2act_hidden']' = leaky_relu'
    # R['name2act_hidden'] = 'srelu'
    # R['name2act_hidden'] = 's2relu'
    # R['name2act_hidden'] = 'sin'
    R['name2act_hidden'] = 'sinAddcos'
    # try tanh
    # R['name2act_hidden'] = 'elu'

    # R['name2act_out'] = 'linear'
    R['name2act_out'] = 'sigmoid'
    # try relu

    # &&&&&&&&&&&&&&&&&&&&& some other factors for network &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
    R['freq'] = np.concatenate(([1], np.arange(1, 30 - 1)), axis=0)  # 网络的频率范围设置

    R['if_repeat_High_freq'] = False

    R['sfourier'] = 1.0
    R['use_gpu'] = False

    R['scale_modify2beta'] = 1.0
    R['scale_modify2gamma'] = 1.0
    R['scale_modify2mu'] = 1.0

    R['scheduler'] = 75

    R['weight_of_loss_s'] = 1
    R['weight_of_loss_i'] = 1
    R['weight_of_loss_r'] = 1
    R['weight_of_loss_d'] = 1
    R['weight_of_loss_WB'] = 0.0001
    solve_SIRD(R)


def run_sird(data_path):
    """
    Run the SIRD model with the provided data path.

    Args:
        data_path (str): Path to the CSV file containing the data.
    """
    import os
    import torch
    import numpy as np
    import pandas as pd
    import math
    from .AB3_solveSIRD import solve_SIRD

    R = {}
    R['gpuNo'] = 0
    if torch.cuda.is_available():
        os.environ["CUDA_VISIBLE_DEVICES"] = "0,1,2,3"
    else:
        os.environ["CUDA_VISIBLE_DEVICES"] = "1"

    R['seed'] = np.random.randint(1e5)
    R['FolderName'] = os.path.join('SIRD_AB3', str(R['seed']))
    os.makedirs(R['FolderName'], exist_ok=True)

    # Read data and set parameters
    temp_df = pd.read_csv(data_path)
    Total_observations = len(temp_df)

    R['activate_stop'] = int(0)
    R['max_epoch'] = 15000
    R['input_dim'] = 1 # 输入维数，即问题的维数(几元问题)
    R['output_dim'] = 1 # 输出维数
    R['ODE_type'] = 'SIRD'
    R['equa_name'] = 'simulated_SIRD3'
    R['opt2AB3'] = 'AB3_iter'
    R['total_population'] = 100000
    R['normalize_population'] = 10000
    R['size2train'] = math.floor(Total_observations * (14 / 15)) # 训练集的大小
    R['batch_size2train'] = math.floor(Total_observations * (1 / 15)) # 训练数据的批大小
    R['batch_size2test'] = 10 # 训练数据的批大小
    R['opt2sample'] = 'windows_rand_sample' # 训练集的选取方式--随机窗口采样(以随机点为基准，然后滑动窗口采样)
    R['lambda2lncosh'] = 0.05 # 这个因子效果很好
    R['loss_type'] = 'L2_loss'
    R['optimizer_name'] = 'Adam' # 优化器
    R['learning_rate'] = 4e-3 # 学习率
    R['train_model'] = 'union_training'
    R['regular_wb_model'] = 'L0'
    R['penalty2weight_biases'] = 0.00001
    R['activate_penalty2pt_increase'] = 1
    R['init_penalty2predict_true'] = 10
    R['model2NN'] = 'Fourier_DNN'

    if R['model2NN'] == 'Fourier_DNN':
        R['hidden_layers'] = (40, 50, 25, 25, 10)
        # (70, ...)
    else:
        R['hidden_layers'] = (90, 50, 25, 25, 10)
    R['name2act_in'] = 'tanh'
    R['name2act_hidden'] = 'sinAddcos'
    R['name2act_out'] = 'sigmoid'
    R['freq'] = np.concatenate(([1], np.arange(1, 30 - 1)), axis=0) # 网络的频率范围设置
    R['if_repeat_High_freq'] = False
    R['sfourier'] = 1.0
    R['use_gpu'] = False
    R['scale_modify2beta'] = 1.0
    R['scale_modify2gamma'] = 1.0
    R['scale_modify2mu'] = 1.0
    R['scheduler'] = 75
    R['weight_of_loss_s'] = 1
    R['weight_of_loss_i'] = 1
    R['weight_of_loss_r'] = 1
    R['weight_of_loss_d'] = 1
    R['weight_of_loss_WB'] = 0.0001

    solve_SIRD(R)


import pandas as pd
import sys

if sys.version_info >= (3, 7):  # For Python 3.7 and above
    from importlib import resources

    def load_demo_data():
        """
        Load the demo data using `importlib.resources` (Python 3.7+).
        """
        with resources.open_text('pinns_sird.data', 'simulated_SIRD3.csv') as f:
            demo_data = pd.read_csv(f)
        return demo_data
else:  # For Python versions below 3.7
    import pkg_resources

    def load_demo_data():
        """
        Load the demo data using `pkg_resources` (Python < 3.7).
        """
        data_path = pkg_resources.resource_filename('pinns_sird.data', 'simulated_SIRD3.csv')
        demo_data = pd.read_csv(data_path)
        return demo_data