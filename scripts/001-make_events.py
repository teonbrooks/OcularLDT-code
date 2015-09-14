import os.path as op
from copy import deepcopy
import numpy as np
import mne
import config

redo = config.redo
path = config.drive


def make_events(raw, subject, exp):
    # E-MEG alignment
    evts = mne.find_stim_steps(raw, merge=-2)
    alignment = deepcopy(evts)
    idx = np.nonzero(alignment[:, 2])[0]
    alignment = alignment[idx]
    current_pos = np.array([(x & (2 ** 1 + 2 ** 0)) >> 0 for x in
                            alignment[:, 2]])
    idx = np.where(current_pos == 1)[0]
    alignment[idx, 2] = 50
    alignment = alignment[idx]

    if exp.startswith('OLDT'):
        expt = np.array([(x & 2 ** 5) >> 5 for x in evts[:, 2]], dtype=bool)
        evts = evts[expt]
        idx = np.nonzero(evts[:, 2])[0]
        evts = evts[idx]
        triggers = evts[:, 2]

        semantic = np.array([(x & 2 ** 4) >> 4 for x in triggers], dtype=bool)
        nonword_pos = np.array([(x & (2 ** 3 + 2 ** 2)) >> 2 for x in triggers])
        current_pos = np.array([(x & (2 ** 1 + 2 ** 0)) >> 0 for x in triggers])

        idx = np.where(nonword_pos - current_pos != 0)[0]
        idy = np.where(current_pos < nonword_pos)[0]
        idy2 = np.where(nonword_pos == 0)[0]
        idy3 = np.where(current_pos != 0)[0]
        idy = np.unique(np.hstack((idy, idy2, idy3)))
        n_idx = np.where(nonword_pos - current_pos == 0)[0]
        n_idy = np.where(nonword_pos != 0)[0]

        semantic_idx = np.where(semantic)[0]
        words_idx = np.intersect1d(idx, idy)
        nonwords_idx = np.intersect1d(n_idx, n_idy)
        fix_idx = np.where(current_pos == 0)[0]
        primes_idx = np.where(current_pos == 1)[0]
        targets_idx = np.where(current_pos == 2)[0]

    elif exp.startswith('SENT'):
        expt = np.array([(x & 2 ** 4) >> 4 for x in evts[:, 2]], dtype=bool)
        evts = evts[expt]
        idx = np.nonzero(evts[:, 2])[0]
        evts = evts[idx]
        triggers = evts[:, 2]

        semantic = np.array([(x & 2 ** 3) >> 3 for x in triggers], dtype=bool)
        current_pos = np.array([(x & (2 ** 2 + 2 ** 1 + 2 ** 0)) >> 0
                                for x in triggers])

        semantic_idx = np.where(semantic)[0]
        fix_idx = np.where(current_pos == 0)[0]
        primes_idx = np.where(current_pos == 1)[0]
        targets_idx = np.where(current_pos == 3)[0]

    else:
        raise ValueError('This function only works for '
                         'OLDTX or SENTX experiments, not %s.' % exp)

    # semantic priming condition
    target_words_idx = np.intersect1d(targets_idx, words_idx)  # target words
    primed_idx = np.intersect1d(semantic_idx, target_words_idx)
    unprimed_idx = np.setdiff1d(target_words_idx, primed_idx)


    # recode
    evts[:, 2] = 0
    # prime vs target
    evts[primes_idx, 2] += 1
    evts[targets_idx, 2] += 2
    # semantic priming
    evts[primed_idx, 2] += 4
    if exp.startswith('OLDT'):
        # word vs nonword
        evts[nonwords_idx, 2] += 8
    # alignment
    idx = np.hstack((fix_idx, primes_idx, targets_idx))
    evts[idx, 2] = 64
    # fixation
    evts[fix_idx, 2] = 128

    # write the co-registration event file
    idx = zip(trials[:, 0], np.arange(trials.size))
    idx = list(zip(*sorted(idx))[-1])
    trials = trials[idx]
    path = op.dirname(raw.info['filename'])
    mne.write_events(op.join(path, '..', 'mne', '%s_%s_trials-eve.txt')
                     % (subject, exp), trials)

    # write the co-registration file
    trial_fname = op.join(path, '..', 'mne', '%s_%s_trials.txt'
                          % (subject, exp))
    coreg_fname = op.join(path, '..', 'mne', '%s_%s_coreg-eve.txt'
                          % (subject, exp))
    coreg_evts = []
    with open(trial_fname, 'w') as FILE:
        FILE.write('trialid\ti_start\tprev_trigger\ttrigger\n')
        ii = 0
        for trial in trials:
            if trial[1] == 0:
                ii += 1
            else:
                coreg_evts.append(trial)
                trial = [ii] + list(trial)
                trial = '\t'.join(map(str, trial)) + '\n'
                FILE.write(trial)

    # write the events
    idx = zip(evts[:, 0], np.arange(evts.size))
    idx = list(zip(*sorted(idx))[-1])
    evts = evts[idx]
    path = op.dirname(raw.info['filename'])
    # master event list
    evts_fname = op.join(path, '..', 'mne', '%s_%s-eve.txt') % (subject, exp)
    mne.write_events(evts_fname, evts)
    # coreg event list
    coreg_evts = np.array(coreg_evts)
    mne.write_events(coreg_fname, coreg_evts)


for subject in config.subjects:
    print config.banner % subject

    exps = [config.subjects[subject][0], config.subjects[subject][2]]
    evt_file = op.join(path, subject, 'mne', subject + '_OLDT-eve.txt')
    if not op.exists(evt_file) or redo:
        if 'n/a' in exps:
            exps.pop(exps.index('n/a'))
            raw = config.kit2fiff(subject=subject, exp=exps[0],
                                  path=path, dig=False, preload=False)
        else:
            raw = config.kit2fiff(subject=subject, exp=exps[0],
                                  path=path, dig=False, preload=False)
            raw2 = config.kit2fiff(subject=subject, exp=exps[1],
                                  path=path, dig=False, preload=False)
            mne.concatenate_raws([raw, raw2])
        make_events(raw, subject, 'OLDT')
