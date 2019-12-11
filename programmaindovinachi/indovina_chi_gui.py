import json
import webbrowser
import os
import numpy as np
from html_utility import *

"""
Programma per la gestione dell'interfaccia grafica del gioco "Indovina chi"
"""

#variabili globali
file_directory = os.path.dirname(os.path.abspath(__file__))
file_html_name = "indovina_chi.html"

def create_web_page(statoGioco):
    """
    Restituisce il contenuto da scrivere nel file html
    :param json_data: json contenente le informazioni dei personaggi di "Indovina chi"
    """

    new_html_content = html_page_start

    for person in statoGioco:
        #creazione caselle personaggi per il file html
        image_path = ""
        if(statoGioco[person]=="presente"):
            image_path = "<img src=\"Personaggi/Personaggi/" + person.lower()  + ".png\">"
        else:
            image_path = "<img src=\"Personaggi/Personaggi/not_available.jpg\">"
        new_html_content += "<div class=\"box\">" + image_path + "</div>\n"

    new_html_content += html_page_end

    return new_html_content

def write_new_html_file(statoGioco):
    """
    Legge le informazioni sul gioco dal file database.txt e le traduce in formato html,
    visualizzabile da browser.
    """

    html_page_content = create_web_page(statoGioco)

    f = open(file_html_name, "w")
    f.write(html_page_content)
    f.close()

if __name__ == "__main__":
    write_html_file()
