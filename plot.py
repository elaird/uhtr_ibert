#!/usr/bin/env python

import os
import common
import ROOT as r


def summary(fileName="", uhtrs=[], runs=[""], pad=lambda x: 1,
            berMin=1.863e-13, berMax=1.0e-2, samplePoint=0.598,
            begin=False, end=False):
    assert fileName
    assert berMin
    assert runs

    grs = common.graphs(uhtrs=uhtrs, runs=runs)
    c = r.TCanvas()
    c.Divide(2, 2)

    if begin:
        c.cd(0)
        c.Print(fileName+"[")

    h = r.TH2D("h", ";Horizontal Offset (UI); BER", 1, 0.0, 1.0, 1, berMin, berMax)
    h.SetStats(False)

    keep = []
    drawn = {1: False,
             2: False,
             3: False,
             4: False
             }

    line = r.TLine()
    line.SetLineStyle(2)

    for (uhtr, gtx100, gtx4, run), g in sorted(grs.iteritems()):
        iPad = pad(uhtr)
        c.cd(iPad)
        if not drawn[iPad]:
            h2 = h.DrawClone()
            h2.SetTitle("%s, optical loop-back, 6.4 Gbps" % common.versions(uhtr))
            keep.append(h2)
            drawn[iPad] = True
            leg = r.TLegend(0.14, 0.85, 0.44, 0.15)
            leg.SetBorderSize(0)
            leg.SetFillStyle(0)
            leg.SetHeader("uHTR s/n %d" % uhtr)
            keep.append(leg)
            if samplePoint is not None:
                line.DrawLine(samplePoint, berMin, samplePoint, berMax)
                leg.AddEntry(line, "IBERT sampling point", "l")
            leg.Draw("same")


        iColor = 1 + gtx4 + 4*(gtx100 - 112)
        color = r.TColor.GetColorPalette(2 * iColor)
        g.SetLineStyle(1 + ((iColor-1) % 3))
        g.SetLineColor(color)
        g.SetMarkerColor(color)
        g.Draw("lsame")
        
        r.gPad.SetLogy()
        r.gPad.SetTickx()
        r.gPad.SetTicky()
        
        name = "GTX%d_%d" % (gtx4, gtx100)
        if run == "_1":
            name += " (100s)"
        else:
            name += " (1s)"
        leg.AddEntry(g, name, "l")

    c.cd(0)
    c.Print(fileName)

    if end:
        c.cd(0)
        c.Print(fileName+"]")


def reworked():
    fileName = "reworked_uhtrs.pdf"
    runs = ["", "_1"]
    pad = lambda uhtr: 1 + (uhtr - 103) % 4
    summary(uhtrs=[103, 104, 106], begin=True, runs=runs, fileName=fileName, pad=pad)
    summary(uhtrs=[107, 109, 110], end=True,   runs=runs, fileName=fileName, pad=pad)
    os.system("cp -p %s ~/public/html/tmp/" % fileName)


def new():
    fileName = "new_uhtrs.pdf"
    pad = lambda uhtr: 1 + {110:0, 111:1, 14:2}[uhtr]
    summary(uhtrs=[110, 111, 14], begin=True, end=True, fileName=fileName, pad=pad)
    os.system("cp -p %s ~/public/html/tmp/" % fileName)


if __name__ == "__main__":
    r.gStyle.SetPalette(1)
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000

    reworked()
    new()
