#!/bin/env python
# coding: utf-8

#****************************************************************************
#  TAEC(Tiny Avc Encode Consultant).py 
#                                                     written by Chikezun
#  Reference literature:
#    ITU-T H.264 (03/2010)
#       – Advanced video coding for generic audiovisual
#    猫科研究所( http://www.up-cat.net/ )
#       x264(vbv-maxrate,vbv-bufsize,profile,level),H.264(Profile/Level)
#
#****************************************************************************

__version__ = '0.3.2'
import sys
import getopt
import math

def set_default():
    width   = int(1920) # must integer
    height  = int(1080) # must integer
    fpsnum  = int(24000) # must integer
    fpsden  = int(1001) # must integer
    profile = 'high'
    mode    = 'progressive'
    return [[width, height], [fpsnum, fpsden], profile, mode]

def usage():
    param = set_default()
    print "\nUsage: taec.py [options]\n"
    print "  -r, --resolution <string> :set 'width x height' ('%ix%i')"\
                % tuple(param[0])
    print "  -f, --fps <string>        :set 'fpsnum / fpsden' ('%i/%i')"\
                % tuple(param[1])
    print "  -p, --profile <string>    :set 'profile' ('%s')" % param[2]
    print "  -i, --interlaced          :specify interlaced mode (not specified)"
    print "  -v, --version             :display version"
    print "  -h, --help                :display this help and exit\n"

def check_res_and_fps(arg, r_or_f):
    try:
        param = [abs(int(i)) for i in arg.split('x' * r_or_f or '/')]
        if len(param) != 2:
            raise SyntaxError
    except:
        print "\nERROR : invalid %s setting." % ('resolution' * r_or_f or 'fps')
        usage()
        sys.exit()
    else:
        return param

def check_profile(profile, ipflag):
    if profile in ('baseline', 'main', 'high'):
        if profile != 'baseline' or ipflag != 'interlaced':
            return 1
        else:
            print "\nERROR : baseline cannot accept interlaced."
    print "\nERROR : invalid profile setting."
    usage()
    sys.exit()

def calc_bs(resolution, fps, ipflag):
    fstmp = [int(math.ceil(float(i) / 16)) for i in resolution]
    fs = dbp = fstmp[0] * fstmp[1]
    mbps  = fs * fps[0] // fps[1]
    if ipflag == 'interlaced':
        dbp += fstmp[0] * (fstmp[1] & 1)
    return [mbps, fs, dbp]

def calc_lv(bs, ip, spec):
    for i in spec:
        if bs[0] <= i[1] and bs[1] <= i[2] and bs[2] <= i[3]:
            return i[0]
    if ip == 'interlaced':
        print "ERROR : interlaced encoding cannot be done to this video."
    print "ERROR : there is no suitable setting."
    usage()
    sys.exit()

def calc_result(pr, bs, line):
    vbv = [int(i * ((pr == 'high') * 1.25 or 1)) for i in line[4]]
    ref = [16 * (i > 16) or i for i in [line[3] // bs[2]]]
    return tuple([line[0]] + vbv + ref)

def display_result(lv, pr, bs, spec):
    index = [i[0] for i in spec]
    try:
        for i in xrange(len(index)):
            if index[i] == lv:
                line = spec[i]
                print "%5s%12i%13i%8i" % calc_result(pr, bs, line)
                lv = index[i + 1]
    except:
        return 0

def get_spec():
#H.264/AVC spec [(level, MaxMBPs, MaxFS, MaxDbpMBs, [MaxBR, MaxCPB], ipflag]}
    return [('1.0',   1485,    99,    396, [    64,    175], 'p'),
            ('1b ',   1485,    99,    396, [   128,    350], 'p'),
            ('1.1',   3000,   396,    900, [   192,    500], 'p'),
            ('1.2',   6000,   396,   2376, [   384,   1000], 'p'),
            ('1.3',  11880,   396,   2376, [   768,   2000], 'p'),
            ('2.0',  11880,   396,   2376, [  2000,   2000], 'p'),
            ('2.1',  19800,   792,   4752, [  4000,   4000], 'i'),
            ('2.2',  20250,  1620,   8100, [  4000,   4000], 'i'),
            ('3.0',  40500,  1620,   8100, [ 10000,  10000], 'i'),
            ('3.1', 108000,  3600,  18000, [ 14000,  14000], 'i'),
            ('3.2', 216000,  5120,  20480, [ 20000,  20000], 'i'),
            ('4.0', 245760,  8192,  32768, [ 20000,  25000], 'i'),
            ('4.1', 245760,  8192,  32768, [ 50000,  62500], 'i'),
            ('4.2', 491520,  8192,  34816, [ 50000,  62500], 'p'),
            ('5.0', 589824, 22080, 110400, [135000, 135000], 'p'),
            ('5.1', 983040, 36864, 184320, [240000, 240000], 'p')]

def set_param(opts,param):
    for opt, arg in opts:
        if opt in ("-r", "--resolution"):
            param[0] = check_res_and_fps(arg, 1)
        elif opt in ("-f", "--fps"):
            param[1] = check_res_and_fps(arg, 0)
        elif opt in ("-p", "--profile"):
            param[2] = arg
        elif opt in ("-i", "--interlaced"):
            param[3] = 'interlaced'
        elif opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-v", "--version"):
            print "tiny avc encode consultant %s" % __version__
            sys.exit()
    return param

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "r:f:p:ihv",
            ["resolution=","fps=","profile=","interlaced","help","version"])
    except:
        usage()
        sys.exit()

    param = set_default()

    if len(opts) > 0:
        param = set_param(opts,param)
    else:
        usage()

    check_profile(param[2], param[3])

    print
    print " resolution       : %i x %i" % tuple(param[0])
    print " fps              : %i / %i" % tuple(param[1])
    print " profile          : %s"      % param[2]
    print " encoding mode    : %s\n"    % param[3]

    bitstream = calc_bs(param[0], param[1], param[3])
    print " MBPS ... %6iMB/s" % bitstream[0]
    print " FS   ... %6iMBs"  % bitstream[1]
    print " DPB  ... %6iMBs\n"  % bitstream[2]

    if param[3] == 'interlaced':
        avcspec = [i for i in get_spec() if i[5] == 'i']
    else:
        avcspec = get_spec()

    minlv = calc_lv(bitstream, param[3], avcspec)

    print " suitable settings are ...\n"
    print " level  vbv-maxrate  vbv-bufsize  max-ref"
    print " ----------------------------------------"
    display_result(minlv, param[2], bitstream, avcspec)
