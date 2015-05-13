from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server
from _thread import start_new_thread
import time

#dictionary der aktiven user
users={}
#dictionary der user, die den button "werbung vorbei" gedrueckt haben
adoverusers={}


#Mit dieser Methode beantwortet der Server Anfragen.
#Für eine Übersicht über die Daten, die in environ stehen, siehe:
#https://www.python.org/dev/peps/pep-0333/#environ-variables
def simple_app(environ, start_response):
    #heartbeat-signal
    if environ["QUERY_STRING"].startswith("heartbeat"):
        return handle_heartbeat(environ,start_response)
    #user hat button "werbung vorbei" gedrueckt
    elif environ["QUERY_STRING"].startswith("button_adover"):
        return handle_adover(environ,start_response);
    #wenn / angefragt: index.html liefern
    elif environ["PATH_INFO"] == "/" and environ["QUERY_STRING"] == "":
        f=open('index.html','r')
        file=f.read()
        start_response('200 OK', [])
        return [file.encode('utf-8')]
    #sonst einfach angefragte datei liefern (unsicher?)
    elif environ["QUERY_STRING"] == "":
        f=open(environ["PATH_INFO"][1:],'r')
        file=f.read()
        start_response('200 OK', [])
        return [file.encode('utf-8')]

        
def handle_heartbeat(environ,start_response):
    global users
    query=environ["QUERY_STRING"].split(":")
    uid=query[1]
    # wenn uid noch nicht in users: neu hinzu, sonst wird automatisch
    # vorhandener wert an stelle uid mit True ueberschrieben
    users.update({uid:True})
    start_response('200 OK', [])
    print("Heartbeat von "+uid)
    return [str(len(users)).encode('utf-8')]

def handle_adover(environ,start_response):
    global adoverusers
    query=environ["QUERY_STRING"].split(":")
    uid=query[1]
    # wenn uid noch nicht in adoverusers: neu hinzu, sonst wird einfach
    # vorhandener wert ueberschrieben
    adoverusers.update({uid:True})
    #testen, ob Mehrheit Button Werbung vorbei gedrueckt hat
    if len(adoverusers)>1/2*len(users):
        response="adover"
        #Werbung vorbei, adoverusers loeschen
        adoverusers={}
    else:
        response="adnotover"
    start_response('200 OK', [])
    print("Werbung vorbei bei "+uid)
    return [response.encode('utf-8')]

    
#Server erzeugen, der die Methode simple_app zur Beantwortung von Anfragen verwendet
httpd = make_server('', 8000, simple_app)
print("Serving HTTP on port 8000...")

#Thread starten, der alle 2 min im users-dictionary aufraemt (alle user entfernen,
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
            
start_new_thread(cleanupusers,())



# Beantworte dauerhaft Anfragen
httpd.serve_forever()
