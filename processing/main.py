import mne as mne
import numpy as np

raw = mne.io.read_raw_bdf("./UnicornRawDataRecorder_17_11_2025_18_09_13.bdf").load_data()
# raw = mne.io.read_raw_bdf("./UnicornRecorder_17_11_2025_18_09_13.bdf").load_data()
# raw.info['bads'].append('EEG 3')

print(raw)

# raw.apply_function(lambda x: x * 1e-6)
# raw.drop_channels(['CNT', 'DT', 'Status'])
# raw.filter(1, 30)
# raw.notch_filter([50])

# raw.compute_psd().plot()
raw.plot(block=True, scalings="auto")
