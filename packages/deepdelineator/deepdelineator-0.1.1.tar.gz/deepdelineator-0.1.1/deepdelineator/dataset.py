import math
import random

import numpy as np
import torch
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import Dataset


##############################################
# PredictDataset (Base Class)
##############################################
class PredictDataset(Dataset):
    def __init__(self, X, device):
        self.X = X
        self.scaler = MinMaxScaler()
        self.device = device

    def __getitem__(self, index):
        x = self.X[index]
        x = self.scaler.fit_transform(x)
        x = np.reshape(x, (1, np.shape(x)[0]))
        x = torch.from_numpy(x).float().to(self.device)
        return x

    def __len__(self):
        return len(self.X)


class CustomDataset(Dataset):
    """
    Custom Dataset used for training the model.

    """

    def __init__(
        self,
        X,
        pulse_list,
        Y,
        device,
        t_i,
        t,
        p_drop_max,
        noise_std,
        scale_std_max,
        noise_mean,
        len_signal,
        low_frec,
        high_frec,
        low_amp,
        high_amp,
        f_rs,
        k_low,
        k_high,
        sigmoid_low,
        sigmoid_high,
        sigmoid_i_f,
        scaler,
        colors,
    ):
        self.X = X
        self.pulse_list = pulse_list
        self.Y = Y
        self.device = device
        self.t_i = t_i
        self.t = t
        ################
        # TRANSFORMATIONS
        ################
        self.p_drop_max = p_drop_max
        # Noise
        self.noise_std = noise_std
        self.scale_std_max = scale_std_max
        self.noise_mean = noise_mean
        # Resp / sin
        self.Ns = len_signal  # sampling points
        self.low_frec = low_frec
        self.high_frec = high_frec
        self.low_amp = low_amp
        self.high_amp = high_amp
        self.f_rs = f_rs
        self.T = 1 / f_rs
        self.t0 = np.linspace(0, self.Ns * self.T, self.Ns)
        # Constant
        self.k_low = k_low
        self.k_high = k_high
        self.scaler = scaler
        # plot
        self.colors = colors
        # Sigmoid
        self.sigmoid_space = np.linspace(-sigmoid_i_f, sigmoid_i_f, len_signal)
        self.sigmoid_vec = 1 / (1 + np.exp(-self.sigmoid_space))
        self.sigmoid_low = sigmoid_low
        self.sigmoid_high = sigmoid_high

    ################################################################################
    def find_regions(self, value, a):
        # Create an array that is 1 where a is `value`, and pad each end with an extra 0.
        isvalue = np.concatenate(([0], np.equal(a, value).view(np.int8), [0]))
        absdiff = np.abs(np.diff(isvalue))
        # Runs start and end where absdiff is 1.
        ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
        return ranges

    def func_constant_artifact(self, x, i_init, i_end):
        scale_std = np.random.randint(1, self.scale_std_max)
        noise = np.random.normal(
            self.noise_mean, self.noise_std * scale_std, x[i_init:i_end].shape
        )
        constant = np.random.uniform(low=self.k_low, high=self.k_high, size=None)
        x[i_init:i_end] = constant + noise
        return x

    def func_linear_artifact(self, x, i_init, i_end):
        scale_std = np.random.randint(1, self.scale_std_max)
        noise = np.random.normal(
            self.noise_mean, self.noise_std * scale_std, x[i_init:i_end].shape
        )
        x[i_init:i_end] = np.linspace(x[i_init], x[i_end - 1], i_end - i_init) + noise
        return x

    def func_add_sin(self, x):
        # Numpy
        phase = np.random.uniform(0, 2 * math.pi, 1)
        frec = np.random.uniform(self.low_frec, self.high_frec, 1)
        amp = np.random.uniform(self.low_amp, self.high_amp, 1)
        resp = amp * np.sin(2 * np.pi * frec * self.t0 + phase)
        x = x + resp
        return x

    def func_sigmoid_artifact(self, x):
        magnitud = np.random.uniform(self.sigmoid_low, self.sigmoid_high)
        slope = 1 if random.random() < 0.5 else -1
        x = x + (magnitud * self.sigmoid_vec) * slope
        return x

    def func_apply_artifacts(self, x, regions, i_b, type_artifact):
        i_init = regions[i_b, 0]
        i_end = regions[i_b, 1]
        switcher = {0: self.func_constant_artifact, 1: self.func_linear_artifact}
        # Get the function from switcher dictionary
        func = switcher.get(type_artifact, lambda: "Invalid parameter")
        # Excecute
        x = func(x, i_init, i_end)
        return x

    def func_apply_baseline_artifacts(self, x, type_artifact):
        switcher = {1: self.func_sigmoid_artifact, 2: self.func_add_sin}
        # Get the function from switcher dictionary
        func = switcher.get(type_artifact, lambda: "Invalid parameter")
        # Excecute
        x = func(x)
        return x

    ################################################################################

    def __getitem__(self, index):
        x = self.X[index, 0, :].copy()
        y = self.Y[index, 0, :].copy()
        count_pulse = self.pulse_list[index][0]
        pulses = self.pulse_list[index][1]
        pulses_idx = np.arange(count_pulse)
        # Porcentaje de indices a conservar
        p_drop = np.random.uniform(0, self.p_drop_max, 1)
        n_quit = int((p_drop) * count_pulse)
        # Elijo pulsos al azar
        quit_pulses = np.random.choice(pulses_idx, n_quit, replace=False)
        for i_q in quit_pulses:
            y[pulses[i_q, 0] : pulses[i_q, 1]] = 0
        # fig, axs = plot_segments(x,y,self.colors)
        # plt.show()

        # Ranges of  'artifact' to generate
        regions = self.find_regions(0, y)
        # Apply Transforms / Artifacts
        for i_b in range(len(regions)):
            type_artifact = np.random.randint(0, 2)
            # print(type_artifact)
            x = self.func_apply_artifacts(x, regions, i_b, type_artifact)
        # Add baseline artifact to all the signal if =!0
        bs_artifact = np.random.randint(0, 3)
        if bs_artifact != 0:
            x = self.func_apply_baseline_artifacts(x, bs_artifact)

        #
        idx_roll = np.random.randint(0, self.t_i)
        x = x[idx_roll : idx_roll + self.t]
        y = y[idx_roll : idx_roll + self.t]
        # x = x[self.t_i:self.t_i+t]
        # y = y[self.t_i:self.t_i+t]

        noise = np.random.normal(self.noise_mean, self.noise_std, x.shape)
        x = x + noise
        x = self.scaler.fit_transform(x.reshape(-1, 1)).reshape(
            -1,
        )

        # fig, axs = plot_segments(x,y,self.colors)
        # plt.show()
        x = torch.from_numpy(x).float().to(self.device)
        y = torch.from_numpy(y).long().to(self.device)

        x = x.unsqueeze_(0)
        # y = y.unsqueeze_(0)
        return (x, y)

    def __len__(self):
        return len(self.X)
