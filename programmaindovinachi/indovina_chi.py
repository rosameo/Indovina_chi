# -*- coding: utf-8 -*-
"""
Spyder Editor

This is an intelligent agent who plays "Guess who?".
A set of people are presented and the user (the second player, in person)
chooses one of the people (unknown person) among the set of people.
(The characteristics (carat) of the people are contained in the database.json file).
The agent has to guess the unkwnown person by asking a set of questions on the
characteristics of the unknown person.
A maximum number of questions is allowed (nDomandeLimite).
The user can answer only "si'" ("yes") or "no".
As a final question, the agent has to ask a dirtect question on the unknown person:
    "E' <nome personaggio>?" (Is it <name of a person>?)
    If the user answers "Si'" the agent has guessed and wins, otherwise it is defeated.
"""
import json
import random
import os
import webbrowser
from indovina_chi_gui import create_web_page, write_new_html_file

# leggo da file di input (JSON), la descrizione dei personaggi (in data['people'])
# e le domande corrispondenti a ciascuna caratteristica (in data['questions'])

file_directory = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(file_directory+"/database.json"))

#print(data['questions'][0][carat])
#print(data['people'][0])


# numero totale dei personaggi iniziali
n_people = 21

# numero dei personaggi nello stato corrente del gioco : verra' camibato man mano i personaggi verranno
# cancellati dallo ;;;;;;;        stato del gioco
people_in_game = 21

# numero limite di domande oltre il quale il gioco termina e l'agente intelligente non ha vinto se non ha indovinato
# l'agente intelligente vince se fa una domanda diretta (chiede se e' un certo personaggio)
nDomandeLimite = 5

# varra' 1 se rimane un solo personaggio nello stato del gioco
termineGioco=0

# creo una specializzazione dei dizionari che possono essere verificati per l'assenza di una chiave con 'not in'
class Merger(dict):
   def __missing__(self, key):
      return 0

# dizionario delle caratteristiche con le loro frequenze nei personaggi
caratFreq = Merger()

# funzione che cerca la caratteristica con la frequenza cercata nel dizionario freqCarat:
# Se la trova restituisce la domanda associata alla caratteristica
def cerco(freq):
   trovato=0
   domandaDiretta=0 # vale 1 se e' la domanda finale, diretta, che puo' terminare il gioco
   if ((freq==0)or(freq==1)): # vuol dire che c'e' un solo o due personaggi rimanenti e dobbiamo fare una domanda diretta
      # indovino direttamente il personaggio scegliendolo tra quelli presenti
      # cerco il primo personaggio presente in statoGioco[nomePersonaggio]
      for i in range(n_people):
          nomePersonaggio=data['people'][i]['nome']
          if (statoGioco[nomePersonaggio]=="presente"):
              domanda=data['questions'][0][nomePersonaggio]
              carat=nomePersonaggio
              trovato=1
              domandaDiretta=1
              break
   elif (freq in freqCarat):
      caratList=freqCarat[freq]
      #print(caratList)
      #print("in cerco: trovata freq: "+str(freq))
      #print(carat)
      # estraggo a caso una caratteristica dalla lista delle caratteristiche, aventi la stessa frequenza
      nCarat=len(caratList)
      n=random.randint(0,nCarat-1)
      carat=caratList[n]
      domanda=data['questions'][0][carat]
      # cancello la caratteristica dal dizionario freqCarat per non fare due volte la stessa domanda
      caratList.remove(carat)
      del freqCarat[freq]
      if (len(caratList)>0):
          freqCarat[freq]=caratList
      #print("trovata domanda: "+domanda)
      trovato=1
   else:
      trovato=0
      domanda=""
      carat=""
   return domanda, domandaDiretta, carat, trovato

# funzione che aggiorna lo stato del gioco (tabellone con le facce dei personaggi e dizionario dei personaggi presenti
# nello stato corrente del gioco), a seconda della risposta
# alla domanda sulla caratteristica passate come parametro
# La funzione ritorna 1 se c'e' solo 1 personaggio rimasto (people_in_game), 0 altrimenti
def aggiornaStato(risposta,carat,people_in_game):
   #print(carat)
   for i in range(n_people):
      # cerco la caratteristica carat per il personaggio i-esimo se e' presente nello stato corrente del gioco
      trovato=0
      nomePersonaggio=data['people'][i]['nome']
      if (statoGioco[nomePersonaggio]=="presente"):
         #print("personaggio "+nomePersonaggio+" presente")
         for value in data['people'][i].values():
            if (value==carat):
               #print("personaggio "+nomePersonaggio+" ha "+carat)
               trovato=1
               break
         if ((trovato==1)and(risposta=="N")or(trovato==0)and(risposta=="S")):
             # devo indicare come assente il personaggio i-esimo nello stato corrente del gioco
             del statoGioco[nomePersonaggio]
             statoGioco[nomePersonaggio]="assente"
             people_in_game = people_in_game - 1
             #print("personaggio "+nomePersonaggio+" cancellato ")
             # aggiorno le frequenze delle caratteristiche dei personaggi in freqCarat
             # per tenere conto solo dei personaggi rimanenti: decremento di 1 le frequenze di tutte le caratteristiche
             # che aveva il personaggio cancellato
             decrCaratFreq(i)
         #elif(trovato==1):
             #print(nomePersonaggio+ " rimanente")

   return (people_in_game)


# ciclo su tutti i personaggi per calcolare le frequenze delle caratteristiche dei personaggi
for i in range(n_people):
   for value in data['people'][i].values():
      if (value not in caratFreq): # se non c'e' nel vocabolario delle frequenze delle caratteristiche, lo aggiungo
         caratFreq[value]=1
      else:
         freq=caratFreq[value]
         freq=freq+1 # incrementa la frequenza
         del caratFreq[value]
         caratFreq[value]=freq

#print(caratFreq)

# decremento le frequenze delle caratteristioche quando un personaggio (di indice passato come parametro
# in data['people'][i]) quando e' stato cancellato dallo stato del gioco
def decrCaratFreq(i):
    for value in data['people'][i].values():
        freq=caratFreq[value]
        freq=freq-1 # incrementa la frequenza
        del caratFreq[value]
        caratFreq[value]=freq

# creo un dizionario contrario a caratFreq, con la frequenza come chiave, e la caratteristica (o un elenco di caratteristiche) come valore:
# Mi servira' per trovare le caratteristiche che hanno una certa frequenza (o la frequenza più' vicina a quella ottimale)
# ciclo sul dizionario caratFreq e copio le coppie (value, key) nel nuovo dizionario freqCarat
freqCarat = Merger()

for carat in caratFreq.keys():
   freq=caratFreq[carat]
   if (freq not in freqCarat):
      freqCarat[freq]=[carat]
   else:
      caratList = freqCarat[freq]
      del freqCarat[freq]
      caratList.append(carat)
      freqCarat[freq]=caratList

# ripopolo il dizionario caratFreq dopo che le frequenze delle caratteristiche sono state modificate a causa della
# cancellazione di alcuni personaggi dallo stato del gioco
def refreshFreqCarat():
  for carat in caratFreq.keys():
     freq=caratFreq[carat]
     if (freq not in freqCarat):
        freqCarat[freq]=[carat]
     else:
        caratList = freqCarat[freq]
        del freqCarat[freq]
        caratList.append(carat)
        freqCarat[freq]=caratList


#print(freqCarat)
# inizializzo il dizionario con lo stato del gioco (dizionario con i personaggi presenti o assenti),
# con chiave il nome del personaggio e valore "presente" o "assente" a seconda che sia nello stato corrente del gioco
statoGioco = Merger()
for i in range(n_people):
   nomePersonaggio=data['people'][i]['nome']
   statoGioco[nomePersonaggio]="presente"

file_html_name = "indovina_chi.html"
webbrowser.open(file_directory+"/"+file_html_name)
write_new_html_file(statoGioco)

#print(statoGioco)
nDomandeFatte=0 # numero domande che l'agente intelligente ha fatto all'utente: se e' superiore a nDomandeLimite
# l'agente intelligente ha perso
termineGioco=0 # varra' 1 se il gioco termina: o se l'agente intelligente ha indovinato con una domanda diretta
# o se si e' raggiunto il limite massimo di domande

### Loop del gioco ###
while(termineGioco==0):
   # cerco la caratteristica che ha la frequenza più vicina alla frequenza ottimale, che e' = people_in_game/2
   # se la trovo, restituisco la domanda corrispondente a quella caratteristica,
   # altrimenti o decremento di delta=1 o incremento di delta=1 il valore ottimale e lo cerco;
   # continuo cosi' incrementando delta, finche' lo trovo
   delta=1 # ampiezza intervallo [freqCercata2,freqCercata3] intorno al valore della frequenza cercata, distante da quella ottimale di +/- delta
   trovato=0
   freqCercata=int(people_in_game/2)
   if (people_in_game==3): # invece, se ci sono 3 personaggi rimanenti, conviene cercare una caratteristica
   # che valga per 2 personaggi su 3: mal che vada cancelliamo 1 personaggio soltanto, cosa che faremmo comunque
   # facendo int(freq/2).
       freqCercata=2
   #print("Freq cercata: "+str(freqCercata))
   domanda=""
   domandaDiretta=0 # vale 1 se la domanda che verra' fatta e' la domanda finale, diretta, su un personaggio

   domanda,domandaDiretta,carat,trovato=cerco(freqCercata)
   #print("fuori da cerco: domanda:"+domanda+" trovato:"+str(trovato))
   #print("carat: "+str(carat))
   while(trovato==0):
      #print("delta: "+str(delta))
      freqCercata2=freqCercata-delta
      domanda,domandaDiretta,carat,trovato=cerco(freqCercata2)
      if (trovato==0):
         freqCercata3=freqCercata+delta
         domanda,domandaDiretta,carat,trovato=cerco(freqCercata3)
         delta=delta +1

   # fai la domanda e verifica che la risposta sia corretta (o "si" o "no")
   rispostaCorretta=0
   while(rispostaCorretta==0):
      print("\n"+domanda)
      risposta = input("Rispondi: ")
      #print("Hai risposto: "+risposta)
      if ((risposta=="Si'") or (risposta=="si'") or (risposta=="SI'") or (risposta=="Si") or (risposta=="si") or (risposta=="SI") or (risposta=="Yes") or (risposta=="yes") or (risposta=="YES") or (risposta=="s") or (risposta=="S") or (risposta=="Y") or (risposta=="y")):
          risposta="S"
          rispostaCorretta=1
          #print("rispostaCorretta: "+str(rispostaCorretta))
      elif ((risposta=="No") or (risposta=="no") or (risposta=="NO") or (risposta=="n") or (risposta=="N")):
         risposta="N"
         rispostaCorretta=1
      else:
         print("Puoi rispondere solo si' o no; riprova")

   # quando la risposta e' corretta, aggiorna lo stato del gioco, cancellando i personaggi che non soddisfano le
   # caratteristiche specificate con la risposta
   people_in_game =aggiornaStato(risposta, carat, people_in_game)

   # aggiorna file html del gioco
   write_new_html_file(statoGioco)

   # rinfresco il dizionario con le frequenze aggiornate delle caratteristiche su cui fare le domande,
   # dei personaggi rimanenti nello stato del gioco corrente dopo che alcuni personaggi sono stati cancellati:
   # cancello il dizionario freqCarat completamente e lo ricreo da capo
   del freqCarat
   freqCarat = Merger()
   refreshFreqCarat()

   # stampa i personaggi rimanenti
   print("\n Restano i seguenti personaggi:\n")
   for i in range(n_people):
      nomePersonaggio=data['people'][i]['nome']
      if (statoGioco[nomePersonaggio]=="presente"):
          print(nomePersonaggio)
          #print(data['people'][i])

   # stampa le frequenze delle caratteristiche
   #print("\n Frequenze caratteristiche:")
   #print(caratFreq)

   # se resta solo 1 personaggio e le domanda fatte non sono maggiori del numero limite di domande l'agente
   # intelligente ha vinto

   nDomandeFatte = nDomandeFatte+1
   print("\n Domande rimanenti: "+str(nDomandeLimite-nDomandeFatte))

   if ((risposta=="S")and(domandaDiretta==1)):
      print("Hai vinto! Hai indovinato "+carat+" con "+str(nDomandeFatte)+" domande.")
      termineGioco=1
   elif ((people_in_game>=1) and (nDomandeFatte >= nDomandeLimite)):
         print("Mi spiace, non hai indovinato! Hai fatto "+str(nDomandeFatte)+" domande (limite massimo raggiunto).")
         termineGioco=1
   if (nDomandeFatte==nDomandeLimite):
       termineGioco=1
