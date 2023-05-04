import sys

def gt_print(amessage,chatter=2,die=False,print_border=False):
    '''    
    Function that can be used for printing out messages. 
    print_border prints a nice border around your message
    chatter>3 prints the filename of the file
    die==True exits
    We can set it up for printing in color too.
    '''
    msg="%s: %s" %(sys._getframe(1).f_code.co_name,amessage)
    
    if print_border:
	border=""
	msg="====  "+msg
	for i in range(0,len(msg)+5):
	    border+="="
	print border

    print msg
    if chatter>3: print "Message from file %s" %sys._getframe(1).f_code.co_filename
    if print_border:
	print border
    if die:
	exit()
##########################################################