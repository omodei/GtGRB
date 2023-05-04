#
# $Header: /nfs/slac/g/glast/ground/cvs/GRBAnalysis-scons/GtGRB/python/GTGRB/parse_xml.py,v 1.3 2011/08/17 22:55:48 omodei Exp $
#

from xml.dom import minidom

class GRB_data(object):
    def __init__(self):
        pass

class GRBs(dict):
    conversion = {'TRIGGER_NUM' : (int, "%9i"),
#                  'GRB_MET' : (float, "%15.3f"),
#                  'GRB_RA' : (float, "%10.4f"),
#                  'GRB_DEC' : (float, "%10.4f"),
                  'GRB_MET' : (float, "%.6f"),
                  'GRB_RA' : (float, "%.4f"),
                  'GRB_DEC' : (float, "%.4f"),
                  'GRB_ERROR' : (float, "%10.4f"),
                  'GRB_T90' : (float, "%7.1f"),
                  'INDEX' : (str, "%10s"),
                  'LATFT1DATA' : (str, "%s"),
                  'LATFT2DATA' : (str, "%s"),
                  'LATFOV' : (float, "%104.f")}
    def __init__(self, xmlfile='GRBs.xml'):
        dict.__init__(self)
        self.doc = minidom.parse(xmlfile)
        self.grbs = self.doc.getElementsByTagName('GRB')
        for grb in self.grbs:
            element = grb.getElementsByTagName('INDEX')[0]
            name = apply(self.conversion['INDEX'][0], 
                         (element.firstChild.nodeValue,))
            self[name] = GRB_data()
            for item in self.conversion:
                if item != 'INDEX':
                    element = grb.getElementsByTagName(item)[0]
                    try:
                        value = apply(self.conversion[item][0], 
                                      (element.firstChild.nodeValue,))
                        self[name].__dict__[item] = value
                    except AttributeError:
                        pass

if __name__ == '__main__':
    import glob
    grbs = GRBs('GRBs.xml')

#    dirs = glob.glob('0*')
#    for item in dirs:
#        print item, grbs[item]
