#!/usr/bin/python
# genCollectionInterface.py
# generate a web interface from the result of a search on the internet archive
# dumped as a csv file, organized into categories from the category list. The 
# categories are searched for in the subject field of the csv dump
# all un-categorized data is saved in 'otherCategory.html'
#
# 1) extract header, body, and etc from the template
# 2) output header
# 3) start body
# 4) for each entry in the csv file
#     parse out the fields, save in list, categorize
#     build the appropriate inteface element, save in categories lists
# 5) buildIntefaceElement(meta)
#     get the cover using the OLID map and the OL Cover API
#     create link to bookreader with URL of book using cover as "button"
#     make the title, display under cover
#     make a tooltip string using the metadata
# 6) generate the body using the interface elements above, one page for each category
# 
#
#        
import os
import sys
import csv
import re

def usage():
	print 'usage: genweb.py [options] <input csv> <input categories file> [<output.html>]'
	print '   options:'
	print '      -attached-storage: generate links for attached storage solution'

# creates the interface elements (html, links, tooltip stuff, cover img link, etc) given
# a list of the metadata elements

def buildInterfaceElement(outfile,m):
	# build the  output for the div containg book cover, title, link
	global attStorage # attached storage link switch
	# open the div template

	divstr = open('divtmpl.html.tmpl','r').read();

	# replace the DOM element id with a generated one, use the book id?
	divstr = re.sub('\$idstr', m[4],divstr)

	# replace the cover img src with the one for this book
	# this will use the mapping from iacl to open library id's from the 
	# original book list

	olid =mapIaclIDToOLID(m[4])
	if  olid != '':
		if attStorage == 0:
			coverurl = getCoverUrl(olid)
		else:
			coverurl = getCoverUrl(m[4])
	else: coverurl = ''
	divstr = re.sub('\$coverstr',coverurl,divstr)

	#replace the iacl lookup id with the one for this book in the link

	if attStorage == 0:
		#switch which of the following divstr assignment is commented to select what type of link
		# interface to create
		# 1. link to download djvu
		# divstr = re.sub('\$iaclid',"http://archive.us.org/stream/" + m[4] + "/" + m[4] + ".djvu",divstr)
		# 2. link to the embedded bookreader
	
		divstr = re.sub('\$iaclid', "http://www.us.archive.org/GnuBook/GnuBookEmbed.php?id=" +  m[4], divstr)
	else:
		# 3. link to already downloaded content on attached storage
	
		divstr = re.sub('\$iaclid',"djvu/"  + m[4] + ".djvu",divstr)

	#replace title

	# tear the titles down to max 8 words
	# split first at ':', then max 8 words of what is left of ':'
	l = (m[1].split(':',1)[0]).split(' ',8)[0:7]
	title = ''
	for w in l:
		title = title + w + ' '
	divstr = re.sub('\$title',title,divstr)
	outfile.write(divstr)


# build the tooltip list for each output file
# format of Tip:
# new Tip('<dom_id_of_element>', '<b>Full Title:<\/b> Adventures of Huckleberry Finn (Tom Sawyer\'s comrade)...<br \/><br \/><b>Author:<\/b> Twain, Mark, 1835-1910<br \/><br \/><b>Details:<\/b> Spec. Coll. copy 1: Green cloth over boards, blocked in gold and black, in case. Ex libris Olive Percival. Gift of Jo Swerling<br \/><br \/><b>Subjects:<\/b> Adventure and adventurers, Mississippi River -- Juvenile literature,Missouri -- Juvenile literature, Adventures of Huckleberry Finn');
    
def buildTooltip(ttfile,m):
	# build the output string - probably wind up as tool tip
	outstr =  "new Tip('" + re.sub('\'','\\\'', m[4]) + "', '<b>Full Title:<\/b> " +  re.sub('\'','\\\'', m[1])
	outstr = outstr + '<br \/><br \/><b>Author:<\/b> ' + re.sub('\'','\\\'', m[0]) 
	outstr = outstr + '<br \/><br \/><b>Details:<\/b> ' +  re.sub('\'','\\\'', m[5] )
	outstr = outstr + '<br \/><br \/><b>Subjects:<\/b> ' +  re.sub('\'','\\\'', m[2] )
	# outstr = outstr + 'date: ' +  re.sub('\'','\\\'', m[3].split('-',1)[0]) + '<br>\n'
	# outstr = outstr + 'file: ' +  re.sub('\'','\\\'', m[4]) + '<br>\n'
	outstr = outstr + "');\n"
	ttfile.write(outstr) 

	
# returns true if book is in the booklist file
def isInBookList(id):
	bl = open('iaclBookList.txt','r')
	for line in bl.readlines():
		if line.find(id) != -1:
			return 1
	return 0

#returns the Open Library ID using the mappings in the book list file
def mapIaclIDToOLID(id):
	bl = open('iaclBookList.txt','r')
	for line in bl.readlines():
		if line.find(id) != -1:
			return(line.split(' ',1)[0].lstrip('/b'))
	return('')

# returns the cover url, argument is img file basename 
def getCoverUrl(name):
	global attStorage;
	if attStorage == 0:
		return "http://covers.openlibrary.org/b/OLID/" + name + "-M.jpg"
	else:
		return "covers/" + name + ".jpg"

	
# MAIN
i = 0
attStorage = 0
infile=''
outfile=''
catfile=''
meta=[] # list of csv meta data

for arg in sys.argv:
	if arg[0] == '-':
		if arg == "-attached-storage":	
			attStorage = 1;
		else:
			print 'unrecognized option: ' + arg + ' IGNORED'
		continue;
	if i == 1:
		infile=arg
	if i == 2:
		catfile=arg
	i = i+1

print i
print attStorage

if i < 3:
	usage()
	sys.exit(1)

print 'opening input csv for read: ' + infile
reader=csv.reader(open(infile, 'r'))

title = author = description = subject = date = ''

#indexes for the various fields
aidx=1 # author
tidx=7 # title
sidx=6 # subject, will extract category from here
didx=2 # date
fidx=5 # file - identifier field used to derive the book link
descidx=3 # description
for row in reader:
	for f in row:
		author=row[aidx]
		title=row[tidx]
		subject=row[sidx]
		date=row[didx]
		file=row[fidx]
		desc=row[descidx]
	if isInBookList(file):
		meta.append([author, title, subject, date, file, desc])



cats = open(catfile,'r').readlines() # get the categories list

for m in meta:
	# filter subject categories
	# search subject m[2] for a match in categories
	outcat='' # category string

	for line in cats:
		if re.search(line.rstrip(),m[2],re.I) != None:
			print "found a category match for " + line
			print "subject is: " + m[2]
			print "-------------------------------------------------"
			# if there's a match output to that category
			outcat = line.rstrip() + '.html'
			outcatf = open( outcat, 'a')
			ttfname = line.rstrip() + 'Tooltip.js'
			ttf = open( ttfname, 'a')
			buildInterfaceElement(outcatf,m);
			buildTooltip(ttf,m)

	if (outcat == ''): # went through cat filter without a match
		outcatf = open('other.html', 'a') # dump to the catchall file
		ttf = open( 'otherTooltip.js', 'a')
		buildInterfaceElement(outcatf,m);
		buildTooltip(ttf,m)
		
# now concat templates head, <cat>.html, <cat_tooltip>.js and foot

cathtml = open('categories.html','w')
cathtml.write(re.sub('\$header','Categories',open('headtmpl.html.tmpl','r').read()))

for line in cats:
	if os.path.exists(line.strip() + '.html') != True:
		continue
	# write the category html file
	open(line.strip() + 'Category.html', 'w').write( re.sub('\$header',line.strip(),open('headtmpl.html.tmpl','r').read()) + open(line.strip() + '.html','r').read() + "<script type='text/javascript' language='javascript'>" + open(line.strip() + 'Tooltip.js','r').read()  + open('foottmpl.html.tmpl','r').read() )
	# write the link to the category in the categories.html
	cathtml.write('<a href="' + line.strip() + 'Category.html' + '">' + line.strip() + "</a><br>\n")

if os.path.exists('other.html') == True:
	open('otherCategory.html', 'w').write(open('headtmpl.html.tmpl','r').read() + open('other.html','r').read() + "<script type='text/javascript' language='javascript'>" + open('otherTooltip.js','r').read()  + open('foottmpl.html.tmpl','r').read() )
cathtml.write('<a href="otherCategory.html">Other Category</a><br>\n')
 # complete the categories.html
cathtml.write(open('foottmpl.html.tmpl','r').read())
sys.exit()

