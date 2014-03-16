import urllib,urllib2,sys,zipfile,os.path,sys
from BeautifulSoup import BeautifulSoup
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QLabel

def ConvertEpub(name,html_files):
	epub=zipfile.ZipFile(name,'w')
	epub.writestr("mimetype","application/epub+zip")
	epub.writestr("META-INF/container.xml", '''<container version="1.0"
	           xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
			     <rootfiles>
				     <rootfile full-path="OEBPS/Content.opf" media-type="application/oebps-package+xml"/>
					   </rootfiles>
					   </container>''')
	index_tpl = '''<package version="2.0"
	xmlns="http://www.idpf.org/2007/opf">
	    <metadata/>
		  <manifest>
		      %(manifest)s
			    </manifest>
				  <spine toc="ncx">
				      %(spine)s
					    </spine>
						</package>'''

	manifest = ""
	spine = ""

	for i, html in enumerate(html_files):
		basename = os.path.basename(html)
		manifest += '<item id="file_%s" href="%s" media-type="application/xhtml+xml"/>' % (i+1, basename)
		spine += '<itemref idref="file_%s" />' % (i+1)
		epub.write(html, 'OEBPS/'+basename)
		epub.writestr('OEBPS/Content.opf', index_tpl % {'manifest': manifest,'spine': spine,})

		images = []
		for i, html in enumerate(html_files):
			basename = os.path.basename(html)
			manifest += '<item id="file_%s" href="%s" media-type="application/xhtml+xml"/>' % (i+1, basename)
			spine += '<itemref idref="file_%s" />' % (i+1)
			soup = BeautifulSoup(open(html).read())
			for img in soup.findAll('img'):
				if not img['src'].startswith('http://'):
					images.append(os.path.basename(img['src']))
					img['src'] = os.path.basename(img['src'])

			epub.writestr(str(soup), 'OEBPS/'+basename)
		for img in images:
			epub.write(img, 'OEBPS/'+img)


def RemoveStyle(tag,styles,soup):
	for style in styles:
		for node in soup.findAll(tag,style):
			node.extract()
	return soup
	
class Example(QWidget):
    
    def __init__(self):
        super(Example, self).__init__()
        
        self.lb = QLabel('URL: ', self)

        self.le = QLineEdit(self)
        self.le.setObjectName("url")

        self.btn = QPushButton("Sipppp", self)
        self.btn.clicked.connect(self.buttonClicked)   
         
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.lb)
        hbox1.addWidget(self.le)
        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.btn)

        
        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)

        vbox.addLayout(hbox2)
       
        self.setLayout(vbox)
        
        self.setGeometry(300, 300, 300, 100)
        self.setWindowTitle('Event sender')
        
    def buttonClicked(self):
		url=self.le.text()
		req=urllib2.Request(url)
		response=urllib2.urlopen(req)
		soup=BeautifulSoup(response.read())

		styles=['zh-question-collapsed-link','zm-item-vote','zh-answers-title','zm-votebar','zm-item-comment-el','zm-item-vote-info','zu-top','zu-global-notify','zm-side-section','zh-footer','zh-webshare-dialog','zh-feedback-form','zh-add-question-form','view','business-selection']
		soup=RemoveStyle('div',styles,soup)
		soup=RemoveStyle('h2',['zm-item-title'],soup)
		soup=RemoveStyle('a',['collapse','zg-link-litblue'],soup)
		for tag in soup.findAll('body'):
			tag['style']='margin:0px auto text-align:center'

		html=soup.prettify('utf-8')
		with open('a.html','wb') as f:
			f.write(html)
		name=soup.find('title').getText()

		ConvertEpub(name+'.epub',['a.html']) 

def main():
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

