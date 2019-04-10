"""
This is an extension of uproot with more member functions of TH1 and TProfile
implemented.
"""

from uproot import *

################################
# Additional functions for TH1 #
################################

def getEffectiveEntriesTH1(self):
    if self.fSumw2:
        entries = []
        for w, w2 in zip(self, self.fSumw2):
            if w2 == 0:
                entries.append(0)
                continue
            entries.append(max(w**2/w2, 0))
        return entries
    else:
        return self[:]

def getAllErrorsTH1(self):
    """Return values of errors, including underflow and overflow bin.
    if the sum of squares of weights has been defined (via Sumw2),
    this function returns the sqrt(sum of w2).
    otherwise it returns the sqrt(contents) for this bin.
    """

    if self.fSumw2:
        return [sumw2**0.5 for sumw2 in self.fSumw2]
    return [counts**0.5 for counts in self]

def getErrorsTH1(self):
    """Return values of errors, without underflow and overflow bin.
    """
    return self.allerrors[1:-1]

def getMeanTH1(self, axis=1):
    """Returns the mean value of the histogram.
    """
    if self.fTsumw == 0:
        return 0
    if axis == 1:
        return self.fTsumwx/self.fTsumw
    if axis == 2:
        return self.fTsumwy/self.fTsumw

def getStdDevTH1(self):
    """Returns the Standard Deviation (Sigma) along the X axis.
    The Sigma estimate is computed as
    \f[
    \sqrt{\frac{1}{N}(\sum(x_i-x_{mean})^2)}
    \f]
    """
    if self.fTsumw == 0:
        return 0
    x = self.fTsumwx/self.fTsumw
    stddev2 = abs(self.fTsumwx2/self.fTsumw - x*x)
    return stddev2**0.5

rootio.methods["TH1"].std_dev   = property(getStdDevTH1)
rootio.methods["TH1"].allerrors = property(getAllErrorsTH1)
rootio.methods["TH1"].errors    = property(getErrorsTH1)
rootio.methods["TH1"].getMean   = getMeanTH1
rootio.methods["TH1"].getEffectiveEntries  = getEffectiveEntriesTH1

########################
# Methods for TProfile #
########################

class TProfileMethods(object):
    # makes __doc__ attribute mutable before Python 3.3
    __metaclass__ = type.__new__(type, "type", (rootio.methods["TH1"].__metaclass__,), {})
    @property
    def values(self):
        return [x/self.fBinEntries[i] for i, x in enumerate(self)][1:-1]
    def getEffectiveEntries(self):
        """Return bin effective entries for a weighted filled Profile histogram.
        In case of an unweighted profile, it is equivalent to the number of
        entries per bin The effective entries is defined as the square of the
        sum of the weights divided by the sum of the weights square.
        TProfile::Sumw2() must be called before filling the profile with
        weights. Only by calling this method the  sum of the square of the
        weights per bin is stored.
        """
        if self.fBinSumw2:
            entries = []
            for w, w2 in zip(self.fBinEntries, self.fBinSumw2):
                if w2 == 0:
                    entries.append(0)
                    continue
                entries.append(max(w**2/w2, 0))
            return entries
        else:
            return self.fBinEntries
    @property
    def errors(self):
        """compute bin error of profile histograms
        """
        def get_error(cont, summ, err2, neff):
            # for empty bins
            if summ == 0:
                return 0.
            # case the values y are gaussian distributed
            #     y +/- sigma and w = 1/sigma^2
            elif self.fErrorMode == 3:
                return 1/summ**0.5
            # compute variance in y (eprim2) and standard deviation in y (eprim)
            contsum = cont/summ
            eprim2  = abs(err2/summ - contsum*contsum)
            eprim   = eprim2**0.5

            if self.fErrorMode == 2:
                if eprim != 0:
                    return eprim/neff**0.5
                # in case content y is an integer (so each my has an error
                # +/- 1/sqrt(12) when the std(y) is zero
                return 1/(12*neff)**0.5

            #  if approximate compute the sums (of w, wy and wy2) using all the
            #  bins when the variance in y is zero
            test = 1
            if err2 != 0 and neff < 5:
                test = eprim2*summ/err2;
            # if self.fgApproximate and (test < 1.e-4 or eprim2 <= 0):
            if False and (test < 1.e-4 or eprim2 <= 0):
               # compute mean and variance in y
               scontsum = self.fTwumwy/self.fTsumw                           # global mean
               seprim2  = abs(self.fTwumwy2/self.fTsumw - scontsum*scontsum) # global variance
               eprim    = 2*seprim2**0.5;                                    # global std (why factor of 2 ??)
               summ = ssum
            summ = abs(summ)

            # case option "S" return standard deviation in y
            if self.fErrorMode == 1:
                return eprim

            # default case : fErrorMode = kERRORMEAN
            # return standard error on the mean of y
            return eprim/neff**0.5

        errors = []
        for args in zip(self, self.fBinEntries, self.fSumw2, self.getEffectiveEntries()):
            errors.append(get_error(*args))
        return errors[1:-1]

rootio.methods["TProfile"] = TProfileMethods
