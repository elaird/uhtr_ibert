import csv
import os
import ROOT as r


def versions(sn=None):
    tag = ""
    if 13 <= sn <= 16:
        tag = "v1.5"
    elif 103 <= sn <= 110:
        tag = "v1.3r"
    elif 111 <= sn <= 144:
        tag = "v1.4"
    else:
      print "version of s/n %d not known" % sn
    return "uHTR %s %d" % (tag, sn)


def datetimes(l):
    dts = []
    for fileName in l:
        f = open(fileName)
        d = {"fileName": fileName}
        for line in f:
            fields = line.split(",")
            if len(fields) != 2:
                continue
            if fields[0] not in ["date", "time"]:
                continue
            d[fields[0]] = fields[1].replace("\n", "")
        f.close()
        if len(d) == 3:
            dts.append(d)
    return dts


def latest(l=[]):
    tuples = []
    for d in datetimes(l):
        month, day, year = d["date"].split("/")
        n = int(day)
        n += int(month) * 31
        n += int(year) * 31 * 12
        fields = d["time"].split()
        assert fields[2] == "CEST"
        n *= 60*24  # minutes per day
        hm = fields[0].split(":")
        hour = int(hm[0])
        minute = int(hm[1])
        if fields[1] == "PM":
            hour += 12
        n += minute
        n += hour * 60
        tuples.append((n, d["fileName"]))
    assert tuples
    return max(tuples)[1]


def csvFileName(dir="", sn=0, gtx=0, run=""):
    dir = "%s/uHTR%03d" % (dir, sn)
    prefix = "%s_sweep_results" % gtx
    suffix = ".csv"
    default = "%s/%s%s%s" % (dir, prefix, run, suffix)

    if run == "latest":
        candidates = []
        for fileName in os.listdir(dir):
            if not fileName.startswith(prefix):
                continue
            if not fileName.endswith(suffix):
                continue
            candidates.append("%s/%s" % (dir, fileName))
        if candidates:
            return latest(candidates)
        else:
            return default
    else:
        return default


def results(sn, gtx, run, ctp7=False, func=csvFileName):
    d = {-5: " RX Sampling Point(tap)",
          -2: " # Errs",
          -1: " BER",
          }
    if ctp7:
        dir = "ctp7"
        del d[-2]
        d[-3] = " # Errs1"
        okLen = 10
    else:
        dir = "optical_loopback"
        okLen = 11

    fileName = func(dir=dir, sn=sn, gtx=gtx, run=run)

    out = []

    try:
        assert fileName
        f = open(fileName)
    except IOError, e:
        print e
        return out

    headers = []
    for row in csv.reader(f):
        if len(row) != okLen:
            continue
        if not headers:
            headers = row
        else:
            try:
                phase = int(row[-5])
                nErrors = int(row[-3]) if ctp7 else None
                ber = float(row[-1])
                out.append( (phase, nErrors, ber))
            except ValueError:
                print "skipping %s\n%s\n" % (fileName, row)

    f.close()
    for i, s in sorted(d.iteritems()):
        assert headers[i] == s, fileName + s
    return out


def oneGraph(uhtr, gtx100, gtx4, run, ctp7=None, xMin=None, xMax=None, csvFileNameFunc=None):
    g = r.TGraph()
    gtx = "%s%d_%d" % ("GTH" if ctp7 else "GTX", gtx4, gtx100)
    g.SetName("%d_%s_%s" % (uhtr, gtx, run))
    res = results(uhtr, gtx, run,
                  ctp7=ctp7,
                  func=csvFileNameFunc)

    if not res:
        return
    phases = [x[0] for x in res]
    pMin = min(phases) if xMin else 0
    pMax = max(phases) if xMin else 127

    assert (pMax - pMin), "%d_%d" % (pMax, pMin)
    for i, (phase, nErrors, ber) in enumerate(res):
        x = xMin + (xMax - xMin) * (phase - pMin) / (pMax - pMin)
        g.SetPoint(i, x, ber)
    return g


def graphs(xMin=0.0, xMax=1.0, uhtrs=[], runs=[""], gtxes=[], ctp7=False,
           csvFileNameFunc=csvFileName):
    if not gtxes:
        gtx4s = range(4)
        if ctp7:
            gtxes = range(113, 116)
        else:
            gtxes = range(112, 118)
    else:
        gtx4s = range(1)

    out = {}
    for uhtr in uhtrs:
        for gtx100 in gtxes:
            for gtx4 in gtx4s:
                for run in runs:
                    key = (uhtr, gtx100, gtx4, run)
                    g = oneGraph(*key,
                                  xMin=xMin,
                                  xMax=xMax,
                                  ctp7=ctp7,
                                  csvFileNameFunc=csvFileNameFunc)
                    if g:
                        out[key] = g
                    else:
                        continue
    return out
