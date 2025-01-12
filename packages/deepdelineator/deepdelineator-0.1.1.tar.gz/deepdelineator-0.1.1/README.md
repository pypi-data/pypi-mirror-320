# deepdelineator

The `deepdelineator` library can be used to detect characteristic points in arterial blood pressure waveforms using deep learning techniques to improve the accuracy of the detection. At the same time, regions with noise can be identified automatically. 

![detections](imgs/full_real_signal.jpeg)

## Installation
`pip install deepdelineator`

## Usage

```python
from deepdelineator.utils import load_delineator

delineator = load_delineator()
s_f = 500 # Sampling frecuency of the signals, adjust to your data
# Detection!
detections = model.pred_from_numpy(signal_list=list_of_abp_signals,s_f=s_f)
```

For more details, please refer to the `examples` folder.


# Citing
If you consider this work useful, please cite the following paper:

## A Delineator for Arterial Blood Pressure Waveform Analysis Based on a Deep Learning Technique


```
@INPROCEEDINGS{9630717,
  author={Aguirre, Nicolas and Grall-Maës, Edith and Cymberknop, Leandro J. and Armentano, Ricardo L.},
  booktitle={2021 43rd Annual International Conference of the IEEE Engineering in Medicine   Biology Society (EMBC)}, 
  title={A Delineator for Arterial Blood Pressure Waveform Analysis Based on a Deep Learning Technique}, 
  year={2021},
  volume={},
  number={},
  pages={56-59},
  doi={10.1109/EMBC46164.2021.9630717}}

```
