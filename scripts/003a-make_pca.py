import mne
import os.path as op
from mne.report import Report
import config
import matplotlib.pyplot as plt
from matplotlib import gridspec


layout = mne.channels.read_layout('KIT-AD.lout')
img = config.img
drive = config.drive
exp = 'OLDT'
filt = config.filt
redo = config.redo
reject = config.reject
baseline = (-.2, -.1)
tmin, tmax = -.2, .6


for subject in config.subjects:
    print config.banner % subject

    # define filenames
    path = op.join(drive, subject, 'mne')
    fname_rep = op.join(config.results_dir, subject,
                        subject + '_%s_%s_filt_pca-report.html'
                        % (exp, filt))
    fname_epo = op.join(path, subject + '_%s_calm_%s_filt-epo.fif'
                        % (exp, filt))
    fname_proj = op.join(path, subject + '_%s_calm_%s_filt-proj.fif'
                         % (exp, filt))

    if not op.exists(fname_proj) or redo:
        rep = Report()
        # pca input is from fixation cross to three hashes
        # no language involved
        epochs = mne.read_epochs(fname_epo)['prime']
        epochs.pick_types(meg=True, exclude='bads')
        epochs.drop_bad_epochs(reject=reject)

        # plot evoked
        evoked = epochs.average()
        p = evoked.plot(titles={'mag': 'Original Evoked'}, show=False)
        rep.add_figs_to_section(p, 'Original Evoked Response to Prime Word',
                                'Summary', image_format=img)

        # compute the SSP
        epochs.crop(-.1, .03, copy=False)
        ev_proj = epochs.average()
        projs = mne.compute_proj_evoked(ev_proj, n_mag=3)

        # apply projector individually
        evokeds = list()
        for proj in projs:
            ev = evoked.copy()
            ev.add_proj(proj, remove_existing=True)
            ev.apply_proj()
            evokeds.append(ev)

        # plot PCA topos
        p = mne.viz.plot_projs_topomap(projs, layout, show=False)
        rep.add_figs_to_section(p, 'PCA topographies', 'Summary',
                                image_format=img)

        # plot evoked - each proj
        for i, ev in enumerate(evokeds):
            pca = 'PC %d' % i
            fig = plt.figure(figsize=(12, 6))
            gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1])
            ax0 = plt.subplot(gs[0])
            ax1 = plt.subplot(gs[1])
            e = ev.plot(titles={'mag': 'PC %d' % i}, show=False, axes=ax0)
            p = mne.viz.plot_projs_topomap(ev.info['projs'], layout,
                                           show=False, axes=ax1)
            rep.add_figs_to_section(fig, 'Evoked without PC %d' %i,
                                    pca, image_format=img)

        # remove all
        evoked.add_proj(projs).apply_proj()
        e  = evoked.plot(titles={'mag': 'All PCs'}, show=False)
        rep.add_figs_to_section(e, 'Evoked without all PCs',
                                'All PCs', image_format=img)

        rep.save(fname_rep, overwrite=True, open_browser=False)

        # save projs
        mne.write_proj(fname_proj, projs)
