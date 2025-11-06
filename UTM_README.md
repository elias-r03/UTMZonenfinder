Dieses Python-Webprojekt ermöglicht die interaktive Erkundung des Universal Transverse Mercator (UTM)-Systems. Nutzer können durch Klick auf die Karte oder manuelle Koordinateneingabe die UTM-Zone eines beliebigen Punkts auf der Erde bestimmen.

Das Programm kombiniert ein Flask-Backend mit einem Leaflet-/Folium-Frontend. Nach Auswahl eines Punkts werden dessen geografische Koordinaten, die UTM-Zone sowie die zugehörige Hemisphäre berechnet und auf einer Mercator-Karte farbig markiert. Ein Marker zeigt die Ergebnisse detailliert per Popup an.

Das UTM-System teilt die Erdoberfläche in 60 Zonen zu je 6° Länge ein, basierend auf einer transversalen Zylinderprojektion. Jede Zone nutzt eine Standardlinie, wodurch das Verzerrungsproblem lokaler Projekte reduziert wird. Als Referenzkörper dient ein Rotationsellipsoid, um der tatsächlichen Erdform Rechnung zu tragen. Im Bereich der Berührungslinie wird ein Skalenfaktor von 0,9996 verwendet, was eine gleichmäßige Verteilung der Verzerrung und eine Genauigkeit unter 0,1 % pro Zone ermöglicht—besser als bei globalen Projektionen.

Die Anwendung bietet einen intuitiven Zugang zu zentralen Konzepten der Kartengeometrie und hilft besonders Lernenden, die räumliche Struktur des UTM-Systems direkt auf der Weltkarte nachvollziehen zu können.

Benötigte Bibliotheken:
Flask, Folium

Benutze Sprachen
Python 
JavaScript
HTML / CSS 

06.11.2025
