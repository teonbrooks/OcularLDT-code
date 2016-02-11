import os.path as op
from glob import glob
import itertools
import numpy as np
from collections import defaultdict


mne_bin = '/Applications/packages/mne-c/bin'
# drives
drives = {'local': op.join(op.expanduser('~'), 'Experiments', 'E-MEG', 'data'),
          'server': op.join('/Volumes', 'server', 'MORPHLAB', 'Teon',
                            'E-MEG', 'data'),
          'home': op.join('/Volumes', 'teon-backup', 'Experiments',
                          'E-MEG', 'data'),
          'office': op.join('/Volumes', 'office', 'Experiments',
                            'E-MEG', 'data'),
          'google_drive': op.join(op.expanduser('~'), 'Google Drive',
                                  'E-MEG', 'data'),
          'dropbox': op.join(op.expanduser('~'), 'Dropbox', 'academic',
                             'Experiments', 'E-MEG', 'output'),
         }
# Parameters:
redo = True
results_dir = op.join(drives['dropbox'], 'results')
reject = dict(mag=3e-12)
baseline = (-.2, -.1)
img = 'png'
filt = 'iir'
banner = ('#' * 9 + '\n# %s #\n' + '#' * 9)
# determine which drive you're working from
drive = 'home'
event_id = {'word/prime/unprimed': 1,
            'word/target/unprimed': 2,
            'word/prime/primed': 5,
            'word/target/primed': 6,
            'nonword/prime': 9,
            'nonword/target': 10,
            # for the co-registration, there are no fixations in the evts
            # 'fixation': 128
            }

# Bad Channels
bads = defaultdict(lambda: [])
bads['A0023'] += ['MEG 059']
bads['A0023'] += ['MEG 049', 'MEG 054']
bads['A0136'] += ['MEG 057', 'MEG 128', 'MEG 179']
bads['A0106'] += ['MEG 160', 'MEG 072']


# arrange the OLDT in the presentation order
subjects = {'A0023': ['OLDT2', 'SENT2', 'OLDT1'],
            'A0078': ['OLDT1', 'SENT1', 'OLDT2'],
            'A0085': ['OLDT2', 'SENT2', 'OLDT1'],
            'A0100': ['OLDT1', 'SENT1', 'OLDT2'],
            'A0106': ['OLDT1', 'SENT1', 'OLDT2'],
            'A0110': ['OLDT2', 'SENT2', 'OLDT1'],
            'A0123': ['OLDT1', 'SENT1', 'OLDT2'],
            'A0125': ['OLDT1', 'SENT2', 'OLDT2'],
            'A0127': ['OLDT2', 'SENT1', 'OLDT1'],
            # 'A0129': ['OLDT1', 'SENT1', 'n/a'],
            'A0129': ['OLDT1', 'SENT1', 'OLDT2'],
            'A0130': ['OLDT2', 'SENT2', 'OLDT1'],
            'A0134': ['OLDT2', 'SENT2', 'OLDT1'],
            'A0136': ['OLDT1', 'SENT1', 'OLDT2'],
            # 'A0148': ['OLDT1', 'SENT1', 'n/a'],
            'A0148': ['OLDT1', 'SENT1', 'OLDT2'],
            'A0150': ['OLDT2', 'SENT2', 'OLDT1'],
            'A0155': ['OLDT2', 'SENT2', 'OLDT1'],
            'A0159': ['OLDT1', 'SENT1', 'OLDT2'],
            # 'A0161': ['n/a', 'SENT1', 'OLDT2'],
            'A0161': ['OLDT1', 'SENT1', 'OLDT2'],
            'A0163': ['OLDT2', 'SENT2', 'OLDT1'],
            'A0164': ['OLDT2', 'SENT2', 'OLDT1'],
            }

for subject, _ in subjects.items():
    if op.exists(op.join(drives[drive], subject)):
        continue
    else:
        del subjects[subject]

drive = drives[drive]

def kit2fiff(subject, exp, path, dig=True, preload=False):
    from mne.io import read_raw_kit
    kit = op.join(path, subject, 'kit',
                  subject + '*' + exp + '*' + 'calm.con')
    mrk_pre = op.join(path, subject, 'kit',
                      subject + '*mrk*' + 'pre_' + exp + '*.mrk')
    mrk_post = op.join(path, subject, 'kit',
                       subject + '*mrk*' + 'post_' + exp + '*.mrk')
    elp = op.join(path, subject, 'kit', subject + '*p.txt')
    hsp = op.join(path, subject, 'kit', subject + '*h.txt')

    mrk_pre = glob(mrk_pre)[0]
    mrk_post = glob(mrk_post)[0]
    elp = glob(elp)[0]
    hsp = glob(hsp)[0]
    kit = glob(kit)[0]

    if dig:
        raw = read_raw_kit(input_fname=kit, mrk=[mrk_pre, mrk_post],
                           elp=elp, hsp=hsp, stim='>', slope='+',
                           preload=preload, verbose=False)
    else:
        raw = read_raw_kit(input_fname=kit, stim='>', slope='+',
                           preload=preload, verbose=False)

    return raw
