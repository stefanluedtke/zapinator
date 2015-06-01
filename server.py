from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server
from _thread import start_new_thread
from string import Template
import time
import json
import urllib.parse

#dictionary der aktiven user
users={}
#dictionary der user, die den button "werbung vorbei" gedrueckt haben
adoverusers={}
adstartsusers={}
isad=False

class MyTemplate(Template):
    delimiter="|"


#Mit dieser Methode beantwortet der Server Anfragen.
#Für eine Übersicht über die Daten, die in environ stehen, siehe:
#https://www.python.org/dev/peps/pep-0333/#environ-variables
def simple_app(environ, start_response):
    #wenn query-string nicht leer: decoden und entsprechende aktion ausfuehren
    #wenn detail.html: seite bauen, dann ausliefern
    if environ["PATH_INFO"]== "/detail.html/":
        print("HIER3")
        qstring=urllib.parse.unquote(environ["QUERY_STRING"])
        query=json.loads(qstring)
        stname=query["stationpage"]
        f=open('detail.html','r')
        file=f.read()
        template=MyTemplate(file)
        answer=template.substitute(station=stname)
        start_response('200 OK', [])
        return [answer.encode('utf-8')]
    #wenn Datenuebertragung vom client: entweder heartbeat oder adover
    elif environ["QUERY_STRING"].startswith("{"):
        print("HIER1")
        qstring=urllib.parse.unquote(environ["QUERY_STRING"])
        query=json.loads(qstring)
        print(query)
        if query["type"]=="heartbeat":
            return handle_heartbeat(query["uid"],query["station"],start_response)
        elif query["type"]=="adover":
            return handle_adover(query["uid"],query["station"],start_response)
        elif query["type"]=="adstarts":
            return handle_adstarts(query["uid"],query["station"],start_response)
        elif query["type"]=="adstatus":
            return handle_adstatus(start_response)
    #wenn query-string leer:
    #wenn / angefragt: index.html liefern
    elif environ["PATH_INFO"] == "/" and environ["QUERY_STRING"] == "":
        print("HIER2")
        f=open('index.html','r')
        file=f.read()
        start_response('200 OK', [])
        return [file.encode('utf-8')]
    #sonst einfach angefragte datei liefern (unsicher?)
    elif environ["QUERY_STRING"] == "":
        print("HIER4")
        f=open(environ["PATH_INFO"][1:],'r')
        file=f.read()
        start_response('200 OK', [])
        return [file.encode('utf-8')]

        
def handle_heartbeat(uid,station,start_response):
    global users
    # wenn uid noch nicht in users: neu hinzu, sonst wird automatisch
    # vorhandener wert an stelle uid mit True ueberschrieben
    users.update({uid:True})
    start_response('200 OK', [])
    print("Heartbeat von "+str(uid))
    return [str(len(users)).encode('utf-8')]

def handle_adover(uid,station,start_response):
    global adoverusers
    global isad
    # wenn uid noch nicht in adoverusers: neu hinzu, sonst wird einfach
    # vorhandener wert ueberschrieben
    adoverusers.update({uid:True})
    #testen, ob Mehrheit Button Werbung vorbei gedrueckt hat
    if len(adoverusers)>=1/2*len(users):
        response="true"
        #Werbung vorbei, adoverusers loeschen
        adoverusers={}
        isad=False
    else:
        response="false"
    answer={"adover":response}
    start_response('200 OK', [])
    print("Werbung vorbei bei "+uid)
    #antwort adover:true oder adover:false senden
    return [str(answer).encode('UTF-8')]

def handle_adstarts(uid,station,start_response):
    global adstartsusers
    global isad
    # wenn uid noch nicht in adoverusers: neu hinzu, sonst wird einfach
    # vorhandener wert ueberschrieben
    adstartsusers.update({uid:True})
    #testen, ob Mehrheit Button Werbung vorbei gedrueckt hat
    if len(adstartsusers)>=1/2*len(users):
        response="true"
        #Werbung faengt an, adstartsusers loeschen
        adoverusers={}
        isad=True
    else:
        response="false"
    answer={"adstarts":response}
    start_response('200 OK', [])
    print("Werbung startet bei "+uid)
    #antwort adstarts:true oder adstarts:false senden
    return [str(answer).encode('UTF-8')]

def handle_adstatus(start_response):
    start_response('200 OK', [])
    if isad==True:
        return [str({"ad": "true"}).encode('UTF-8')]
    else:
        return [str({"ad": "false"}).encode('UTF-8')]

    
#Thread, der alle 2 min im users-dictionary aufraemt (alle user entfernen,
#von denen dann noch kein heartbeat erhalten wurde
def cleanupusers():
    global users
    while True:
        time.sleep(120)
        print("Aufraeumen")
        newusers=dict(users)
        for uid in users:
            if users[uid]==True:
                newusers[uid]=False
            else:
                del newusers[uid]
        users=newusers


#----------------------MAIN----------------------
#Server erzeugen, der die Methode simple_app zur Beantwortung von Anfragen verwendet
httpd = make_server('', 8000, simple_app)
print("Serving HTTP on port 8000...")
#Aufraeum-Thread starten
start_new_thread(cleanupusers,())
# Beantworte dauerhaft Anfragen
httpd.serve_forever()
