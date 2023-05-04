#!/usr/bin/env python
'''Selection of tools that deal with calculation of individual event probabilities'''

from GtGRB_IO import *
import astropy.io.fits as pyfits

def gt_probs_Parse_File(probs_fits_file,probs_txt_file_out="",t_offset=0,print_probs=False,chatter=2):
    '''parse a fits file created with gtsrcprob and return a list with event times,energies,probabiblities and a text filename with the same data
       t_offset is a MET offset to be subtracted from all reported times.
       prob_txt_file_out is an optional name of a txt file in which the prob data will be also dumped.
    '''
    nevts = 0

    if probs_txt_file_out=="":
	probs_txt_file_out = probs_fits_file.replace('.fits','.txt')

    if chatter>1: gt_print('Reading probs from file %s source GRB' %probs_fits_file,chatter=chatter)
    hdulist = pyfits.open(probs_fits_file)
    nevts   = hdulist['EVENTS'].header['NAXIS2']
    #except:
#	gt_print('Error opening file...',chatter=chatter)
#        return None

    if nevts==0:
	gt_print("No events in file %s!" %probs_fits_file,chatter=chatter)
    pass

    data   = hdulist['EVENTS'].data
    time   = data.field('TIME')
    energy = data.field('ENERGY')
    prob   = data.field('GRB')

    txt= '#%10s %15s %10s\n' %('TIME','ENERGY','PROB')


    _prob=[]
    _time=[]
    _energy=[]
    for i in range(nevts):
        txt+='%10.2f %15.1f %10.3f\n' %(time[i]-t_offset,energy[i],prob[i])
	_time.append(time[i]-t_offset)
	_prob.append(prob[i])
	_energy.append(energy[i])
    pass
    if print_probs: print txt
    outFile=file(probs_txt_file_out,'w')
    outFile.write(txt)
    outFile.close()
    hdulist.close()
    
    ev_data={}
    ev_data['TIME']=_time
    ev_data['PROBABILITY']=_prob
    ev_data['ENERGY']=_energy
    ev_data['PROB_TXT_FILE_OUT']=probs_txt_file_out
    return ev_data
    

    
def GetEventWithMaxEnergy(probs_fits_file,t_offset=0,minene=0,minprob=0,print_probs=False,chatter=2):

    ev_data=gt_probs_Parse_File(probs_fits_file=probs_fits_file,t_offset=t_offset,print_probs=print_probs,chatter=chatter)

    probs_txt_fits_file=ev_data['PROB_TXT_FILE_OUT']
    prob  =ev_data['PROBABILITY']
    energy=ev_data['ENERGY']
    time  =ev_data['TIME']
    if minprob==0 and prob.max()>0.9: minprob=0.9
    txt= '#%10s %15s %10s\n' %('TIME','ENERGY','PROB')
    energy_max      = 0
    time_max        = 0
    probability_max = 0
    N_threshold     = 0
    for i in range(nevts):
        if prob[i] > 0.9: N_threshold += 1
        if (prob[i]>minprob and energy[i]>minene):
            relative_time = time[i]-t0
            txt+='%10.2f %15.1f %10.3f\n' %(relative_time,energy[i],prob[i])
            if energy[i] > energy_max:
                energy_max = energy[i]
                time_max   = relative_time
                prob_max   = prob[i]
                pass
            pass
        pass
    txt+='#--------------------------------------------------\n'
    txt+='# NUMBER OF EVENTS ABOVE THRESHOLD: %d' % N_threshold
    txt+='# ENERGY MAX EVENT: %.2f MeV, %.3f s, %.4f \n'%(energy_max,time_max,prob_max)
    txt+='#--------------------------------------------------\n'
    outFile=file(outFileName,'w')
    outFile.write(txt)
    outFile.close()
    myres={}
    myres['gtsrcprob_File']=outFileName
    myres['gtsrcprob_Emax']=energy_max
    myres['gtsrcprob_Tmax']=time_max
    myres['gtsrcprob_Pmax']=prob_max
    myres['gtsrcprob_Nthr']=N_threshold
    print txt
    return myres
