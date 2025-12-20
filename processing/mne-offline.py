import mne as mne
import numpy as np
import pylsl as lsl
import matplotlib.pyplot as plt

raw = mne.io.read_raw_bdf("./UnicornRawDataRecorder_17_11_2025_18_09_13.bdf").load_data()
# raw = mne.io.read_raw_bdf("./UnicornRecorder_17_11_2025_18_09_13.bdf").load_data()
# raw.info['bads'].append('EEG 3')
raw.drop_channels(['CNT', 'DT', 'Status'])
raw.set_eeg_reference([])
raw.apply_function(lambda x: x * 1e-6)

iir_params = dict(order=4, ftype='butter')
raw.filter(3, 30, method='iir')
# raw.filter(3, 30, method='iir', phase='forward', pad='reflect_limited')

# raw.compute_psd().plot()
raw.plot(block=True, scalings=None)
