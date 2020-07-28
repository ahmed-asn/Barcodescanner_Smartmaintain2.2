import kivy
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout

from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.audio import SoundLoader


import pickle
import os
import time




class WindowManager(ScreenManager):
    """
    Managet im Kivy file alle Windows

    """

    pass



class BarcodeReaderScreen(Screen, FloatLayout):
    """
    Barcode Reader, welcher für alle tools genutzt wird; Je nach Modis werden entsprechende Funktion für den Button
    ok ausgeführt

    """

    #globale variablen:
    #String für modus um die Modis zu verwalten
    modus = ""

    #globale objektvariable zum konstruieren des Labels
    label_modus = None

    #ObjectPropertys für den Python zugriff auf kivy Attribute
    #ObjectProperty um textfeld zu getten
    tool_ean = ObjectProperty(None)
    #ObjectProperty um zbarcam objekt zu schließen und öffnen
    detektor = ObjectProperty(None)

    #globale temporäre liste für den modus vereinnahmen
    ean_liste = []

    #sounds loaden zum einfügen
    #bad_sound = SoundLoader.load("bad_sound.wav")



    def on_enter(self, *args):
        """
        Wenn das Fenster betreten wird, soll das Label den namen des Modis annehmen und der Barcode reader
        gestartet werden

        """

        #ZBarCam Detector starten//ID im Kivy File, hier zugriff über Objectproperty
        self.detektor.start()


        #gespeichertes Objekt laden, für den Modi über das Modul pickle --> Objekte werden extern abgespeichert
        if os.path.exists("save_mode.txt"):
            with open("save_mode.txt", "rb") as file:
                self.modus = pickle.load(file)

        else:
            self.modus = ""

        #Label erstellen;als namen den jeweiligen MODI
        self.label_modus = Label(text=self.modus, size_hint=(0.7, 0.1), pos_hint={"x": 0.15, "y": 0.85},
                              color=(0, 69 / 255, 99 / 255, 1), font_size=50)
        self.add_widget(self.label_modus)


    def on_leave(self, *args):
        """
        wenn das fenster verlassen wird, soll das Label des Modis gelöscht werden und der
        Barcode Reader gestoppt werden aus Effizienz gründen

        """

        #Barcode Detector stoppen
        self.detektor.stop()

        #Label entfernen um beim nächsten Modi keine Überschreibung zu bekommen
        self.remove_widget(self.label_modus)



    def set_mode(self, ein_modus):
        """
        wandelt den Modi um // wird jedesmal aufgerufen, wenn der barcodescanner von einem
        bestimmten Modi aufgerufen wird

        """

        self.modus = ein_modus
        #speichert das objekt mittels pickle um beim wiederholten aufrufen der klasse die objekte zu sichern
        with open("save_mode.txt", "wb") as file:
            pickle.dump(self.modus, file)
        print("ACTUAL MODE: {}".format(self.modus))


    def ok(self):
        """
        Je nach aktuellem Modi werden verschiedene Prozeduren ausgeführt
        hier werden hauptsächlich die RPCs benötigt

        """

        #gespeichertes objekt mittels pickle laden // extern gespeichertes Objekt
        if os.path.exists("save_mode.txt"):
            with open("save_mode.txt","rb") as file:
                self.modus = pickle.load(file)


        # überprüft den Modi und jenachdem welcher Modi, werden individuelle aktionen ausgeführt
        #=================VEREINNAHMEN==================================================================================
        if self.modus == "VEREINNAHMEN":
            print("MODE -> VEREINNAHMEN")

            #Button griden um gelesene daten in der Datenbank abzufragen


            #EAN abspeichern damit detektor gestoppt werden kann
            ean = self.tool_ean.text
            #detektor stoppen aus effizienz gründen
            self.detektor.stop()

            #überprüft ob in interne liste ist um zu checken ob der Barcode in dem Durchgang schon gelesen wurde
            if ean in self.ean_liste:
                print("EAN WURDE BEREITS GESCANNT")
                #TODO: Sound einfügen (negativ)


            #EAN muss zwischen 8 und 17 sein sonst ungültig
            elif not(7 < len(ean) < 17):
                print("UNGÜLTIGER EAN --> EAN MUSS 8-16 ZIFFERN BETRAGEN")
                # TODO: Sound einfügen (negativ)


            else:
                #ean zur liste hinzufügen
                self.ean_liste.append(ean)
                print("EAN HINZUGEFÜGT...")
                # TODO: Sound einfügen (positiv)

                #eingabefeld leeren...
                self.tool_ean.text = ""
                print(self.ean_liste)


            #dektor wieder starten...
            self.detektor.start()


        #===================INSPEKTION==================================================================================
        elif self.modus == "INSPEKTION":
            print("MODE -> INSPEKTION")


            #TODO: RPC als Bedingung der folgenden Aktionen // ist EAN in Datenbank?
            #speichert ean ab und ruft die funktion auf die das Label setzt
            ean = self.tool_ean.text
            InspektionScreen().set_ean_label(ean)

            #dektor stoppen aus effizienz gründen
            self.detektor.stop()


            #Textfeld leeren...
            self.tool_ean.text = ""
            #wechselt den screen zu InspektionScreen
            self.manager.current = "inspektion"
            self.manager.transition.direction = "right"

            #da bildschirm gewechselt wird müssen wir detekor nicht wieder starten...



        #=================WARTUNG=======================================================================================
        elif self.modus == "WARTUNG":
            print("MODE -> WARTUNG")

            #TODO: RPC als Bedingung der folgenden Aktionen // ist EAN in Datenbank
            #speichert ean ab und ruft die funktion auf die das Label setzt
            ean = self.tool_ean.text
            WartungScreen().set_ean_label(ean)

            #detektor stoppen aus effizienz gründen
            self.detektor.stop()


            #Textfeld leeren...
            self.tool_ean.text = ""
            #wechselt den Screen zu Wartungsscreen
            self.manager.current = "wartung"
            self.manager.transition.direction = "right"


        #=================VERSAND=======================================================================================
        elif self.modus == "VERSAND":
            print("MODE -> VERSAND")

            #TODO: RPC als Bedingung der folgenden Funktionen // ist EAN in Datenbank
            #speichert ean ab und ruft funktion auf die das Label setzt
            ean = self.tool_ean.text
            VersandScreen().set_ean_label(ean)

            #dektor stoppen aus effizienz gründen
            self.detektor.stop()

            #Textfeld leeren...
            self.tool_ean.text = ""
            #wecheslt den screen zurück zum VersandScreen
            self.manager.current = "versand"
            self.manager.transition.direction = "right"

            #dektor wider starten ist aufgrund des Bildschirmwechsels ineffizient
            #--> BarcodeReaderScreen().on_leave()...





class HomeScreen(Screen, FloatLayout):
    """
    Bildet den Home-Bildschirm ab // Manager wird im kivy file editiert
    """

    #um auf funktionen und attribute vom barcodereader im kivy file zuzugreifen
    modus = BarcodeReaderScreen()


class VereinnahmenScreen(Screen, FloatLayout):

    """
    SCREEN WIRD NICHT BENÖTIGT ---> ER WIRD DIREKT ZUM BARCODE READER GEFÜHRT

    """

    pass




class InspektionScreen(Screen, FloatLayout):
    """
    Inspektion des Tools wird dokumentiert -> Datenbank kommunikation // Layout wird im Kivy file manipuliert

    """

    #globale Variablen

    #EAN String setzen um EAN LABEL zu verwalten
    EAN = ""

    #gloable objektvariable zum konstruieren des Labels
    label_ean_ins = None


    def on_enter(self, *args):
        """
        Beim betreten des fensters wird das neuste EAN abgefragt und als Label gesetzt

        """

        #EAN aus pickle entnehmen und intern apspeichern
        if os.path.exists("save_ean_ins.txt"):
            with open("save_ean_ins.txt", "rb") as file:
                self.EAN = pickle.load(file)

        else:
            #STANDARD WERT
            self.EAN = "BARCODE"

        #Label konstruieren und abspeichern
        self.label_ean_ins = Label(text="'{}'".format(self.EAN), size_hint=(0.7, 0.075), pos_hint={"x":0.15, "y":0.65},
                               color=(0, 69/255, 99/255, 1), font_size=30)
        self.add_widget(self.label_ean_ins)


    def on_leave(self, *args):
        """
        Beim verlassen des fensters wird der das Label gelöscht

        """

        #Label löschen um beim erneuten aufruf Überschneidungen zu vermeiden
        self.remove_widget(self.label_ean_ins)



    def set_ean_label(self, ean):
        """
        Settet den Label namen neu // das label zeigt an welches Tool gerade Inspiziert wird

        """

        self.EAN = ean
        #speichert das Objekt mittels pickle extern ab
        with open("save_ean_ins.txt", "wb") as file:
            pickle.dump(self.EAN, file)




class WartungScreen(Screen):
    """
    Wartung des Tools wird dokumentiert -> Datenbank kommunikation // Layout wird im Kivy file manipuliert

    """

    #globale Variablen

    #EAN als string setzten um EAN LABEL zu verwalten
    EAN = ""

    #Stringpropertys um Strings aus dem Kivyfile zu manipulieren
    #time Stringproperty um als Start Label wiederzugeben
    start_zeit = StringProperty()
    #time StringProperty um als Ende Label wiederzugeben
    end_zeit = StringProperty()

    #ObjectPropertys um in Python file auf kivy objekte zuzugreifen
    #um wartungsdauer über RPC abzuspeichern
    wartungs_dauer = ObjectProperty(None)

    #gloabele objektvariable zum konstruieren des labels
    label_ean_war = None





    def on_enter(self, *args):
        """
        Beim betreten des fensters wird das neuste EAN abgefragt und als Label gesetzt

        """

        #Label EAN aus pickle laden
        if os.path.exists("save_ean_war.txt"):
            with open("save_ean_war.txt", "rb") as file:
                self.EAN = pickle.load(file)

        else:
            self.EAN = "DEFAULT"

        #label konstruieren
        self.label_ean_war = Label(text="'{}'".format(self.EAN), size_hint=(0.7, 0.075), pos_hint={"x":0.15, "y":0.65},
                               color=(0, 69/255, 99/255, 1), font_size=30)
        self.add_widget(self.label_ean_war)



    def on_leave(self, *args):
        """
        Beim verlassen des fensters wird der das Label gelöscht

        """

        #label löschen
        self.remove_widget(self.label_ean_war)


    def set_ean_label(self, ean):
        """
        Settet den Label namen neu // das label zeigt an welches Tool gerade Inspiziert wird
        wird schon im barcode reader aufgerufen...

        """

        self.EAN = ean
        # speichert das Objekt mittels pickle extern ab
        with open("save_ean_war.txt", "wb") as file:
            pickle.dump(self.EAN, file)




    def get_time(self, modus):
        """
        Gibt den genauen Startpunkt zurück und speichert den als Stringproperty ab

        """

        #settet die Label namen // da über Stringpropertys werden sie im kivy file manipulliert
        if modus == "start":
            self.start_zeit = time.asctime(time.localtime(time.time()))

        elif modus == "ende":
            self.end_zeit = time.asctime(time.localtime(time.time()))


    def lastpruefung_check(self):
        """
        wird ausgeführt wenn Checkbox LASTPRUEFUNG angeklickt wird..
        --> RPC

        """
        pass

class VersandScreen(Screen, FloatLayout):
    """
    Versand des Screens wird dokumentiert -> Datenbank kommunikation // Layout wird im kivy file manipuliert

    """

    #globale Variablen

    #EAN String für das setzen Des EAN LAbels --> wird extern in pickle abgespeichert
    EAN = ""

    #globale Objektvariable zum konstruieren des Labels
    label_ean_ver = None


    def on_enter(self, *args):
        """
        Beim betreten des fensters wird das neuste EAN abgefragt und als Label gesetzt

        """

        #Label EAN mittels Pickle laden und intern speichern
        if os.path.exists("save_ean_ver.txt"):
            with open("save_ean_ver.txt", "rb") as file:
                self.EAN = pickle.load(file)
        else:
            self.EAN = "DEFAULT"

        #Label konstruieren
        self.label_ean_ver = Label(text="'{}'".format(self.EAN), size_hint=(0.7, 0.075), pos_hint={"x":0.15, "y":0.75},
                               color=(0, 69/255, 99/255, 1), font_size=30)
        self.add_widget(self.label_ean_ver)


    def on_leave(self, *args):
        """
        Beim verlassen des fensters wird der das Label gelöscht

        """

        #Label löschen
        self.remove_widget(self.label_ean_ver)


    def set_ean_label(self, ean):
        """
        Settet das Label neu // das Label zeigt welches Tool gerade Versand wird
        --> wird schon im BarcodeReaderScreen aufgerufen

        """

        self.EAN = ean
        #objekt mittels pickle extern speichern sodass bei wiederholten klassenaufruf die objekte erhalten bleiben
        with open("save_ean_ver.txt", "wb") as file:
            pickle.dump(self.EAN, file)



class MobileApp(App):


    def build(self):
        """
        wird automatisch beim Befehl kivy.app.App().run() aufgerufen
        -> das was hier return wird wird gebuildet // Kivy ruft automatisch ein kivy file auf, welcher den Namen der
            Klasse enthält in unserem Fall "mobile.kv", deshalb muss hier nichts returnt werden...

        """

        return



if __name__ == '__main__':
    """
    In der Main Ausführung wird das kivy.app.App Objekt aufgerufen und mit run ausgeführt
    
    """

    #App Objekt erstellen und ausführen
    mobile_obj = MobileApp()
    mobile_obj.run()


