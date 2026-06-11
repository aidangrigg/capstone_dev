from collections import defaultdict

import mne
import matplotlib.pyplot as plt
import numpy as np

import pandas as pd

import pyxdf

ALPHA_MIN = 8.0
ALPHA_MAX = 13.0

THETA_MIN = 4.0
THETA_MAX = 8.0

annotations_map = {
    "instruction_2_start": "Baseline",
    "instruction_3_start": "FAA Training",
    "instruction_5_start": "Theta Training",
    "instruction_7_start": "FAA & Theta Training",
}

def compute(raw_filename):
    data, header = pyxdf.load_xdf(raw_filename)

    markers = None
    eeg_data = None

    for d in data:
        print(d["info"]["type"])
        if d["info"]["type"][0].upper() == "EEG":
            eeg_data = d
        elif d["info"]["type"][0] == "marker" and markers is None:
            markers = d

    assert(markers is not None and eeg_data is not None)

    first_ts = eeg_data["time_stamps"][0]

    annotations = mne.Annotations([], [], [], header["info"]["datetime"][0])

    onsets = markers["time_stamps"] - first_ts
    descriptions = [
        f"{annotations_map[item]}" if item in annotations_map else item for sub in markers["time_series"] for item in sub
    ]

    annotations.append(onsets, [0] * len(onsets), descriptions)

    info = mne.create_info(4, 250, ["eeg"] * 4)
    raw = mne.io.RawArray(eeg_data["time_series"].T, info)

    raw.set_eeg_reference([])

    raw.set_annotations(annotations)
    raw.apply_function(lambda x: x * 1e-6)

    iir_params = dict(order=4, ftype='butter')
    raw.filter(3, 30, method='iir')

    raw.drop_channels(['2', '3'])

    # raw.plot(block=True)

    faa_scores = defaultdict(list)
    theta_scores = defaultdict(list)

    prev_onset = 0.0
    end = raw.times[-1]

    for ann_idx, ann in enumerate(raw.annotations):

        block_name = ann["description"]

        onset = ann["onset"]
        duration = onset - prev_onset

        # Skip tiny blocks
        if duration <= 1.0:
            continue

        print(f"\nProcessing block: {block_name}")
        print(f"Onset: {onset:.2f}s")
        print(f"Duration: {duration:.2f}s")

        # ========================================================
        # Crop raw data to this block
        # ========================================================

        block_raw = raw.copy().crop(
            tmin=prev_onset,
            tmax=onset,
            include_tmax=False,
            verbose=False
        )

        # ========================================================
        # Create fixed-length epochs
        # ========================================================

        try:
            epochs = mne.make_fixed_length_epochs(
                block_raw,
                duration=2.0,
                overlap=0.0,
                preload=True,
                verbose=False
            )
        except:
            continue

        reject_criteria = dict(eeg=100e-6)
        flatten_criteria = dict(eeg=20e-6)
        # epochs.drop_bad(reject=reject_criteria)
        epochs.drop_bad(reject=reject_criteria, flat=flatten_criteria)

        print(f"Created {len(epochs)} epochs")

        if len(epochs) == 0:
            prev_onset = onset
            continue

        # ========================================================
        # Compute PSD
        # ========================================================

        psd = epochs.compute_psd(
            method="welch",
            fmin=1.0,
            fmax=40.0,
            verbose=False
        )

        psd_data = psd.get_data()
        freqs = psd.freqs

        # Shape:
        # (n_epochs, n_channels, n_freqs)

        print(f"PSD shape: {psd_data.shape}")

        # ========================================================
        # Find alpha band indices
        # ========================================================

        alpha_mask = (freqs >= ALPHA_MIN) & (freqs <= ALPHA_MAX)
        theta_mask = (freqs >= THETA_MIN) & (freqs <= THETA_MAX)

        # ========================================================
        # Find channel indices
        # ========================================================

        left_idx = psd.ch_names.index('0')
        right_idx = psd.ch_names.index('1')

        # ========================================================
        # Compute FAA for each epoch
        # ========================================================

        for epoch_idx in range(psd_data.shape[0]):

            # PSD for this epoch
            epoch_psd = psd_data[epoch_idx]

            # Alpha power
            left_alpha = np.trapezoid(
                epoch_psd[left_idx, alpha_mask],
                freqs[alpha_mask]
            )

            right_alpha = np.trapezoid(
                epoch_psd[right_idx, alpha_mask],
                freqs[alpha_mask]
            )

            # Prevent log(0)
            left_alpha = max(left_alpha, 1e-12)
            right_alpha = max(right_alpha, 1e-12)

            # FAA calculation
            faa = np.log(right_alpha) - np.log(left_alpha)

            faa_scores[block_name].append(faa)

            # ====================================================
            # Theta bandpower (average across F3 and F4)
            # ====================================================
            left_theta_power = np.trapezoid(
                epoch_psd[left_idx, theta_mask],
                freqs[theta_mask]
            )

            right_theta_power = np.trapezoid(
                epoch_psd[right_idx, theta_mask],
                freqs[theta_mask]
            )

            theta_power = (
                left_theta_power +
                right_theta_power
            ) / 2.0

            theta_power *= 1e12

            theta_scores[block_name].append(theta_power)

        # ========================================================
        # Store detailed results
        # ========================================================

        prev_onset = onset

    return faa_scores, theta_scores


filenames = [
    # "./CapstoneData/sub-P002/ses-S002/eeg/sub-P002_ses-S002_task-Default_run-002_eeg.xdf",
    # "./CapstoneData/sub-P002/ses-S003/eeg/sub-P002_ses-S003_task-Default_run-002_eeg.xdf",
    # "./CapstoneData/sub-P002/ses-S004/eeg/sub-P002_ses-S004_task-Default_run-001_eeg.xdf",
    "./CapstoneData/sub-P002/ses-S006/eeg/sub-P002_ses-S006_task-FixedAsymmetry_run-001_eeg.xdf",
    "./CapstoneData/sub-P002/ses-S007/eeg/sub-P002_ses-S007_task-FixedAsymmetry_run-002_eeg.xdf",
    "./CapstoneData/sub-P002/ses-S008/eeg/sub-P002_ses-S008_task-Default_run-002_eeg.xdf",
    # "./CapstoneData/sub-P002/ses-S009 (bad signal)/eeg/sub-P002_ses-S009_task-Default_run-001_eeg.xdf",
    "./CapstoneData/sub-P002/ses-S010/eeg/sub-P002_ses-S010_task-Default_run-001_eeg.xdf"
]

sessions = []

plt.style.use('ggplot')

for f in filenames:
    sessions.append(compute(f))

faa_plots = defaultdict(list)
theta_plots = defaultdict(list)

faa_data = defaultdict(list)
theta_data = defaultdict(list)

for ann in annotations_map.values():
    for s in sessions:
        faa_plots[ann].append(np.mean(s[0][ann]))
        theta_plots[ann].append(np.mean(s[1][ann]))

        faa_data[ann].append(np.mean(s[0][ann]))
        theta_data[ann].append(np.mean(s[1][ann]))
        faa_data[ann].append(np.std(s[0][ann]))
        theta_data[ann].append(np.std(s[1][ann]))

x = [
    "Session 1",
    "Session 2",
    "Session 3",
    "Session 5",
]

# line plot
faa_fig, faa_ax = plt.subplots()
theta_fig, theta_ax = plt.subplots()

# bar plot
barWidth = 0.75 / len(sessions)
x_bar = [np.arange(len(sessions))]

for i in range(len(sessions) - 1):
    x_bar.append([x + barWidth for x in x_bar[-1]])

faa_bar_fig, faa_bar_ax = plt.subplots()
theta_bar_fig, theta_bar_ax = plt.subplots()

faa_ax.set_ylabel(r'FAA Score ($\ \ln(F4) - \ln(F3)\ $)')
theta_ax.set_ylabel(r'Theta Power ($\mu V^2$)')
faa_bar_ax.set_ylabel(r'FAA Score ($\ \ln(F4) - \ln(F3)\ $)')
theta_bar_ax.set_ylabel(r'Theta Power ($\mu V^2$)')

for i, (name, val) in enumerate(faa_plots.items()):
    faa_ax.plot(x, val, 'o-', label=name)
    faa_bar_ax.bar(x_bar[i], val, width=barWidth, label=name)

for i, (name, val) in enumerate(theta_plots.items()):
    theta_ax.plot(x, val, 'o-', label=name)
    theta_bar_ax.bar(x_bar[i], val, width=barWidth, label=name)

faa_ax.set_ylim(-0.5, 0.5)
faa_bar_ax.set_ylim(-0.3, 0.3)
theta_bar_ax.set_ylim(0, 25.0)

faa_bar_ax.set_xticks([r + barWidth for r in range(len(x))], x)
theta_bar_ax.set_xticks([r + barWidth for r in range(len(x))], x)

faa_ax.legend()
theta_ax.legend()
faa_bar_ax.legend()
theta_bar_ax.legend()

faa_fig.savefig("./out/faa_vs_sessions.png")
theta_fig.savefig("./out/theta_vs_sessions.png")

faa_fig.suptitle("Mean FAA within training blocks over sessions")
theta_fig.suptitle("Mean Theta power within training blocks over sessions")

faa_fig.savefig("./out/faa_vs_sessions_title.png")
theta_fig.savefig("./out/theta_vs_sessions_title.png")

faa_bar_fig.savefig("./out/faa_vs_sessions_bar.png")
theta_bar_fig.savefig("./out/theta_vs_sessions_bar.png")

faa_df = pd.DataFrame.from_dict(faa_data)
theta_df = pd.DataFrame.from_dict(theta_data)

faa_df.to_csv('./out/faa_vs_sessions.csv')
theta_df.to_csv('./out/theta_vs_sessions.csv')

for name, v in theta_plots.items():
    print(f"{name}: {np.mean(v)}")

for name, v in faa_plots.items():
    print(f"{name}: {np.mean(v)}")


# plt.bar(br1, IT, color ='r', width=barWidth, edgecolor ='grey', label ='IT')
# plt.bar(br2, ECE, color ='g', width = barWidth,
#         edgecolor ='grey', label ='ECE')
# plt.bar(br3, CSE, color ='b', width = barWidth,
#         edgecolor ='grey', label ='CSE')

