#!/usr/bin/env python

import common
import ROOT as r


def csvFileName(sn=0, gtx=0, run="", **_):
    fileName = "gtx%d_%s.csv" % (gtx, run)
    return "jumper_test/uHTR%03d/%s" % (sn, fileName)


def graphs(xMin=0.0, xMax=1.0):
    gtxs = [12, 21, 16]
    runs = ["a", "b", "c", "c2", "d"]
    
    out = {}
    for gtx in gtxs:
        for run in runs:
            key = (gtx, run)

            g = r.TGraph()
            g.SetName("%d_%s" % key)
            res = common.results(105, gtx, run, func=csvFileName)
            if not res:
                continue
            phases = [x[0] for x in res]
            pMin = min(phases)
            pMax = max(phases)
            
            assert (pMax - pMin), "%d_%d" % (pMax, pMin)
            for i, (phase, nErrors, ber) in enumerate(res):
                x = xMin + (xMax - xMin) * (phase - pMin) / (pMax - pMin)
                g.SetPoint(i, x, ber)
            out[key] = g
    return out


def summary(fileName="", berMin=None, berMax=1.0, nRuns=5, samplePoint=None):
    assert fileName
    assert berMin

    grs = graphs()
    c = r.TCanvas()
    c.Divide(2, 2)


    #h = r.TH2D("h", ";Horizontal Offset (UI); BER", 1, -0.5, 0.5, 1, berMin, 1.0)
    h = r.TH2D("h", ";Horizontal Offset (UI); BER", 1, 0.0, 1.0, 1, berMin, berMax)
    h.SetStats(False)

    keep = []
    drawn = {1: False,
             2: False,
             3: False,
             4: False
             }

    colorsLegs = {"a": (r.kBlack, "no jumper (1s)"),
                  "b": (r.kRed, "no jumper (pc) (1s)"),
                  "c": (r.kBlue, "jumper (1s)"),
                  "c2": (r.kGreen, "jumper (10s)"),
                  "d": (r.kMagenta, "no jumper (1s)"),
                  }

    line = r.TLine()
    line.SetLineStyle(2)
    for key, g in sorted(grs.iteritems()):
        #iPad = key[0] - 102
        iPad = {12: 1, 21: 2, 16:3}[key[0]]
        c.cd(iPad)
        if not drawn[iPad]:
            h2 = h.DrawClone()
            h2.SetTitle("uHTR 105 GTX %d" % key[0])
            keep.append(h2)
            drawn[iPad] = True
            leg = r.TLegend(0.14, 0.85, 0.44, 0.15)
            leg.SetBorderSize(0)
            leg.SetFillStyle(0)
            #leg.SetHeader("run")
            keep.append(leg)
            if samplePoint is not None:
                line.DrawLine(samplePoint, berMin, samplePoint, berMax)
                leg.AddEntry(line, "IBERT sampling point", "l")
            leg.Draw("same")

        run = key[1]
        color, name = colorsLegs[run]
        g.SetLineColor(color)
        g.SetMarkerColor(color)
        g.Draw("lpsame")
        
        r.gPad.SetLogy()
        r.gPad.SetTickx()
        r.gPad.SetTicky()
        
        leg.AddEntry(g, name, "lp")

#        if leg.GetNRows() == nRuns:
#            if samplePoint is not None:
#                line = r.TLine()
#                line.SetLineStyle(2)
#                line.DrawLine(samplePoint, berMin, samplePoint, berMax)
#                leg.AddEntry(line, "IBERT sampling point", "l")
#            leg.Draw("same")

    c.cd(0)
    c.Print(fileName)


if __name__ == "__main__":
    summary(fileName="uhtr_jumper.pdf", berMin=1.863e-12, berMax=1.0e-2, samplePoint=0.598)
