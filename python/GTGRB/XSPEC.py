import os

class Parameter:
    def __init__(self,name,value,error,errorL,errorH,searchError):
        self.Name = name
        self.Unit = ''
        self.Value = value
        self.Error = error
        self.ErrorL = errorL
        self.ErrorH = errorH
        self.SearchError = searchError

        self.Good = True
        if 'T' in self.SearchError:
            self.Good = False

class FitModel:

    def __init__(self,name) :
        self.Name = name
        self.PrmNumber = 0
        self.Prm = []

    def ReadModel(self,local_model_path,local_model_name):

        if local_model_path and local_model_name :
            filename = local_model_path + '/' + local_model_name + '.dat'
            if os.path.isfile(filename):
                self.SearchModel(filename)
            else:
                print 'Local models definition file ' + filename + ' not found'

        if not self.PrmNumber :
            comd = 'find ' + os.getenv('HEADAS') + '/.. -name "model.dat"'
            a = os.popen(comd)
            b = a.read()
            a.close()
            filename = b.split('\n')[0]
            if os.path.isfile(filename):
                self.SearchModel(filename)
            else:
                print 'XSPEC models definition file model.dat not found in ' + os.getenv('HEADAS') + '/../'

                
    def SearchModel(self,filename):

        file = open(filename,'r')

        line = file.readline()
        while line and not self.PrmNumber :
            if line.split():
                #print line
                if self.Name == line.split()[0][:len(self.Name)] :
                    self.PrmNumber = int(line.split()[1])
                    for i in range(self.PrmNumber):
                        line = file.readline()
                        self.Prm.append(line.split()[0])
                break
                        
            line = file.readline()
        file.close()

        if not self.PrmNumber  :
            print 'Model ' + self.Name + ' not found in definition file ' + filename
        

class GRB_xspec:

    def __init__(self):
        self.Name = ''
        self.Add = ''
        self.FixedParameters = {}
        self.Parameters = {}
        self.Model = ''
        self.StatVal = 0
        self.DoF = 0
        self.HasFit = False

    def ReadFile(self,filename = 'fit_result.dat'):

        file = open(filename,'r')

        while '===== fit result' not in file.readline():
            pass

        self.Model = file.readline()

        while '----- parameters' not in file.readline():
            pass

        line = file.readline()

        while '-----' not in line:

            l = (line.rstrip('\n')).split()

            parameter = l[0]
            value = file.readline()
            errors = file.readline()

            print 'got param ' + parameter

            if 'fixed' in errors:
                self.FixedParameters[parameter] = float(value.split()[0])
            else:
                val = float(value.split()[0])
                errorL = val - float(errors.split()[0])
                errorH = float(errors.split()[1])-val
                error = (errorH+errorL)/2
                self.Parameters[parameter] = Parameter(parameter,val,error,errorL,errorH,errors.split()[2])
                if len(l)>1:
                    self.Parameters[parameter].Unit = l[1]

            line = file.readline()

        while '----- statistics' not in line:
            line = file.readline()

        line = file.readline()
        self.StatVal = float(line.split()[0])

        while '----- dof' not in line:
            line = file.readline()

        line = file.readline()
        self.DoF = float(line.split()[0])

## defines BGO related XSPEC commands
#
# ignore E<150keV and E>30MeV
# rebin 5 8
def add_BGO_related(number, f):
    datstr = 'ignore ' + str(number) + ':**-150. \n'
    f.write(datstr)
    datstr = 'ignore ' + str(number) + ':30000.-** \n'
    f.write(datstr)
    datstr = 'setplot rebin 5 8  ' + str(number) + ' \n'
    f.write(datstr)

## defines NaI related XSPEC commands
#
# ignore E>1MeV
# rebin 5 5 
def add_NaI_related(number, f):
    datstr = 'ignore ' + str(number) + ':1000.-** \n'
    f.write(datstr)
    datstr = 'setplot rebin 5 5  ' + str(number) + ' \n'
    f.write(datstr)

def MakeScript(PHA, RSP, BAK, Detectors,
               model = 'powerlaw',
               local_model_name='',
               local_model_path='',
               statistics = 'cstat',
               method = 'leven',
               script = 'fit.xcm',
               area = True,
               goodness = 0,
               deltafit = 1.,
               outfile = 'fit_result.dat',
               parameters = {},
               FitIter = 100,
               CalcFlux = True,
               SpectrumFileName = 'fit.ps') :

    
    for det in PHA:
        print det
    f = open(script,'w')

#    f.write('query yes \n')

    datstr = 'data '
    respstr = 'response '
    bakstr = 'backgrnd '
 
    groupNumbers = {}
    count = 1

    for detector in Detectors:
        datstr = datstr + PHA[detector] + ','
        respstr = respstr + RSP[detector] + ','
        bakstr = bakstr + BAK[detector] + ','
        groupNumbers[detector] = count
        count = count + 1

    datstr = datstr[:-1]+';'
    respstr = respstr[:-1]+';'
    bakstr = bakstr[:-1]+';'

    f.write(datstr + '\n')
    f.write(respstr + '\n')
    f.write(bakstr + '\n')

    for detector in Detectors:
        if detector[0] == 'B':
            add_BGO_related(groupNumbers[detector],f)
        if detector[0] == 'N':
            add_NaI_related(groupNumbers[detector],f)

    if local_model_path != '' and local_model_name != '':
        f.write('lmod ' + local_model_name + ' ' + local_model_path + '\n')

    # general stuff
    f.write('setplot energy \n')
    if area:
        f.write('setplot area \n')

    f.write('model '+model+' & /* \n')

    if len(parameters):
        for i in range(len(parameters)):
            fitmodel = FitModel(model)
            fitmodel.ReadModel(local_model_path,local_model_name)

            if parameters.keys()[i] in fitmodel.Prm :
                f.write('newpar '+ str(fitmodel.Prm.index(parameters.keys()[i])) + ' ' + str(parameters.values()[i]) +' \n')            
            elif parameters.keys()[i] == 'norm' :
                f.write('newpar '+ str(fitmodel.PrmNumber+1) + ' ' + str(parameters.values()[i]) +' \n')
            else :
                print 'Parameter ' + parameters.keys()[i] + ' not defined in model ' + model + ' : ignored'

    #f.write('renorm \n')
    f.write('statistic '+ statistics +' \n')
    if  method != '' :
        f.write('method '+ method + ' \n')
    
    f.write('fit ' + str(FitIter) + ' \n')

    outputdir = os.path.split(outfile)[0]
    if outputdir == '':
        outputdir = '.'

    f.write('tclout model                          \n')
    f.write('set mod [string trim $xspec_tclout]    \n')

    if deltafit>0:
        f.write('query yes \n')
        f.write('set pars [tcloutr modpar]              \n' + \
                'error maximum 100 ' + str(deltafit) + ' 1-$pars \n')

    if (goodness > 0):
        f.write('goodness ' + str(goodness) + '\n')

    f.write('tclout energies                     \n' + \
            'set emin [lindex $xspec_tclout 0]   \n' + \
            'set emax [lindex $xspec_tclout end] \n')

#     if len(Detectors)>1:
#         f.write('dummyrsp $emin $emax \n')

    if CalcFlux:
        f.write('flux $emin $emax err 1000 68.3      \n')

#     if len(Detectors)>1:
#         f.write('response \n')

    IncludeWriteResults(f,outfile,CalcFlux)

    if SpectrumFileName.upper()=='X':
        f.write('cpd /xw \n')
        f.write('plot ld ratio \n')
    else:
        f.write('cpd ' + SpectrumFileName + '/cps \n')
        f.write('plot ld ratio \n')
        f.write('exit \n')

    f.close()
    
def IncludeWriteResults(f, outfile = 'fit_result.dat', CalcFlux = True):

    # Open the file to put the results in.
    f.write('set fileid [open '+outfile+' w]    \n')
    
    # get fit results
    f.write('puts $fileid "===== fit result"                     \n' + \
            'tclout model                          \n' + \
            'set mod [string trim $xspec_tclout]    \n' + \
            'puts $fileid "$mod"                     \n' + \
            'puts $fileid "----- parameters"                     \n' + \
            'set comps [tcloutr modcomp]              \n' + \
            'set pars [tcloutr modpar]              \n' + \
            'for {set i 1} {$i <= $pars} {incr i} { \n' + \
            '  tclout pinfo $i                        \n' + \
            '  set pn [string trim $xspec_tclout]     \n' + \
            '  if {$comps>1} then {                    \n' + \
            '    puts $fileid "$i$pn"                      \n' + \
            '  } else {                                 \n' + \
            '    puts $fileid "$pn"                     \n' + \
            '  }                                      \n' + \
            '  tclout param $i                        \n' + \
            '  set par [string trim $xspec_tclout]    \n' + \
            '  puts $fileid "$par"                    \n' + \
            '  set num  [llength $xspec_tclout]      \n' + \
            '  if {$num > 2} then {                   \n' + \
            '    tclout error $i                        \n' + \
            '    set err [string trim $xspec_tclout]    \n' + \
            '    puts $fileid "$err"            \n' + \
            '    } else {            \n' + \
            '    puts $fileid "fixed"            \n' + \
            '    }            \n' + \
            '}                                      \n' + \
            'puts $fileid "----- covariance"                      \n' + \
            'tclout covariance                      \n' + \
            'set cov [string trim $xspec_tclout]    \n' + \
            'puts $fileid "$cov"                    \n' + \
            'puts $fileid "----- simpars"                      \n' + \
            'tclout simpars                      \n' + \
            'set god [string trim $xspec_tclout]    \n' + \
            'puts $fileid "$god"                    \n' + \
            'puts $fileid "----- statistics"                      \n' + \
            'tclout stat                      \n' + \
            'set stat [string trim $xspec_tclout]    \n' + \
            'puts $fileid "$stat"                    \n' + \
            'puts $fileid "----- dof"                      \n' + \
            'tclout dof                      \n' + \
            'set dof [string trim $xspec_tclout]    \n' + \
            'puts $fileid "$dof"                    \n' + \
            'puts $fileid "-----"                      \n' + \
            'puts $fileid "^^^^^"                      \n')
    
    # get spectrum
    f.write('puts $fileid "===== spectrum"                     \n' + \
            'set nospec [tcloutr datasets]              \n' + \
            'for {set i 1} {$i <= $nospec} {incr i} { \n' + \
            '  puts $fileid "----- spectrum $i"                     \n' + \
            '  tclout plot ld x $i                  \n' + \
            '  set e [string trim $xspec_tclout]    \n' + \
            '  puts $fileid "$e"                    \n' + \
            '  tclout plot ld xerr $i                  \n' + \
            '  set ee [string trim $xspec_tclout]    \n' + \
            '  puts $fileid "$ee"                    \n' + \
            '  tclout plot ld y $i                  \n' + \
            '  set y [string trim $xspec_tclout]    \n' + \
            '  puts $fileid "$y"                    \n' + \
            '  tclout plot ld yerr $i                  \n' + \
            '  set ye [string trim $xspec_tclout]    \n' + \
            '  puts $fileid "$ye"                    \n' + \
            '  plot ld ratio $i                \n' + \
            '}                                      \n' + \
            'puts $fileid "^^^^^"                      \n')
    
    # get flux
    f.write('puts $fileid "===== flux"                     \n' + \
            'flux 50. 300.                                   \n' + \
            'set nospec [tcloutr datasets]              \n' +
            'for {set i 1} {$i <= $nospec} {incr i} { \n' + \
            ' tclout flux $i                     \n' + \
            ' set god [string trim $xspec_tclout]    \n' + \
            ' puts $fileid "$god"                    \n' + \
            '}                                      \n' + \
            'flux 100000. 1000000000.                  \n' + \
            'set nospec [tcloutr datasets]              \n' +
            'for {set i 1} {$i <= $nospec} {incr i} { \n' + \
            ' tclout flux $i                     \n' + \
            ' set god [string trim $xspec_tclout]    \n' + \
            ' puts $fileid "$god"                    \n' + \
            '}                                      \n' + \
            'puts $fileid "^^^^^"                      \n')

    if CalcFlux:
        f.write('for {set i 1} {$i <= $nospec} {incr i} { \n' + \
                '  tclout flux $i                 \n')
        f.write('  set god [string trim $xspec_tclout]    \n' + \
                '  puts $fileid "$god"                    \n' + \
                '}                                      \n')

        f.write('if {$nospec == 1} then {  \n' + \
                '  if {$emin <= 30000} then {  \n' + \
                '    flux 30000 $emax err  \n' + \
                '    tclout flux   \n' + \
                '    puts $fileid "----- flux30"        \n' + \
                '    set god [string trim $xspec_tclout]    \n' + \
                '    puts $fileid "$god"                    \n' + \
                '  }                                      \n' + \
                '  if {$emin <= 100000} then {  \n' + \
                '    flux 100000 $emax err  \n' + \
                '    tclout flux   \n' + \
                '    puts $fileid "----- flux100"        \n' + \
                '    set god [string trim $xspec_tclout]    \n' + \
                '    puts $fileid "$god"                    \n' + \
                '  }                                      \n' + \
                '}                                      \n')
        
    else:
        f.write('for {set i 1} {$i <= $nospec} {incr i} { \n')
        f.write('  puts $fileid "0 0 0 0 0 0"                    \n' + \
                '}                                      \n')
    
    f.write('puts $fileid "^^^^^"                      \n')
 
    # Close the file.
    f.write('close $fileid\n')


def Fit(script = 'fit.xcm'):
    print 'executing...',script
    os.system('xspec - '+script)
    
def Test(pha,rsp,bak,model='powerlaw'):

    PHA = {}
    RSP = {}
    BAK = {}

    PHA['LAT'] = pha
    RSP['LAT'] = rsp
    BAK['LAT'] = bak

    det = ['LAT']
    MakeScript(PHA,RSP,BAK,det, goodness = 1000, model = model)
    Fit()

def TestIC():

    PHA = {'B1': 'GRB081117953_B1.pha',   \
           'LAT': 'GRB081117953_lat.pha', \
           'N6': 'GRB081117953_N6.pha',   \
           'N7': 'GRB081117953_N7.pha'}

    RSP = {'B1': '../data/GRB081117953/GLG_CSPEC_B1_BN081117953_V02.RSP', \
           'LAT': 'GRB081117953_lat.rsp',                                 \
           'N6': '../data/GRB081117953/GLG_CSPEC_N6_BN081117953_V02.RSP', \
           'N7': '../data/GRB081117953/GLG_CSPEC_N7_BN081117953_V02.RSP'}

    BAK = {'B1': '../data/GRB081117953/GLG_BCK_B1_BN081117953_V02.BAK', \
           'LAT': '', \
           'N6': '../data/GRB081117953/GLG_BCK_N6_BN081117953_V02.BAK', \
           'N7': '../data/GRB081117953/GLG_BCK_N7_BN081117953_V02.BAK'}

    Detectors = ['N7', 'N6', 'B1', 'LAT']

    params = ['-0.742123       0.01        -10         -3          2          5',
              '-2.03805       0.01        -10         -5          2         10',
              '187.272         10         10         10       1000       1000',
              '0.12851       0.01          0          0      1e+24      1e+24',
              '-0.880487       0.01        -10         -3          2          5',
              '-1.64422       0.01        -10         -5          2         10',
              '52384.9       1000      10000      10000      1e+06      1e+06',
              '0.00775843       0.01          0          0      1e+24      1e+24',
              '1.92374e+07      10000     100000     100000      1e+09      1e+09',
              '1.28363e+07      10000     100000     100000      1e+09      1e+09']


    MakeScript(PHA, RSP, BAK, Detectors,model='grbm + grbm*highecut',\
               script='test.xcm',outfile='test.dat',\
               parameters=params, FitIter=600)

    Fit('test.xcm')


def make_fit(model='grbm',local_model_name='',local_model_path='',*kargs,**kwargs):

    # should add a test for use or not of a local model, for testing or not the MODELS variable:
    # if len(kargs) == 1 and kargs[0].detector_name == 'LAT'
    # and in case you have local models to fit both GBM and LAT it wont work...

    # list of detectors and dictionary of parameters to give XSPEC.MakeScript

    if not len(kargs):
        print 'Please specify at least one detector'

    else:

        Dets=[]
        PHAfiles={}
        RSPfiles={}
        BAKfiles={}
        
        bursts=[]
        
        scriptname = ''
        outputfile = ''
        specfile = ''
        
        for det in kargs:
            Dets.append(det.detector_name)
            PHAfiles[det.detector_name]=det.sp_outFile
            RSPfiles[det.detector_name]=det.rsp_File
            BAKfiles[det.detector_name]=det.back_File
            
            scriptname += det.detector_name + '_'
            outputfile += det.detector_name + '_'
            specfile += det.detector_name + '_'
            
            bursts.append(det.grb_name)

        if bursts.count(det.grb_name) != len(Dets):
            print 'I think you are mixing several GRBs...'
            print bursts

        #elif 'LAT' in Dets and Dets.index('LAT') != len(Dets)-1:
            #print 'You should sort your detectors list as follows: LAT last, always' # not so necessary, in fact...
        else:
            scriptname = det.GRB.out_dir+'/'+scriptname+'fit_'+model+'.xcm'
            outputfile = det.GRB.out_dir+'/'+outputfile+'fit_'+model+'.dat'
            specfile = det.GRB.out_dir+'/'+specfile+'fit_'+model+'.ps'

            pars = []
            parn = []
            i = 1
            if len(kwargs.keys()):
                for par in kwargs.keys():
                    pars.append(str(kwargs[par]))
                    parn.append(str(i))
                    i += 1
                    
                
            MakeScript(PHAfiles,
                       RSPfiles,
                       BAKfiles,
                       Dets,
                       area = False,
                       model = model,
                       local_model_name = local_model_name,
                       local_model_path = local_model_path,
                       statistics = 'cstat',
                       script = scriptname,
                       outfile = outputfile,
                       CalcFlux = True,
                       paramnumbers = parn,
                       parameters = pars,
                       SpectrumFileName = specfile,
                       deltafit=1.)
            
            Fit(scriptname)
            
