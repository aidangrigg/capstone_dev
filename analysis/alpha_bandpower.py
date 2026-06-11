from collections import defaultdict

import mne
import matplotlib.pyplot as plt
import numpy as np

import pyxdf

ALPHA_MIN = 8.0
ALPHA_MAX = 13.0

def compute(raw_filename):
    data, header = pyxdf.load_xdf(raw_filename)

    eeg_data = None

    for d in data:
        print(d["info"]["type"])
        if d["info"]["type"][0].upper() == "EEG":
            eeg_data = d

    assert(eeg_data is not None)

    info = mne.create_info(4, 250, ["eeg"] * 4)
    raw = mne.io.RawArray(eeg_data["time_series"].T, info)

    raw.apply_function(lambda x: x * 1e-6)

    iir_params = dict(order=4, ftype='butter')
    raw.filter(3, 30, method='iir')

    raw.drop_channels(['2', '3'])

    epochs = mne.make_fixed_length_epochs(
        raw,
        duration=30.0,
        overlap=0.0,
        preload=True,
        verbose=False
    )

    psd = epochs.compute_psd(
        method="welch",
        fmin=1.0,
        fmax=40.0,
        verbose=False
    )

    psd_data = psd.get_data()
    freqs = psd.freqs

    alpha_mask = (freqs >= ALPHA_MIN) & (freqs <= ALPHA_MAX)

    res = []

    for epoch_idx in range(psd_data.shape[0]):
        # PSD for this epoch
        epoch_psd = psd_data[epoch_idx]

        left_alpha_power = np.trapezoid(
            epoch_psd[0, alpha_mask],
            freqs[alpha_mask]
        )

        right_alpha_power = np.trapezoid(
            epoch_psd[1, alpha_mask],
            freqs[alpha_mask]
        )

        alpha_power = (
            left_alpha_power +
            right_alpha_power
        ) / 2.0

        res.append(alpha_power)

    return res


session1 = compute("./CapstoneData/sub-P002/ses-S002/eeg/sub-P002_ses-S002_task-EyesClosed EyesOpen_run-001_eeg.xdf")
session2 = compute("./CapstoneData/sub-P002/ses-S003/eeg/sub-P002_ses-S003_task-EyesOpenEyesClosed_run-001_eeg.xdf")

plt.style.use('ggplot')

eye_open = []
eye_closed = []

for i in range(4):
    if i % 2 == 0:
        eye_open.append(session1[i])
        eye_open.append(session2[i])
    else:
        eye_closed.append(session1[i])
        eye_closed.append(session2[i])

fig1, ax1 = plt.subplots()
# fig1.suptitle("Eyes opened vs eyes closed alpha power")

ax1.set_ylabel(r'Alpha Power ($\mu V^2$)')

y = [np.mean(eye_open) * 1e12, np.mean(eye_closed) * 1e12]

ax1.bar(['Eyes opened', 'Eyes closed'], y)

plt.savefig("./out/alpha_bandpower.png")

# plt.show()

