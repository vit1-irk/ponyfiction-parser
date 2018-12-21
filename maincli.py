#!/usr/bin/env python3

from parser import *
import curses
import npyscreen

storylink = input("Ссылка на фанфик: ")
data = getFile(storylink)

meta, status = storyMetaData(data)
chapt_titles = [x["title"] for x in meta["chapters"]]
tag_info = ", ".join(meta["tags"])

def wrap(s, w):
    return [s[i:i + w] for i in range(0, len(s), w)]

def adjustMultiline(text, columns):
    hsplit = text.replace("\n\n", "%%lb%%")
    hsplit = hsplit.replace("\n", " ")
    hsplit = hsplit.replace("%%lb%%", "\n").split("\n")

    nchars = int(columns - 10)
    finalArray = []
    for key in hsplit:
        finalArray.extend(wrap(key, nchars))
        finalArray.extend([""])

    return finalArray

def somethingSelected(key):
    return key == 10 or key == 32

class OptionChooser(npyscreen.MultiLineAction):
    def actionHighlighted(self, act_on_this, key_press):        
        if (somethingSelected(key_press)):
            number = self.values.index(act_on_this)
            
            if status != "single":
                data2 = getFile(meta["chapters"][number]["link"])
                contents = chapterContents(data2)
            else:
                contents = meta["chapters"][0]["text"]

            meta["chapters"][number]["contents"] = contents
            self.parent.parentApp.getForm("FanficRead").value = meta["chapters"][number]
            self.parent.parentApp.switchForm("FanficRead")

class FicMetadata(npyscreen.FormMultiPage):
    def __init__(self, *args, **keywords):
        super(FicMetadata, self).__init__(*args, **keywords)
        self.add_handlers({
            "Q": self.allexit,
            "^Q": self.allexit,
            "K": self.previousPage
        })
    def create(self):
        self.value = None
        self.titletext = self.add_widget_intelligent(npyscreen.TitleText, name=meta["title"], editable=False)

        for descpart in adjustMultiline(meta["description"], self.columns):
            if descpart == "":
                continue
            self.add_widget_intelligent(npyscreen.Textfield, value=descpart, editable=False)

        self.add_widget_intelligent(npyscreen.FixedText, value="   ")
        self.add_widget_intelligent(npyscreen.TitleText, name="Теги:", editable=False)
        for txt in adjustMultiline(tag_info, self.columns):
            if (txt != ""):
                self.add_widget_intelligent(npyscreen.Textfield, value=txt, editable=False)

        self.add_widget_intelligent(npyscreen.FixedText, value="   ", editable=False)
        self.add_widget_intelligent(npyscreen.TitleText, name="Главы:", editable=False)
        
        self.chooser = self.add_widget_intelligent(OptionChooser, values = chapt_titles)
        self.switch_page(0)
    def previousPage(self, event):
        self.clear
        self.switch_page(0)
    def allexit(self, event):
        self.parentApp.switchForm(None)

class FanficRead(npyscreen.FormBaseNew):    
    def __init__(self, *args, **keywords):
        self.title=None
        super(FanficRead, self).__init__(*args, **keywords)
        self.add_handlers({
            "Q": self.parentApp.switchFormPrevious,
            "^Q": self.parentApp.switchFormPrevious
        })

    def create(self):
        self.titletext = self.add(npyscreen.FixedText, editable=False)
        self.baseline = self.add(npyscreen.TitleText, name="-"*(self.columns-10), editable=False)
        self.textDisplay = self.add(npyscreen.Pager, values = [""])

    def beforeEditing(self):
        self.titletext.value = self.value["title"]
        self.titletext.update()
        self.textDisplay.values = adjustMultiline(self.value["contents"], self.columns)
        self.textDisplay.update()

class PonyFictionApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm("MAIN", FicMetadata)
        self.addForm("FanficRead", FanficRead)

if __name__ == '__main__':
    myApp = PonyFictionApp()
    myApp.run()
