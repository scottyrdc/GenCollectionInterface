# Copyright(c)2008 Internet Archive. Software license GPL version 3.
 
# modified from the IACL bulk download example script by RSA 11/09
# takes the IACL booklist file supplied to the IACL4OPLC project
# and downloads all the books and covers.
 
# Multiple downloaders can be run at the same time using the startnum and endnum
# parameters, which will help to speed up the download process.
 
import csv
import os
import commands
import sys
 
startnum = 0
endnum   = 999999
 
filenum = startnum
iaclBookList = open('iaclBookList.txt','r').readlines()

for line in iaclBookList:
    lst = line.split() 
    if len(lst) != 2: # format is <olid> <iaid>
	  continue
    id = lst[1]
    print id
    ollst = lst[0].split('/')
    print ollst
    if len(ollst) != 3: # format is '/b/<olid>'
	  continue
    olid = ollst[2]
    dirnum = "%09d"%filenum
    print "downloading book #%s, id=%s" % (dirnum, id)
 
    path = 'djvu/'
 
    if not os.path.exists(path):
        os.makedirs(path)
 
 
    url = "http://www.archive.org/download/%s/%s.djvu" % (id, id)
    dlpath = "%s/%s.djvu"%(path, id)
 
    if not os.path.exists(dlpath):
        #urllib.urlretrieve(url, dlpath)
        #use rate limiting to be nicer to the cluster
        (status, output) = commands.getstatusoutput("""wget '%s' -O '%s' --limit-rate=250k --user-agent='IA Bulk Download Script' -q""" % (url, dlpath))
        assert 0 == status
    else:
        print "\talready downloaded, skipping..."
# get covers
    dirnum = "%09d"%filenum
    print "downloading cover #%s, id=%s" % (dirnum, id)
 
    path = 'covers/'
 
    if not os.path.exists(path):
        os.makedirs(path)
 
 
    url = "http://covers.openlibrary.org/b/OLID/%s-M.jpg" % (olid)
    dlpath = "%s/%s.jpg"%(path, id)
 
    if not os.path.exists(dlpath):
        #urllib.urlretrieve(url, dlpath)
        #use rate limiting to be nicer to the cluster
        (status, output) = commands.getstatusoutput("""wget '%s' -O '%s' --limit-rate=250k --user-agent='IA Bulk Download Script' -q""" % (url, dlpath))
        assert 0 == status
    else:
        print "\talready downloaded, skipping..."
 
 
    filenum+=1
    if (filenum > endnum):
        sys.exit()
