from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server

# Dient erst mal nur dazu, zu zeigen, dass Kommunikation zwischen Client und
# Server möglich ist und Werte gespeichert werden können. Das Speichern in einer
# Datei ist sicherlich nicht ideal


#Mit dieser Methode beantwortet der Server Anfragen.
#Für eine Übersicht über die Daten, die in environ stehen, siehe:
#https://www.python.org/dev/peps/pep-0333/#environ-variables
def simple_app(environ, start_response):

    if environ["PATH_INFO"] == "/anzahl.txt":
        #wenn anzahl.txt angefragt wird:
        #anzahl aus datei einlesen, um 1 erhoehen, und zurueckliefern
        f = open('anzahl.txt', 'r')
        anzahl = int(f.read())
        f.close()
        anzahl += 1
        f = open('anzahl.txt','w')
        f.write(str(anzahl))
        f.close()
        start_response('200 OK', [])
        return [str(anzahl).encode('utf-8')]
    elif environ["PATH_INFO"] == "/":
        #wenn / angefragt: index.html liefern
        f=open('index.html','r')
        file=f.read()
        start_response('200 OK', [])
        return [file.encode('utf-8')]        
    else:
        #sonst einfach angefragte datei liefern (unsicher?)
        f=open(environ["PATH_INFO"][1:],'r')
        file=f.read()
        start_response('200 OK', [])
        return [file.encode('utf-8')]
        

#Server erzeugen, der die Methode simple_app zur Beantwortung von Anfragen verwendet
httpd = make_server('', 8000, simple_app)
print("Serving HTTP on port 8000...")

# Beantworte dauerhaft Anfragen
httpd.serve_forever()
