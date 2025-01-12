import math
import os
import random

from typing import Union
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.io as sio
import torch
import torch.nn as nn
from tqdm.autonotebook import tqdm, trange

from deepdelineator.model import DeepDelineator

WEIGHS_PATH = os.path.join(os.path.dirname(__file__), "weights")

model_to_file = {
    "U_NET": os.path.join(WEIGHS_PATH, "U_NET.pt"),
    "TCN": os.path.join(WEIGHS_PATH, "TCN.pt"),
    "U_TCN": os.path.join(WEIGHS_PATH, "U_TCN.pt"),
    "U_GRU": os.path.join(WEIGHS_PATH, "U_GRU.pt"),
}


##############################################
# UTILS
##############################################


# To create and load pretrained models.
def load_delineator(model_type:str='U_NET', device: Union[torch.device, str]='cuda') -> DeepDelineator:
    # Validate model type
    if model_type not in model_to_file:
        valid_types = ", ".join(model_to_file.keys())
        raise ValueError(
            f"Invalid model type '{model_type}'. Supported types are: {valid_types}"
        )
    # Get checkpoint path
    path = model_to_file[model_type]
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Checkpoint file not found at: {path}")
    # Determine map location
    map_location = torch.device("cuda" if torch.cuda.is_available() else "cpu") if device != "cpu" else "cpu"
    # Load model
    checkpoint = torch.load(path, map_location=map_location)
    args = checkpoint["args"]
    #update device key
    args["device"] = map_location
    # Model
    model = DeepDelineator(args).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
    model.scheduler.load_state_dict(checkpoint["scheduler_state_dict"])
    model.history = checkpoint["history"]
    model.epochs = checkpoint["epoch"]
    model.best_valid_loss = checkpoint["best_valid_loss"]
    return model


# To load .mat files
def loadmat(filename):
    """
    this function should be called instead of direct spio.loadmat
    as it cures the problem of not properly recovering python dictionaries
    from mat files. It calls the function check keys to cure all entries
    which are still mat-objects
    """

    def _check_keys(d):
        """
        checks if entries in dictionary are mat-objects. If yes
        todict is called to change them to nested dictionaries
        """
        for key in d:
            if isinstance(d[key], sio.matlab.mio5_params.mat_struct):
                d[key] = _todict(d[key])
        return d

    def _todict(matobj):
        """
        A recursive function which constructs from matobjects nested dictionaries
        """
        d = {}
        for strg in matobj._fieldnames:
            elem = matobj.__dict__[strg]
            if isinstance(elem, sio.matlab.mio5_params.mat_struct):
                d[strg] = _todict(elem)
            elif isinstance(elem, np.ndarray):
                d[strg] = _tolist(elem)
            else:
                d[strg] = elem
        return d

    def _tolist(ndarray):
        """
        A recursive function which constructs lists from cellarrays
        (which are loaded as numpy ndarrays), recursing into the elements
        if they contain matobjects.
        """
        elem_list = []
        for sub_elem in ndarray:
            if isinstance(sub_elem, sio.matlab.mio5_params.mat_struct):
                elem_list.append(_todict(sub_elem))
            elif isinstance(sub_elem, np.ndarray):
                elem_list.append(_tolist(sub_elem))
            else:
                elem_list.append(sub_elem)
        return elem_list

    data = sio.loadmat(filename, struct_as_record=False, squeeze_me=True)
    return _check_keys(data)


##############################################
# DATA AUGMENTATION
##############################################

def worker_init_fn(worker_id):
    torch_seed = torch.initial_seed()
    random.seed(torch_seed + worker_id)
    if torch_seed >= 2**30:  # make sure torch_seed + workder_id < 2**32
        torch_seed = torch_seed % 2**30
    np.random.seed(torch_seed + worker_id)

#######################################
# LearningRateFinder
#######################################

# Reference:
# https://gist.github.com/johschmidt42/e13b448302dac72b8eb5e9eb36278d94#file-lr_rate_finder-py


class LearningRateFinder:
    """
    Train a model using different learning rates within a range to find the optimal learning rate.
    """

    def __init__(self, model: nn.Module, criterion, optimizer, device):
        self.model = model
        self.criterion = criterion
        self.optimizer = optimizer
        self.loss_history = {}
        self._model_init = model.state_dict()
        self._opt_init = optimizer.state_dict()
        self.device = device

    def fit(
        self,
        data_loader: torch.utils.data.DataLoader,
        steps=100,
        min_lr=1e-7,
        max_lr=1,
        constant_increment=False,
    ):
        """
        Trains the model for number of steps using varied learning rate and store the statistics
        """
        self.loss_history = {}
        self.model.train()
        current_lr = min_lr
        steps_counter = 0
        epochs = math.ceil(steps / len(data_loader))

        progressbar = trange(epochs, desc="Progress")
        for epoch in progressbar:
            batch_iter = tqdm(
                enumerate(data_loader), "Training", total=len(data_loader), leave=False
            )

            for i, (x, y) in batch_iter:
                x, y = x.to(self.device), y.to(self.device)
                for param_group in self.optimizer.param_groups:
                    param_group["lr"] = current_lr
                self.optimizer.zero_grad()
                out = self.model(x)
                loss = self.criterion(out, y)
                loss.backward()
                self.optimizer.step()
                self.loss_history[current_lr] = loss.item()

                steps_counter += 1
                if steps_counter > steps:
                    break

                if constant_increment:
                    current_lr += (max_lr - min_lr) / steps
                else:
                    current_lr = current_lr * (max_lr / min_lr) ** (1 / steps)

    def plot(self, smoothing=True, clipping=True, smoothing_factor=0.1):
        """
        Shows loss vs learning rate(log scale) in a matplotlib plot
        """
        loss_data = pd.Series(list(self.loss_history.values()))
        lr_list = list(self.loss_history.keys())
        if smoothing:
            loss_data = loss_data.ewm(alpha=smoothing_factor).mean()
            loss_data = loss_data.divide(
                pd.Series(
                    [
                        1 - (1.0 - smoothing_factor) ** i
                        for i in range(1, loss_data.shape[0] + 1)
                    ]
                )
            )  # bias correction
        if clipping:
            loss_data = loss_data[10:-5]
            lr_list = lr_list[10:-5]
        plt.plot(lr_list, loss_data)
        plt.xscale("log")
        plt.title("Loss vs Learning rate")
        plt.xlabel("Learning rate (log scale)")
        plt.ylabel("Loss (exponential moving average)")
        plt.show()

    def reset(self):
        """
        Resets the model and optimizer to its initial state
        """
        self.model.load_state_dict(self._model_init)
        self.optimizer.load_state_dict(self._opt_init)
        print("Model and optimizer in initial state.")
