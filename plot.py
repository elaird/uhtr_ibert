#!/usr/bin/env python

import os
import common
import ROOT as r


def summary(fileName="", uhtrs=[], runs=[""], pad=lambda x: 1,
            berMin=1.863e-13, berMax=1.0e-2,
            ctp7=False, begin=False, end=False):

    assert fileName
    assert berMin
    assert runs

    if ctp7:
        xMin = -0.5
        xMax = 0.5
        samplePoint = None
        berMax = 1.0
    else:
        xMin = 0.0
        xMax = 1.0
        samplePoint = 0.598

    grs = common.graphs(uhtrs=uhtrs,
                        runs=runs,
                        xMin=xMin,
                        xMax=xMax,
                        ctp7=ctp7)
    c = r.TCanvas()
    c.Divide(2, 2)

    if begin:
        c.cd(0)
        c.Print(fileName+"[")

    h = r.TH2D("h", ";Horizontal Offset (UI); BER", 1, xMin, xMax, 1, berMin, berMax)
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
            title = "uHTR%d - CTP7" % uhtr if ctp7 else "%s, optical loop-back" % common.versions(uhtr)
            h2.SetTitle("%s, 6.4 Gbps" % title)
            keep.append(h2)

            drawn[iPad] = True
            if ctp7:
                leg = r.TLegend(0.44, 0.85, 0.64, 0.15)
            else:
                leg = r.TLegend(0.14, 0.85, 0.44, 0.15)
            leg.SetBorderSize(0)
            leg.SetFillStyle(0)
            if ctp7:
                leg.SetHeader("CTP7 GTH")
            keep.append(leg)
            if samplePoint is not None:
                line.DrawLine(samplePoint, berMin, samplePoint, berMax)
                leg.AddEntry(line, "IBERT sampling point", "l")
            leg.Draw("same")

        offset = 113 if ctp7 else 112
        iColor = 1 + gtx4 + 4*(gtx100 - offset)
        color = r.TColor.GetColorPalette(2 * iColor)

        g.SetLineStyle(1 + ((iColor-1) % 3))
        g.SetLineColor(color)
        g.SetMarkerColor(color)
        g.Draw("lsame")
        
        r.gPad.SetLogy()
        r.gPad.SetTickx()
        r.gPad.SetTicky()
        
        name = "_".join(g.GetName().split("_")[1:3])
        if run == "_1":
            name += " (100s)"
        elif not ctp7:
            name += " (1s)"
        leg.AddEntry(g, name, "l")
        leg.SetHeader("%d" % (leg.GetNRows() - 2))

    c.cd(0)
    c.Print(fileName)

    if end:
        c.cd(0)
        c.Print(fileName+"]")


def ctp7():
    fileName = "uhtr_ctp7.pdf"
    summary(fileName=fileName,
            berMin=1.863e-10,
            uhtrs=[103, 104, 105, 106],
            pad=lambda uhtr: uhtr - 102,
            ctp7=True)


def compare_versions():
    fileName = "compare_versions.pdf"
    pad = lambda uhtr: 1 + {110:0, 111:1, 14:2}[uhtr]
    summary(uhtrs=[110, 111, 14], begin=True, end=True, fileName=fileName, pad=pad)
    os.system("cp -p %s ~/public/html/tmp/" % fileName)


def sns(dir="optical_loopback", snMin=115):
    out = []
    for subdir in os.listdir(dir):
        try:
            sn = int(subdir[-3:])
            if snMin <= sn:
                out.append(sn)
        except:
            print "Skipping %s" % subdir
    return sorted(out)


def padDct(l=[]):
    out = {}
    for i, x in enumerate(l):
        out[x] = 1 + i
    return out


def all_uhtrs():
    fileName = "all_uhtrs.pdf"
    fullSnList = sns()
    runs = [""]

    iMax = len(fullSnList) - 1
    iMax -= (iMax % 4)
    for i, sn in enumerate(fullSnList):
        if i % 4:
            continue

        snList = []
        for j in range(i, min([i + 4, len(fullSnList)])):
            snList.append(fullSnList[j])

        dct = padDct(snList)
        pad = lambda uhtr: dct[uhtr]
        summary(uhtrs=snList,
                fileName=fileName,
                pad=pad,
                runs=["latest"],  # magic string
                begin=(not i),
                end=(i==iMax),
                )
    os.system("cp -p %s ~/public/html/tmp/" % fileName)


if __name__ == "__main__":
    r.gStyle.SetPalette(1)
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000

    #ctp7()
    #compare_versions()
    all_uhtrs()
