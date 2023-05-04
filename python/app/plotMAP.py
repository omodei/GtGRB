#!/usr/bin/env python
from astropy.io import fits
import scipy as sp
import aplpy
import sys,os
import matplotlib
import matplotlib.colors as colors
import matplotlib.cm as cmx
from matplotlib import pyplot as plt
def readResults(results_file):
    _mydictionary={}
    for l in file(results_file,'r').readlines():
        var,val=l.split('=')
        #print var,val
        try:
            _mydictionary[var]=float(val)
        except:
            _mydictionary[var]=val
            pass
        pass
    return _mydictionary

def plotCMAP(cmap_file,evt_file,out_file=None,radius=None,txt=None,show=True):
    fig = plt.figure(figsize=(14, 10))    
    gc = aplpy.FITSFigure(cmap_file,figure=fig,subplot=[0.2,0.1,0.6,0.8],convention='calabretta')
    #gc.show_grayscale()
    draw_events=False
    if evt_file is not None and os.path.exists(evt_file):
        evt=fits.open(evt_file)['EVENTS'].data
        if evt.size>0:
            ra =evt.field('RA')
            dec=evt.field('DEC')
            log_ene=sp.log10(evt.field('ENERGY'))
            psf=sp.maximum(0.1,5.0*(100.0/evt.field('ENERGY')))
            #print ra,dec,log_ene
            cNorm  = colors.Normalize(vmin=sp.log10(60), vmax=sp.log10(300000))
            cmap = plt.get_cmap('jet')        
            scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cmap)
            _colors=scalarMap.to_rgba(log_ene)
            #gc.show_markers(ra,dec,s=100*psf,c=_colors,alpha=0.2)
            gc.show_markers(ra,dec,c=_colors,alpha=0.2)
            #for r,d,e,p in zip(ra,dec,evt.field('ENERGY'),psf): print r,d,e,p
            #for x,y,r,c in zip(ra,dec,psf,_colors): gc.show_circles(x,y,radius=r,facecolor=(0,0,0,0),edgecolor=c)
            draw_events=True
            pass
        pass
    else:
        gc.show_grayscale()
        pass
    gc.set_tick_labels_font(size='large')
    gc.set_axis_labels_font(size='large')

    gc.add_grid()
    gc.grid.set_color('grey')
    gc.grid.set_alpha(0.8)
    gc.grid.set_linestyle('dashed')
    gc.tick_labels.set_xformat('dd')
    gc.tick_labels.set_yformat('dd')
    #if radius is not None:
    #    gc.recenter(results['RA'],results['DEC'], radius=radius)
    if draw_events:
        ax2 = fig.add_axes([0.81, 0.1, 0.05, 0.8])
        plt.xticks(size=20)
        cb1 = matplotlib.colorbar.ColorbarBase(ax2, cmap=cmap,norm=cNorm)
        cb1.set_label('log$_{10}$ Energy [MeV]',size=30)
        ax2.xaxis.set_label_coords(0.05, 1.5)
        pass
    if txt is not None:  plt.annotate(txt,xy=(0.2,0.93),xycoords='figure fraction',fontsize=20,horizontalalignment='left',color='b')
    
    fig.canvas.draw()
    if out_file is not None:
        print "Saving plot as %s" % out_file
        fig.savefig(out_file)
        pass
    if show: plt.show()
    pass


if __name__=='__main__':
    
    cmap_file=None
    evt_file=None
    legend=None
    radius = None
    out_file=None
    show = True
    for i,a in enumerate(sys.argv):
        if a=='-cmap': cmap_file=sys.argv[i+1]
        if a=='-evt': evt_file=sys.argv[i+1]
        if a=='-out': out_file=sys.argv[i+1]
        if a=='-txt': legend=sys.argv[i+1]
        if a=='-radius' : radius = sys.argv[i+1]
        if a=='-show': show = sys.argv[i+1]
        pass
    if cmap_file is None:
        print 'Specify the input cmap file: ./plotMAP.py -evt_file <input_dir>'
        exit()

    plotCMAP(cmap_file,evt_file,out_file,radius,txt=legend,show=show)
    
