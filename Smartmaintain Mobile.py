import kivy
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout

from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.audio import SoundLoader
from kivy_garden.zbarcam import ZBarCam

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
    Barcode Reader, welcher für alle tools genutzt wird
    """

    #statische variablen:
    #Stringproperty für die dynamische Überschreibung der Modis
    modus = StringProperty()
    #label des Modis
    label_mode = None
    #ObjectProperty um textfeld zu getten
    tool_ean = ObjectProperty(None)
    #statische temporäre liste für den modus vereinnahmen
    ean_list = []
    #ObjectProperty um zbarcam objekt zu schließen und öffnen
    detector = ObjectProperty(None)




    def on_enter(self, *args):
        """
        Wenn das Fenster betreten wird, soll das Label den namen des Modis annehmen

        """
        #ZBarCam Detector starten
        self.detector.start()

        #gespeichertes Objekt laden, für den Modi
        if os.path.exists("save_mode.txt"):
            with open("save_mode.txt", "rb") as file:
                self.modus = pickle.load(file)

        else:
            self.modus = "DEFAULT"

        self.label_mode = Label(text=self.modus, size_hint=(0.7, 0.1), pos_hint={"x": 0.15, "y": 0.85},
                              color=(0, 69 / 255, 99 / 255, 1), font_size=50)
        self.add_widget(self.label_mode)


    def on_leave(self, *args):
        """
        wenn das fenster verlassen wird, soll das Label des Modis gelöscht werden

        """
        #ZBarCam Detector stoppen
        self.detector.stop()

        self.remove_widget(self.label_mode)



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
        Je nach aktuellem Modi werden verschiedene Operationen ausgeführt // hier werden hauptsächlich die RPCs benötigt

        """
        #gespeichertes objekt mittels pickle laden
        if os.path.exists("save_mode.txt"):
            with open("save_mode.txt","rb") as file:
                self.modus = pickle.load(file)

        #überprüft den Modi und jenachdem welcher Modi, werden individuelle aktionen ausgeführt
        if self.modus == "VEREINNAHMEN":
            print("MODE -> VEREINNAHMEN")

            #Button griden um gelesene daten in der Datenbank abzufrageb

            #überprüft ob in interne liste ist
            if self.tool_ean.text in self.ean_list:
                print("EAN WURDE BEREITS GESCANNT")
                #TODO: Sound einfügen (negativ)
                #create popup window..




            elif len(self.tool_ean.text) < 8 or len(self.tool_ean.text) > 16:
                print("UNGÜLTIGER EAN --> EAN MUSS 8 ZIFFERN BETRAGEN")
                # TODO: Sound einfügen (negativ)
                # create Popup Window


            else:
                #ean zur liste hinzufügen
                self.ean_list.append(self.tool_ean.text)
                print("EAN HINZUGEFÜGT...")
                # TODO: Sound einfügen (positiv)
                #eingabefeld leeren...
                self.tool_ean.text = ""
                print(self.ean_list)



        elif self.modus == "INSPEKTION":
            print("MODE -> INSPEKTION")
            #TODO: RPC als Bedingung des Bildschrim wechsels
            #speichert ean ab und ruft die funktion auf die das Label setzt
            ean = self.tool_ean.text
            #print(int(ean))
            InspektionScreen().set_ean_label(ean)
            #Textfeld leeren...
            self.tool_ean.text = ""
            #wechselt den screen zu InspektionScreen
            self.manager.current = "inspektion"
            self.manager.transition.direction = "right"


        elif self.modus == "WARTUNG":
            print("MODE -> WARTUNG")
            #TODO: RPC als Bedingung des Bildschrim wechsels
            #speichert ean ab und ruft die funktion auf die das Label setzt
            ean = self.tool_ean.text
            WartungScreen().set_ean_label(ean)
            #Textfeld leeren...
            self.tool_ean.text = ""
            #wechselt den Screen zu Wartungsscreen
            self.manager.current = "wartung"
            self.manager.transition.direction = "right"

        elif self.modus == "VERSAND":
            print("MODE -> VERSAND")
            #speichert ean ab und ruft funktion auf die das Label setzt
            ean = self.tool_ean.text
            VersandScreen().set_ean_label(ean)
            #Textfeld leeren...
            self.tool_ean.text = ""
            #wecheslt den screen zurück zum VersandScreen
            self.manager.current = "versand"
            self.manager.transition.direction = "right"



class HomeScreen(Screen, FloatLayout):
    """
    Bildet den Home-Bildschirm ab // Manager wird im kivy file editiert
    """
    #um auf funktionen und attribute vom barcodereader im kivy file zuzugreifen
    mode = BarcodeReaderScreen()


class VereinnahmenScreen(Screen, FloatLayout):

    """
    Dokumentation des Tools beim ankommen -> Datenbank kommunikation // Layout wird im Kivy file manipuliert
    LayoutManager um touch Ereignisse aufnehmen zu können

    """
    # um auf funktionen und attribute vom barcodereader im kivy file zuzugreifen
    mode = BarcodeReaderScreen()




class InspektionScreen(Screen, FloatLayout):
    """
    Inspektion des Tools wird dokumentiert -> Datenbank kommunikation // Layout wird im Kivy file manipuliert
    """
    #statische Variablen
    #ruft die Klasse BarcodeReaderScreen auf//wird benötigt um im kivy file auf dessen funktionen zuzugreifen
    mode = BarcodeReaderScreen()
    #EAN Stringproperty für dynamische Änderung des Labels
    EAN = StringProperty()
    #label objekt als statische(klassen-global) variable
    label_ean_ins = None


    def on_enter(self, *args):
        """
        Beim betreten des fensters wird das neuste EAN abgefragt und als Label gesetzt

        """
        #falls das objekt noch nie gespeichert wurde

        if os.path.exists("save_ean_ins.txt"):
            with open("save_ean_ins.txt", "rb") as file:
                self.EAN = pickle.load(file)

        else:
            self.EAN = "DEFAULT"

        self.label_ean_ins = Label(text="'{}'".format(self.EAN), size_hint=(0.7, 0.075), pos_hint={"x":0.15, "y":0.65},
                               color=(0, 69/255, 99/255, 1), font_size=30)
        self.add_widget(self.label_ean_ins)


    def on_leave(self, *args):
        """
        Beim verlassen des fensters wird der das Label gelöscht

        """
        self.remove_widget(self.label_ean_ins)


    def set_ean_label(self, ean):
        """
        Settet den Label namen neu // das label zeigt an welches Tool gerade Inspiziert wird

        """
        self.EAN = ean
        #speichert das Objekt mittels pickle
        with open("save_ean_ins.txt", "wb") as file:
            pickle.dump(self.EAN, file)





class WartungScreen(Screen):
    """
    Wartung des Tools wird dokumentiert -> Datenbank kommunikation // Layout wird im Kivy file manipuliert

    """
    #um auf funktionen und attribute vom barcodereader im kivy file zuzugreifen
    mode = BarcodeReaderScreen()
    #EAN als stringproperty zum setzten des Labels
    EAN = StringProperty()
    #gloabele objektvariable zum konstruieren des labels
    label_ean_war = ObjectProperty(None)
    #time Stringproperty um als Start Label wiederzugeben
    start_time = StringProperty()
    #time StringProperty um als Ende Label wiederzugeben
    end_time = StringProperty()
    #label id
    label1 = ObjectProperty(None)


    def on_enter(self, *args):
        """
        Beim betreten des fensters wird das neuste EAN abgefragt und als Label gesetzt

        """
        #falls das objekt noch nie gespeichert wurde

        if os.path.exists("save_ean_war.txt"):
            with open("save_ean_war.txt", "rb") as file:
                self.EAN = pickle.load(file)

        else:
            self.EAN = "DEFAULT"

        self.label_ean_war = Label(text="'{}'".format(self.EAN), size_hint=(0.7, 0.075), pos_hint={"x":0.15, "y":0.65},
                               color=(0, 69/255, 99/255, 1), font_size=30)
        self.add_widget(self.label_ean_war)


    def on_leave(self, *args):
        """
        Beim verlassen des fensters wird der das Label gelöscht

        """
        self.remove_widget(self.label_ean_war)


    def set_ean_label(self, ean):
        """
        Settet den Label namen neu // das label zeigt an welches Tool gerade Inspiziert wird

        """
        self.EAN = ean
        # speichert das Objekt mittels pickle
        with open("save_ean_war.txt", "wb") as file:
            pickle.dump(self.EAN, file)

        #neuer EAN bedeutet auch neuer Zeitansatz:
        self.label1.text = ""



    def get_time(self, mode):
        """
        Gibt den genauen Startpunkt zurück und speichert den als Stringproperty ab

        """
        if mode == "start":
            self.start_time = time.asctime(time.localtime(time.time()))

        elif mode == "stop":
            self.end_time = time.asctime(time.localtime(time.time()))

    def lastpruefung_check(self):
        pass

class VersandScreen(Screen, FloatLayout):
    """
    Versand des Screens wird dokumentiert -> Datenbank kommunikation // Layout wird im kivy file manipuliert

    """
    #um auf funktionen und attribute vom barcodereader im kivy file zuzugreifen
    mode = BarcodeReaderScreen()
    #StringProperty EAN für dynamische Labeltext verwaltung
    EAN = StringProperty()
    #label id um dynamisch label anzuzeiugen
    label_ean_ver = None


    def on_enter(self, *args):
        """
        Beim betreten des fensters wird das neuste EAN abgefragt und als Label gesetzt

        """
        #falls das objekt noch nie gespeichert wurde
        if os.path.exists("save_ean_ver.txt"):
            with open("save_ean_ver.txt", "rb") as file:
                self.EAN = pickle.load(file)
        else:
            self.EAN = "DEFAULT"

        self.label_ean_ver = Label(text="'{}'".format(self.EAN), size_hint=(0.7, 0.075), pos_hint={"x":0.15, "y":0.75},
                               color=(0, 69/255, 99/255, 1), font_size=30)
        self.add_widget(self.label_ean_ver)


    def on_leave(self, *args):
        """
        Beim verlassen des fensters wird der das Label gelöscht

        """
        self.remove_widget(self.label_ean_ver)


    def set_ean_label(self, ean):
        """
        Settet das Label neu // das Label zeigt welches Tool gerade Versand wird

        """
        self.EAN = ean
        #objekt mittels pickle extern speichern sodass bei wiederholten klassenaufruf die objekte erhalten bleiben
        with open("save_ean_ver.txt", "wb") as file:
            pickle.dump(self.EAN, file)




class MobileApp(App):

    def build(self):
        return



if __name__ == '__main__':
    mobile_obj = MobileApp()
    mobile_obj.run()


