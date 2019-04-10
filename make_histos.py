# import uproot_patched as uproot
import uproot
from uproot_exts import *
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
from matplotlib import gridspec
import os.path

rcParams['font.family'] = 'DejaVu Sans Mono'

def to_precision(x,p):
    x = float(x)
    if x == 0.: return "0.0"
    c_count = False
    a_count = False
    c = 0
    a = -1
    for d in "{:f}".format(x):
        if not d in ["-", ".", "0"]: c_count = True
        if d == ".": a_count = True
        if c_count: c += 1
        if a_count: a += 1
        if c > p: break
    if a < 0: a = 0
    return "{0:.{prec}f}".format(x, prec=a)

def format_title(title):
    if title == "":
        return " "
    title = title.replace("transverse momentum", "p_T")
    title = title.replace("{", "")
    title = title.replace("}", "")
    title = title.replace("# ", "tmp1")
    title = title.replace("#", "")
    title = title.replace("tmp1", "# ")
    return title

def format_math_title(title):
    if title == "":
        return " "
    title = title.replace("#","\\")
    title = title.replace("\\Chi","\\chi")
    return r'$'+title+r'$'

# Create the histogram label with the TH1 stats included
def create_TH1_label(h1, label):
    return "{0}\nEntries{1:11.2f}\nMean{2}\nStd Dev{3}\nUnderflow{4:9d}\nOverflow{5:10d}".format(\
            label,
            np.sum(getEffectiveEntriesTH1(h1)),
            to_precision(getMeanTH1(h1), 4).rjust(14),
            to_precision(getStdDevTH1(h1), 4).rjust(11),
            int(h1.underflows),
            int(h1.overflows))

# Create the histogram label with the TProfile stats included
def create_TProfile_label(h1, label):
    return "{0}\nEntries{1:11.2f}\nMean{2}\nMean y{3}".format(\
            label,
            np.sum(getEffectiveEntriesTProfile(h1)),
            to_precision(getMeanTH1(h1), 4).rjust(14),
            to_precision(getMeanTH1(h1, axis=2), 4).rjust(12))

def construct_plot(tgt, ref, title_y=0., logscale=False, hist_type="TH1", adjust_top=0.):
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
    axis = plt.subplot(gs[0])

    gs.update(wspace=0.025, hspace=0.025)

    plt.title(format_title(tgt.title), y=title_y,fontweight="bold")

    axr  = plt.subplot(gs[1])
    plt.setp(axis.get_xticklabels(), visible=False)

    axr.set_xlabel(format_title(tgt._fXaxis._fTitle))
    axis.set_ylabel(format_title(tgt._fYaxis._fTitle))

    _, bins = tgt.numpy()
    axis.set_xlim(bins[0], bins[-1])
    axr.set_xlim(bins[0], bins[-1])
    axr.set_ylim(-0.4, 2.4)

    if hist_type == "TH1":
        create_label = create_TH1_label
        getErrors = getErrorsTH1
    if hist_type == "TProfile":
        create_label = create_TProfile_label
        getErrors = getErrorsTProfile

    hist_tgt, bins = tgt.numpy()
    if hist_type == "TProfile":
        hist_tgt = hist_tgt / np.array(tgt._fBinEntries)[1:-1]

    axis.errorbar((bins[1:]+bins[:-1])/2.,hist_tgt,yerr=np.array(getErrors(tgt)),
            fmt='s', color='r', markersize=3, capsize=0.0, capthick=1.5, elinewidth=1.5, label=create_label(tgt,"TARGET"))

    axr.plot(axr.get_xlim(), [1.,1.], 'k--', linewidth=0.5, alpha=0.8)

    # if not ref is None:
    hist_ref, bins = ref.numpy()
    if hist_type == "TProfile":
        hist_ref = hist_ref / np.array(ref._fBinEntries)[1:-1]
    hist_ref = np.nan_to_num(hist_ref)
    axis.step(bins,np.concatenate([[hist_ref[0]], hist_ref]),
            color='b', label=create_label(ref, "REFERENCE"))

    axr.errorbar((bins[1:]+bins[:-1])/2., hist_tgt/hist_ref, yerr=(np.array(getErrors(tgt))+np.array(getErrors(ref)))**0.5/hist_ref,
            fmt='s', markersize=3, capsize=0.0, capthick=1.5, elinewidth=1.5, color='k')

    # Make legend
    leg = axis.legend(prop={'family': 'DejaVu Sans Mono'},
                      bbox_to_anchor=(0., 1.02, 1., .102),
                      loc=3, ncol=2, mode="expand", borderaxespad=0.)


    # Color the text in the legend
    for artist, text in zip(leg.legendHandles, leg.get_texts()):
        col = artist.get_color()
        if isinstance(col, np.ndarray):
            col = col[0]
        text.set_color(col)

    if logscale:
        axis.set_yscale("log", nonposy='clip')

    plt.gcf().subplots_adjust(top=adjust_top)

    if hist_type == "TH1" and not logscale:
        axis.set_ylim(0, axis.get_ylim()[1])

    return axis, axr

def main(tgt_file, ref_file, spec_file, mAOD=(False, False), out_dir=None):

    if out_dir is None:
        out_dir = "__".join(tgt_file.split("__")[1:3]) + "__vs__" + "__".join(ref_file.split("__")[1:3])

    tgt_hists = uproot.open(tgt_file)['DQMData/Run 1/EgammaV/Run summary']
    ref_hists = uproot.open(ref_file)['DQMData/Run 1/EgammaV/Run summary']

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    with open(spec_file, 'r') as f:
        specs = [l.strip().split() for l in f.readlines() if "h_" in l]

    for s in specs:
        h_name     = s[0]
        h_name_ref = h_name
        if not mAOD[0]:
            h_name = h_name.replace("MiniAOD", "")
        if not mAOD[1]:
            h_name_ref = h_name_ref.replace("MiniAOD", "")

        if not "MiniAOD" in h_name and "recomp":
            h_name = h_name.replace("_recomp", "")

        if not "MiniAOD" in h_name_ref and "recomp":
            h_name_ref = h_name_ref.replace("_recomp", "")

        print("Drawing "+h_name)
        logscale = "ELE_LOGY" in tgt_hists[h_name]._fOption
        # ref = None
        # if h_name_ref in ref_hists:
        ref = ref_hists[h_name_ref]
        if "pfx" in s[0]:
            plt.figure(figsize=(6.0,5.85))
            construct_plot(tgt_hists[h_name], ref, title_y=1.25, logscale=logscale, hist_type="TProfile", adjust_top=0.80)
        else:
            plt.figure(figsize=(6.0,6.0))
            construct_plot(tgt_hists[h_name], ref, title_y=1.36, logscale=logscale, hist_type="TH1", adjust_top=0.77)
        plt.savefig(os.path.join(out_dir, os.path.basename(h_name))+".png", dpi=150, bbox="tight")
        plt.close()

if __name__ == "__main__":

    # execute only if run as a script
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('target', help='ROOT DQM file for target')
    parser.add_argument('reference', help='ROOT DQM file for reference')
    parser.add_argument('specifications', help='text file with histogram specification')
    # parser.add_argument('--out', help='output directory (histos/ by default)', default="histos")
    parser.add_argument('--mAOD', help='two flags to use miniAOD for target or reference (00 by default)', default="00")
    args = parser.parse_args()
    mAOD = (args.mAOD[0] != "0", args.mAOD[1] != "0")
    main(args.target, args.reference, args.specifications, mAOD=mAOD, out_dir=None)
