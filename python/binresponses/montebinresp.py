import string, random, sys, cPickle
from math import *
from Numeric import *
from miscutils import *
from presto import *
from orbitstuff import *

# Some admin variables
parallel = 0        # True or false
showplots = 0       # True or false
debugout = 0        # True or false
orbsperpt = 100     # Number of orbits to test
pmass = 1.35        # Pulsar mass in solar masses
cmass = {'WD': 0.3, 'NS': 1.35, 'BH': 10.0}  # Companion masses to use
ecc = {'WD': 0.0, 'NS': 0.6, 'BH': 0.6}      # Eccentricities to use

# Simulation parameters
numTbyPb = 100      # The number of points along the x axis
minTbyPb = 0.01     # Minimum Obs Time / Orbital Period
maxTbyPb = 10.0     # Maximum Obs Time / Orbital Period
numppsr = 100       # The number of points along the y axis
minppsr = 0.0005    # Minimum pulsar period (s)
maxppsr = 5.0       # Maximum pulsar period (s)
ctype = 'WD'        # The type of binary companion: 'WD', 'NS', or 'BH'
numbetween = 2      # The number of bins to interpolate during searches
dt = 0.0001         # The duration of each data sample (s)

# Get important psrparams info from a list
def psrparams_from_list(pplist):
    psr = presto.psrparams()
    psr.p = pplist[0]
    psr.orb.p = pplist[1]
    psr.orb.x = pplist[2]
    psr.orb.e = pplist[3]
    psr.orb.w = pplist[4]
    psr.orb.t = pplist[5]
    return psr

########################################################

# Calculate the values of our X and Y axis points
logTbyPb = span(log(minTbyPb), log(maxTbyPb), numTbyPb)
logppsr = span(log(minppsr), log(maxppsr), numppsr)
TbyPb = exp(logTbyPb)
ppsr = exp(logppsr)

# Figure out our environment 
if showplots:
    import Pgplot
if parallel:
    import mpi
    from mpihelp import *
    myid = mpi.comm_rank()
    numprocs = mpi.comm_size()
else:
    myid = 0
    numprocs = 1

# Open a file to save each orbit calculation
file = open('montebinresp_saves.txt','w')

# The Simulation loops

# Loop over T / Porb
for x in range(numTbyPb):
    Pb = T / TbyPb[x]
    xb = asini_c(Pb, mass_funct2(pmass, cmass[ctype], pi / 3.0))
    eb = ecc[ctype]

    # Loop over fpsr
    for y in range(numfpsr):
        # Each processor calculates its own point
        if not (y % myid == 0):  continue
        else:
            # Adjust the number of points in the time series so as to
            # keep the fpsr in the center of the FFT freq range
            # (i.e. fpsr = Nyquist freq / 2)
            N = 4 * fpsr[y]
            T = N * dt
            Ppsr = 1.0 / fpsr[y]

            # Loop over the number of tries per point
            for ct in range(orbsperpt):
                if (eb == 0.0):
                    wb, tp = 0.0, 0.0
                else:
                    (orbf, orbi)  = modf(ct / sqrt(orbsperpt))
                    orbi = orbi / sqrt(orbsperpt)
                    wb, tp = orbf * 180.0, Pb * orbi
                psr = psrparams_from_list([Ppsr, Pb, xb, eb, wb, tp])
                resp = 

# Decide what work we have to perform
work = ['p', 'x', 't', 'e', 'w']
if not parallel:
    if ctype=='WD':
        numjobs = 3
    else:
        numjobs = 5
else:
    numjobs = 1
    
# Begin the loop over the candidates
widths = []
for i in range(numloops):
    # Generate the fake pulsar parameters
    if myid==0:
        psr = fake_mspsr(companion = ctype)
        psrlist = psrparams_to_list(psr)
    else:
        psr = presto.psrparams()
        psrlist = None
    if parallel:
        psrlist = bcast_general(psrlist, myid, 0)
        if myid==0: psrlist = psrparams_to_list(psr)
        else: psr = psrparams_from_list(psrlist)
        if debugout:
            allproc_print(numprocs, 'Psr period =', psr.p)
    print ''
    print 'Trial', i
    if debugout:
        print ''
        print '   PSR mass              =', mpsr
        print '   Companion mass        =', mc
        print '   PSR period (s)        =', psr.p
        print '   PSR frequency (hz)    =', 1.0/psr.p
        print '   Orbit period (s)      =', psr.orb.p
        print '   Orbit asini/c (lt-s)  =', psr.orb.x
        print '   Orbit eccentricity    =', psr.orb.e
        print '   Orbit angle (deg)     =', psr.orb.w
        print '   Orbit time (s)        =', psr.orb.t
        print '   Orbit Fourier Freq    =', T/psr.orb.p
        print '   Orbit z               =', \
              presto.TWOPI*psr.orb.x/psr.p
        print ''
            
    # Create the data set
    cand = presto.orbitparams()
    m = 0
    comb = presto.gen_bin_response(0.0, 1, psr.p, T, psr.orb , 
                                   presto.LOWACC, m)
    ind = len(comb)
    # The follwoing is performed automatically in gen_bin_resp() now
    # m = (ind / 2 + 10) * numbetween
    data = Numeric.zeros(3 * ind, 'F')
    data[ind:2*ind] = comb
    if showplots and not parallel:
        Pgplot.plotxy(presto.spectralpower(data), color='red',
                      title='Data', labx='Fourier Frequency',
                      laby='Relative Power')
        a = raw_input("Press enter to continue...")
        Pgplot.nextplotpage(1)
        
    # Perform the loops over the Keplarian parameters
    for job in range(numjobs):
        if parallel:
            myjob = work[myid]
        else:
            myjob = work[job]
        if myjob=='p':
            Dd = Dp
            psrref = psr.orb.p
        if myjob=='x':
            Dd = Dx
            psrref = psr.orb.x
        if myjob=='t':
            Dd = Dt
            psrref = psr.orb.p
        if myjob=='e':
            Dd = De
            psrref = 1.0
        if myjob=='w':
            Dd = Dw
            psrref = 1.0
        firsttime = 1
        vals = []
        vals.append((0.0, 1.0))
        vals.append((0.0, 1.0))
        ddelta = Dd * psrref
        delta = ddelta
        while vals[-1][1] > 0.5 and vals[-2][1] > 0.5:
            for currentdelta in [delta, -delta]:
                # Adjust our candidate orbital period
                cand = copyorb(psr.orb, cand)
                if myjob=='p': cand.p = psr.orb.p + currentdelta
                if myjob=='x': cand.x = psr.orb.x + currentdelta
                if myjob=='t': cand.t = psr.orb.t + currentdelta
                if myjob=='e': cand.e = psr.orb.e + currentdelta
                if myjob=='w': cand.w = psr.orb.w + currentdelta
                # Generate the new correlation kernel
                kernel = presto.gen_bin_response(0.0, numbetween,
                                                 psr.p, T, cand, 
                                                 presto.LOWACC, m)
                # Perform the correlation
                result = corr(data, kernel, numbetween, firsttime)
                firsttime = 0
                # Convert to a power spectrum
                respow = presto.spectralpower(result)
                vals.append((currentdelta/psrref,
                             Numeric.maximum.reduce(respow)))
                if debugout:
                    # Print the most recent results
                    print '   %s:  Delta = %10.6f   Response = %8.5f' % \
                          (myjob, vals[-1][0], vals[-1][1])
                if showplots and not parallel:
                    # Plot the results of the correlation
                    Pgplot.plotxy(respow, labx='Frequency',
                                  laby='Relative Power')
                    a = raw_input("Press enter to continue...")
                    Pgplot.nextplotpage(1)
            # A very rough adaptive stepsize
            if abs(vals[-3][1] - vals[-1][1]) < 0.04:
                ddelta = ddelta * 2.0            
            delta = delta + ddelta
        # Fit a quadratic to the width values
        fit = leastSquaresFit(quadratic, (-1.0, 0.0, 1.0), vals)
        if debugout:
            print '\n   %sfit = %fx^2 + %fx + %f\n' % (myjob, fit[0][0],
                                                       fit[0][1],
                                                       fit[0][2])
        width = 2.0*math.sqrt(-0.5/fit[0][0])
        if parallel:
            newwidths = mpi.gather_string(str(width), 0)
            if myid==0:
                for proc in range(numprocs):
                    psrlist.append(string.atof(newwidths[proc]))
        else:
            psrlist.append(width)
    widths.append(psrlist)
    if debugout:
        print 'Widths are', widths[i]
    # Save our most recent orbit and width information
    cPickle.dump(widths[i], file, 1)
file.close()

# Store important psrparams info in a list
def psrparams_to_list(psr):
    result = []
    result.append(psr.p)
    result.append(psr.orb.p)
    result.append(psr.orb.x)
    result.append(psr.orb.e)
    result.append(psr.orb.w)
    result.append(psr.orb.t)
    return result

# Correlate a kernel with a data array.  Return the good parts.
def corr(data, kernel, numbetween, firsttime=0):
    numkern = len(kernel)
    kern_half_width = numkern / (2 * numbetween)
    lobin = m / numbetween
    numbins = len(data) - 2 * lobin
    if firsttime: samedata = 0
    else: samedata = 1
    result = Numeric.zeros(numbins * numbetween, 'F')
    presto.corr_complex(data, len(data), lobin, numbins, 
                        numbetween, kernel, m, result, samedata, 0)
    return result

