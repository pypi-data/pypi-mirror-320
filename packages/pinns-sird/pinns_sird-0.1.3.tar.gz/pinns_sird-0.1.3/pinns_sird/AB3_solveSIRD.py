import os
import itertools
import torch
import time

from . import logUtils
from . import dataUtils
from . import saveData
from . import plotData
from .AB3_Iteration import AB3DNN_3


def solve_SIRD(R):
    log_out_path = R['FolderName']        # 将路径从字典 R 中提取出来
    if not os.path.exists(log_out_path):  # 判断路径是否已经存在
        os.mkdir(log_out_path)            # 无 log_out_path 路径，创建一个 log_out_path 路径
    logfile_name = '%s_%s.txt' % ('log2train', R['name2act_hidden'])
    log_fileout = open(os.path.join(log_out_path, logfile_name), 'w')  # 在这个路径下创建并打开一个可写的 log_train.txt文件
    logUtils.dictionary_out2file2AB3(R, log_fileout)

    # 问题需要的设置
    trainSet_szie = R['size2train']          # 训练集大小,给定一个数据集，拆分训练集和测试集时，需要多大规模的训练集
    batchsize2train = R['batch_size2train']
    batchsize2test = R['batch_size2test']
    penalty2WB = R['weight_of_loss_WB']  # Regularization parameter for weights and biases
    init_lr = R['learning_rate']
    act_func = R['name2act_hidden']

    SIRDmodel = AB3DNN_3(input_dim=R['input_dim'], out_dim=R['output_dim'], hidden_layer=R['hidden_layers'],
                       Model_name=R['model2NN'], name2actIn=R['name2act_in'], name2actHidden=R['name2act_hidden'],
                       name2actOut=R['name2act_out'], opt2regular_WB=R['regular_wb_model'], type2numeric='float32',
                       factor2freq=R['freq'], sFourier=R['sfourier'], repeat_highFreq=R['if_repeat_High_freq'],
                       use_gpu=R['use_gpu'], No2GPU=R['gpuNo'])

    if True == R['use_gpu']:
        SIRDmodel = SIRDmodel.cuda(device='cuda:'+str(R['gpuNo']))

    params2Beta_Net = SIRDmodel.BetaNN.parameters()
    params2Gamma_Net = SIRDmodel.GammaNN.parameters()
    params2Mu_Net = SIRDmodel.MuNN.parameters()

    params2Net = itertools.chain(params2Beta_Net, params2Gamma_Net, params2Mu_Net)

    # 定义优化方法，并给定初始学习率
    # optimizer = torch.optim.SGD(params2Net, lr=init_lr)                     # SGD
    # optimizer = torch.optim.SGD(params2Net, lr=init_lr, momentum=0.8)       # momentum
    # optimizer = torch.optim.RMSprop(params2Net, lr=init_lr, alpha=0.95)     # RMSProp
    optimizer = torch.optim.Adam(params2Net, lr=init_lr)                      # Adam

    # 定义更新学习率的方法
    # scheduler = torch.optim.lr_scheduler.ExponentialLR(optimizer, gamma=0.99)
    # scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=lambda epoch: 1/(epoch+1))
    # scheduler = torch.optim.lr_scheduler.StepLR(optimizer, 25, gamma=0.99)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, R['scheduler'], gamma=0.975)
    # 每100(50, 75)步改为原97.5% Scheduler
    # scheduler = torch.optim.lr_scheduler.StepLR(optimizer, 25, gamma=0.975)


    filename = 'data/simulated_SIRD3.csv'

    # 根据文件读入数据，然后存放在 numpy 数组里面
    date, data2S, data2I, data2R, data2D = dataUtils.load_4csvData_cal_S(
        datafile=filename, total_population=R['total_population'])

    assert (trainSet_szie + batchsize2test <= len(data2I))
    if R['normalize_population'] == 1:
        # 不归一化数据
        train_date, train_data2s, train_data2i, train_data2r, train_data2d, test_date, test_data2s, test_data2i, \
        test_data2r, test_data2d = dataUtils.split_5csvData2train_test(
            date, data2S, data2I, data2R, data2D, size2train=trainSet_szie, normalFactor=1.0, to_torch=True,
            to_float=True, to_cuda=R['use_gpu'], gpu_no=R['gpuNo'], use_grad2x=True)
    elif (R['total_population'] != R['normalize_population']) and R['normalize_population'] != 1:
        # 归一化数据，使用的归一化数值小于总“人口”
        train_date, train_data2s, train_data2i, train_data2r, train_data2d, test_date, test_data2s, test_data2i, \
        test_data2r, test_data2d = dataUtils.split_5csvData2train_test(
            date, data2S, data2I, data2R, data2D, size2train=trainSet_szie, normalFactor=R['normalize_population'],
            to_torch=True, to_float=True, to_cuda=R['use_gpu'], gpu_no=R['gpuNo'], use_grad2x=True)
    elif (R['total_population'] == R['normalize_population']) and R['normalize_population'] != 1:
        # 归一化数据，使用总“人口”归一化数据
        train_date, train_data2s, train_data2i, train_data2r, train_data2d, test_date, test_data2s, test_data2i, \
        test_data2r, test_data2d = dataUtils.split_5csvData2train_test(
            date, data2S, data2I, data2R, data2D, size2train=trainSet_szie, normalFactor=R['total_population'],
            to_torch=True, to_float=True, to_cuda=R['use_gpu'], gpu_no=R['gpuNo'], use_grad2x=True)

    # 对于时间数据来说，验证模型的合理性，要用连续的时间数据验证.
    test_t_bach = dataUtils.sample_testDays_serially(test_date, batchsize2test, is_torch=True)

    # 由于将数据拆分为训练数据和测试数据时，进行了归一化处理，故这里不用归一化
    s_obs_test = dataUtils.sample_testData_serially(test_data2s[3: ], batchsize2test - 2, normalFactor=1.0, is_torch=True)
    i_obs_test = dataUtils.sample_testData_serially(test_data2i[3: ], batchsize2test - 2, normalFactor=1.0, is_torch=True)
    r_obs_test = dataUtils.sample_testData_serially(test_data2r[3: ], batchsize2test - 2, normalFactor=1.0, is_torch=True)
    d_obs_test = dataUtils.sample_testData_serially(test_data2d[3: ], batchsize2test - 2, normalFactor=1.0, is_torch=True)

    init2S_test = test_data2s[2]
    init2I_test = test_data2i[2]
    init2R_test = test_data2r[2]
    init2D_test = test_data2d[2]
    S_1test = test_data2s[1]
    I_1test = test_data2i[1]
    R_1test = test_data2r[1]
    D_1test = test_data2d[1]
    S_2test = test_data2s[0]
    I_2test = test_data2i[0]
    R_2test = test_data2r[0]
    D_2test = test_data2d[0]

    # 将训练集的最后一天和测试集的前n天连接起来，作为新的测试批大小
    last_train_ts = torch.reshape(train_date[trainSet_szie - 5:-1], shape=[-1, 1])
    last_train_t = torch.reshape(train_date[trainSet_szie - 1], shape=[1, 1])
    new_test_t_bach = torch.concat([last_train_t, torch.reshape(test_t_bach[0:-1, 0], shape=[-1, 1])], dim=0)

    t0 = time.time()
    loss_all, loss_s_all, loss_i_all, loss_r_all, loss_d_all = [], [], [], [], []  # 空列表, 使用 append() 添加元素
    test_epoch = []
    test_mse2s_all, test_mse2i_all, test_mse2r_all, test_mse2d_all = [], [], [], []
    test_rel2s_all, test_rel2i_all, test_rel2r_all, test_rel2d_all = [], [], [], []

    test_mse2s_Fix_all, test_mse2i_Fix_all, test_mse2r_Fix_all, test_mse2d_Fix_all = [], [], [], []
    test_rel2s_Fix_all, test_rel2i_Fix_all, test_rel2r_Fix_all, test_rel2d_Fix_all = [], [], [], []
    for epoch in range(R['max_epoch'] + 1):
        if batchsize2train == trainSet_szie:
            t_batch = torch.reshape(train_date, shape=[-1, 1])
            s_obs = torch.reshape(train_data2s, shape=[-1, 1])
            i_obs = torch.reshape(train_data2i, shape=[-1, 1])
            r_obs = torch.reshape(train_data2r, shape=[-1, 1])
            d_obs = torch.reshape(train_data2d, shape=[-1, 1])
        else:
            t_batch, s_obs, i_obs, r_obs, d_obs = \
                dataUtils.randSample_Normalize_5existData(
                    train_date, train_data2s, train_data2i, train_data2r, train_data2d, batchsize=batchsize2train,
                    normalFactor=1.0, sampling_opt=R['opt2sample'])

        params, loss2s, loss2i, loss2r, loss2d = SIRDmodel.AB3Iteration(
            t=t_batch, input_size=batchsize2train, s_obs=s_obs, i_obs=i_obs, r_obs=r_obs,
            d_obs=d_obs, loss_type=R['loss_type'], scale2lncosh=R['lambda2lncosh'], scale2beta=R['scale_modify2beta'],
            scale2gamma=R['scale_modify2gamma'], scale2mu=R['scale_modify2mu'])

        regularSum2WB = SIRDmodel.get_regularSum2WB()
        Paras_PWB = penalty2WB * regularSum2WB

        # loss = loss2s + loss2i + loss2r + loss2d + Paras_PWB

        # loss = loss2s + loss2i + 10*loss2r + 20*loss2d + Paras_PWB
        # loss = loss2s + loss2i + 5 * loss2r + 10 * loss2d + Paras_PWB
        loss = R['weight_of_loss_s'] * loss2s + R['weight_of_loss_i'] * loss2i + R['weight_of_loss_r'] * loss2r + \
               R['weight_of_loss_d'] * loss2d + Paras_PWB

        loss_s_all.append(loss2s.item())
        loss_i_all.append(loss2i.item())
        loss_r_all.append(loss2r.item())
        loss_d_all.append(loss2d.item())
        loss_all.append(loss.item())

        optimizer.zero_grad()             # 求导前先清零, 只要在下一次求导前清零即可
        loss.backward(retain_graph=True)  # 对loss关于Ws和Bs求偏导
        optimizer.step()                  # 更新参数Ws和Bs
        scheduler.step()

        if epoch % 2000 == 0:
            run_times = time.time() - t0
            tmp_lr = optimizer.param_groups[0]['lr']
            logUtils.print_training2OneNet(epoch, run_times, tmp_lr, Paras_PWB.item(), loss2s.item(), loss2i.item(),
                                           loss2r.item(), loss2d.item(), loss.item(), log_out=log_fileout)

            # ---------------------------   test network ----------------------------------------------
            test_epoch.append(epoch / 2000)
            paras_nn, S_predict, I_predict, R_predict, D_predict = SIRDmodel.evaluate_AB3DNN(
                t=new_test_t_bach,
                s_init=init2S_test, i_init=init2I_test, r_init=init2R_test, d_init=init2D_test,
                s_1 = S_1test, i_1 = I_1test, r_1 = R_1test, d_1 = D_1test,
                s_2 = S_2test, i_2 = I_2test, r_2 = R_2test, d_2 = D_2test,
                size2predict=batchsize2test, scale2beta=R['scale_modify2beta'], scale2gamma=R['scale_modify2gamma'],
                scale2mu=R['scale_modify2mu'])

            test_mse2S = torch.mean(torch.square(s_obs_test - S_predict))
            test_mse2I = torch.mean(torch.square(i_obs_test - I_predict))
            test_mse2R = torch.mean(torch.square(r_obs_test - R_predict))
            test_mse2D = torch.mean(torch.square(d_obs_test - D_predict))

            test_rel2S = test_mse2S / torch.mean(torch.square(s_obs_test))
            test_rel2I = test_mse2I / torch.mean(torch.square(i_obs_test))
            test_rel2R = test_mse2R / torch.mean(torch.square(r_obs_test))
            test_rel2D = test_mse2D / torch.mean(torch.square(d_obs_test))

            test_mse2s_all.append(test_mse2S.item())
            test_mse2i_all.append(test_mse2I.item())
            test_mse2r_all.append(test_mse2R.item())
            test_mse2d_all.append(test_mse2D.item())

            test_rel2s_all.append(test_rel2S.item())
            test_rel2i_all.append(test_rel2I.item())
            test_rel2r_all.append(test_rel2R.item())
            test_rel2d_all.append(test_rel2D.item())
            logUtils.print_test2OneNet(test_mse2S.item(), test_mse2I.item(), test_mse2R.item(), test_mse2D.item(),
                                       test_rel2S.item(), test_rel2I.item(), test_rel2R.item(), test_rel2D.item(),
                                       log_out=log_fileout)
            # print(last_train_t)
            fix_paras_nn, S_predict2fix, I_predict2fix, R_predict2fix, D_predict2fix = \
                SIRDmodel.evaluate_AB3DNN_FixedParas(t=last_train_t,
                                                     s_init=init2S_test, i_init=init2I_test,
                                                     r_init=init2R_test, d_init=init2D_test,
                                                     s_1=S_1test, i_1=I_1test, r_1=R_1test, d_1=D_1test,
                                                     s_2 = S_2test, i_2 = I_2test, r_2 = I_2test, d_2 = D_2test,
                                                     size2predict=batchsize2test,
                                                     opt2fixed_paras='last2train', scale2beta=R['scale_modify2beta'],
                                                     scale2gamma=R['scale_modify2gamma'], scale2mu=R['scale_modify2mu'])

            test_mse2S_fix = torch.mean(torch.square(s_obs_test - S_predict2fix))
            test_mse2I_fix = torch.mean(torch.square(i_obs_test - I_predict2fix))
            test_mse2R_fix = torch.mean(torch.square(r_obs_test - R_predict2fix))
            test_mse2D_fix = torch.mean(torch.square(d_obs_test - D_predict2fix))

            test_rel2S_fix = test_mse2S_fix / torch.mean(torch.square(s_obs_test))
            test_rel2I_fix = test_mse2I_fix / torch.mean(torch.square(i_obs_test))
            test_rel2R_fix = test_mse2R_fix / torch.mean(torch.square(r_obs_test))
            test_rel2D_fix = test_mse2D_fix / torch.mean(torch.square(d_obs_test))

            test_mse2s_Fix_all.append(test_mse2S_fix.item())
            test_mse2i_Fix_all.append(test_mse2I_fix.item())
            test_mse2r_Fix_all.append(test_mse2R_fix.item())
            test_mse2d_Fix_all.append(test_mse2D_fix.item())

            test_rel2s_Fix_all.append(test_rel2S_fix.item())
            test_rel2i_Fix_all.append(test_rel2I_fix.item())
            test_rel2r_Fix_all.append(test_rel2R_fix.item())
            test_rel2d_Fix_all.append(test_rel2D_fix.item())

            logUtils.print_testFix_paras2OneNet(test_mse2S_fix.item(), test_mse2I_fix.item(), test_mse2R_fix.item(),
                                                test_mse2D_fix.item(), test_rel2S_fix.item(), test_rel2I_fix.item(),
                                                test_rel2R_fix.item(), test_rel2D_fix.item(), log_out=log_fileout)

    datetensor = torch.tensor(date, dtype=torch.float32).view(-1, 1)
    BetaFin = R['scale_modify2beta']  * SIRDmodel.BetaNN(datetensor, scale=SIRDmodel.factor2freq).detach().numpy()
    MuFin = R['scale_modify2beta'] * SIRDmodel.MuNN(datetensor, scale=SIRDmodel.factor2freq).detach().numpy()
    GammaFin = R['scale_modify2beta'] * SIRDmodel.GammaNN(datetensor, scale=SIRDmodel.factor2freq).detach().numpy()
    saveData.save_SIRD_Paras2mat(BetaFin, GammaFin, MuFin, name2para1='Beta',
                                 name2para2='Gamma', name2para3='Mu', outPath=R['FolderName'])
    # ------------------- save the training results into mat file and plot them -------------------------
    saveData.save_SIRD_trainLoss2mat_no_N(loss_s_all, loss_i_all, loss_r_all, loss_d_all, actName=act_func,
                                          outPath=R['FolderName'])

    plotData.plotTrain_loss_1act_func(loss_s_all, lossType='loss2s', seedNo=R['seed'], outPath=R['FolderName'],
                                      yaxis_scale=True)
    plotData.plotTrain_loss_1act_func(loss_i_all, lossType='loss2i', seedNo=R['seed'], outPath=R['FolderName'],
                                      yaxis_scale=True)
    plotData.plotTrain_loss_1act_func(loss_r_all, lossType='loss2r', seedNo=R['seed'], outPath=R['FolderName'],
                                      yaxis_scale=True)
    plotData.plotTrain_loss_1act_func(loss_d_all, lossType='loss2d', seedNo=R['seed'], outPath=R['FolderName'],
                                      yaxis_scale=True)

    # ------------------- save the testing results into mat file and plot them -------------------------
    plotData.plotTest_MSE_REL(test_mse2s_all, test_rel2s_all, test_epoch, actName='S', seedNo=R['seed'],
                              outPath=R['FolderName'], xaxis_scale=False, yaxis_scale=True)
    plotData.plotTest_MSE_REL(test_mse2i_all, test_rel2i_all, test_epoch, actName='I', seedNo=R['seed'],
                              outPath=R['FolderName'], xaxis_scale=False, yaxis_scale=True)
    plotData.plotTest_MSE_REL(test_mse2r_all, test_rel2r_all, test_epoch, actName='R', seedNo=R['seed'],
                              outPath=R['FolderName'], xaxis_scale=False, yaxis_scale=True)
    plotData.plotTest_MSE_REL(test_mse2d_all, test_rel2d_all, test_epoch, actName='D', seedNo=R['seed'],
                              outPath=R['FolderName'], xaxis_scale=False, yaxis_scale=True)

    plotData.plotTest_MSE_REL(test_mse2s_Fix_all, test_rel2s_Fix_all, test_epoch, actName='S_Fix', seedNo=R['seed'],
                              outPath=R['FolderName'], xaxis_scale=False, yaxis_scale=True)
    plotData.plotTest_MSE_REL(test_mse2i_Fix_all, test_rel2i_Fix_all, test_epoch, actName='I_Fix', seedNo=R['seed'],
                              outPath=R['FolderName'], xaxis_scale=False, yaxis_scale=True)
    plotData.plotTest_MSE_REL(test_mse2r_Fix_all, test_rel2r_Fix_all, test_epoch, actName='R_Fix', seedNo=R['seed'],
                              outPath=R['FolderName'], xaxis_scale=False, yaxis_scale=True)
    plotData.plotTest_MSE_REL(test_mse2d_Fix_all, test_rel2d_Fix_all, test_epoch, actName='D_Fix', seedNo=R['seed'],
                              outPath=R['FolderName'], xaxis_scale=False, yaxis_scale=True)

    if True == R['use_gpu']:
        # print('********************** with gpu *****************************')
        test_t_bach_numpy = test_t_bach.cpu().detach().numpy()
        s_obs_test_numpy = s_obs_test.cpu().detach().numpy()
        i_obs_test_numpy = i_obs_test.cpu().detach().numpy()
        r_obs_test_numpy = r_obs_test.cpu().detach().numpy()
        d_obs_test_numpy = d_obs_test.cpu().detach().numpy()

        s_pre_test_numpy = S_predict.cpu().detach().numpy()
        i_pre_test_numpy = I_predict.cpu().detach().numpy()
        r_pre_test_numpy = R_predict.cpu().detach().numpy()
        d_pre_test_numpy = D_predict.cpu().detach().numpy()

        s_fix_test_numpy = S_predict2fix.cpu().detach().numpy()
        i_fix_test_numpy = I_predict2fix.cpu().detach().numpy()
        r_fix_test_numpy = R_predict2fix.cpu().detach().numpy()
        d_fix_test_numpy = D_predict2fix.cpu().detach().numpy()
    else:
        # print('********************* without gpu **********************')
        test_t_bach_numpy = test_t_bach.detach().numpy()

        s_obs_test_numpy = s_obs_test.detach().numpy()
        i_obs_test_numpy = i_obs_test.detach().numpy()
        r_obs_test_numpy = r_obs_test.detach().numpy()
        d_obs_test_numpy = d_obs_test.detach().numpy()

        s_pre_test_numpy = S_predict.detach().numpy()
        i_pre_test_numpy = I_predict.detach().numpy()
        r_pre_test_numpy = R_predict.detach().numpy()
        d_pre_test_numpy = D_predict.detach().numpy()

        s_fix_test_numpy = S_predict2fix.detach().numpy()
        i_fix_test_numpy = I_predict2fix.detach().numpy()
        r_fix_test_numpy = R_predict2fix.detach().numpy()
        d_fix_test_numpy = D_predict2fix.detach().numpy()
    test_t_bach_numpy = test_t_bach[2: ].cpu().detach().numpy()
    plotData.plot_3solus2SIRD_test(s_obs_test_numpy, s_pre_test_numpy, s_fix_test_numpy, exact_name='S_true',
                                   solu1_name='S_pre2time', solu2_name='S_pre2fix',  file_name='S_solu',
                                   coord_points=test_t_bach_numpy, outPath=R['FolderName'])
    plotData.plot_3solus2SIRD_test(i_obs_test_numpy, i_pre_test_numpy, i_fix_test_numpy, exact_name='I_true',
                                   solu1_name='I_pre2time', solu2_name='I_pre2fix', file_name='I_solu',
                                   coord_points=test_t_bach_numpy, outPath=R['FolderName'])
    plotData.plot_3solus2SIRD_test(r_obs_test_numpy, r_pre_test_numpy, r_fix_test_numpy, exact_name='R_true',
                                   solu1_name='R_pre2time', solu2_name='R_pre2fix', file_name='R_solu',
                                   coord_points=test_t_bach_numpy, outPath=R['FolderName'])
    plotData.plot_3solus2SIRD_test(d_obs_test_numpy, d_pre_test_numpy, d_fix_test_numpy, exact_name='D_true',
                                   solu1_name='D_pre2time', solu2_name='D_pre2fix', file_name='D_solu',
                                   coord_points=test_t_bach_numpy, outPath=R['FolderName'])


    S_predict_np = S_predict.detach().numpy()
    I_predict_np = I_predict.detach().numpy()
    R_predict_np = R_predict.detach().numpy()
    D_predict_np = D_predict.detach().numpy()
    saveData.save_SIRD_testSolus2mat(S_predict_np, I_predict_np, R_predict_np, D_predict_np, name2solus1='S_pre',
                                     name2solus2='I_pre', name2solus3='R_pre', name2solus4='D_pre',
                                     file_name='timeParas', outPath=R['FolderName'])

    S_predict2fix_np = S_predict2fix.detach().numpy()
    I_predict2fix_np = I_predict2fix.detach().numpy()
    R_predict2fix_np = R_predict2fix.detach().numpy()
    D_predict2fix_np = D_predict2fix.detach().numpy()
    saveData.save_SIRD_testSolus2mat(S_predict2fix_np, I_predict2fix_np, R_predict2fix_np, D_predict2fix_np, name2solus1='S_pre',
                                     name2solus2='I_pre', name2solus3='R_pre', name2solus4='D_pre',
                                     file_name='fixParas', outPath=R['FolderName'])
    paras_nn_np = paras_nn.detach().numpy()
    saveData.save_SIRD_testParas2mat(paras_nn_np[:, 0], paras_nn_np[:, 1], paras_nn_np[:, 2], name2para1='Beta',
                                     name2para2='Gamma', name2para3='Mu', outPath=R['FolderName'])