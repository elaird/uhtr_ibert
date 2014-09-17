import csv
import ROOT as r


def versions(sn=None):
    if 103 <= sn <= 110:
        return "preprod. uHTR v1.3r"
    if 111 <= sn <= 114:
        return "HF prod. uHTR v1.4"
    if 13 <= sn <= 16:
        return "HBHE preprod. uHTR v1.5"
    return ""


def results(sn, gtx, run, ctp7=False):
    d = {-5: " RX Sampling Point(tap)",
          -2: " # Errs",
          -1: " BER",
          }
    if ctp7:
        del d[-2]
        d[-3] = " # Errs1"
        okLen = 10
    else:
        okLen = 11

    if ctp7:
        fileName = "ctp7/%03d/%s_sweep_results%s.csv" % (sn, gtx, run)
    else:
        fileName = "optical_loopback/uHTR%03d/%s_sweep_results%s.csv" % (sn, gtx, run)

    out = []
    try:
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


def graphs(xMin=0.0, xMax=1.0, uhtrs=[], runs=[""], ctp7=False):
    gtxes = range(113, 116) if ctp7 else range(112, 118)

    out = {}
    for uhtr in uhtrs:
        for gtx100 in gtxes:
            for gtx4 in range(4):
                for run in runs:
                    key = (uhtr, gtx100, gtx4, run)

                    g = r.TGraph()
                    gtx = "%s%d_%d" % ("GTH" if ctp7 else "GTX", gtx4, gtx100)
                    g.SetName("%d_%s_%s" % (uhtr, gtx, run))
                    res = results(uhtr, gtx, run, ctp7=ctp7)
                    if not res:
                        continue
                    phases = [x[0] for x in res]
                    pMin = min(phases) if xMin else 0
                    pMax = max(phases) if xMin else 127

                    assert (pMax - pMin), "%d_%d" % (pMax, pMin)
                    for i, (phase, nErrors, ber) in enumerate(res):
                        x = xMin + (xMax - xMin) * (phase - pMin) / (pMax - pMin)
                        g.SetPoint(i, x, ber)
                    out[key] = g
    return out
