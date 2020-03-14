import os
import random
import plistlib
from AppKit import NSSound, NSBeep, NSSpeechSynthesizer,\
    NSFullUserName,\
    NSImageNameAddTemplate, NSImageNameRemoveTemplate
import vanilla
from defconAppKit.windows.baseWindow import BaseWindowController
import mojo
from mojo.events import addObserver, removeObserver
from mojo import extensions

defaultStub = "com.typesupply.RoboSounds."

# ------
# Events
# ------

knownEvents = """
applicationDidFinishLaunching
applicationDidBecomeActive
applicationWillResignActive
applicationScreenChanged
fontBecameCurrent
fontResignCurrent
fontWillOpen
fontDidOpen
newFontWillOpen
newFontDidOpen
binaryFontWillOpen
fontWillClose
fontWillSave
fontDidSave
fontWillAutoSave
fontDidAutoSave
fontWillGenerate
fontDidGenerate
fontDidChangeExternally
currentGlyphChanged
cut
copyAsComponent
paste
delete
selectAllAlternate
selectAllControl
deselectAll
didUndo
glyphWindowDidOpen
glyphWindowWillClose
glyphWindowWillOpen
spaceCenterDidOpen
spaceCenterWillClose
spaceCenterWillOpen
""".strip()
knownEvents = [i for i in knownEvents.splitlines() if i and not i.startswith("#")]

boringMode = {
    "applicationDidFinishLaunching"  : {
        "frequency" : 1.0,
        "speak" : "Welcome to RoboFont version {robofontVersion} build {robofontBuild}.",
        "sound" : "no sound"
    }
}

coachMode = {
    "applicationDidBecomeActive" : {
        "frequency" : 1.0,
        "sound" : "no sound",
        "speak" : "Welcome back! Let's get to work. | Oh yeah! Back for more!"
    },
    "applicationDidFinishLaunching" : {
        "frequency" : 1.0,
        "sound" : "no sound",
        "speak" : "Boom. Let's do this! | Oh yeah, you look ready to work!"
    },
    "applicationWillResignActive" : {
        "frequency" : 1.0,
        "sound" : "no sound",
        "speak" : "Don't you quit on me now! | Take a few minutes to clear your head, then let's get back to it."
    },
    "binaryFontWillOpen" : {
        "frequency" : 1.0,
        "sound" : "no sound",
        "speak" : "Don't compare yourself to others. | You be you. This is your journey"
    },
    "currentGlyphChanged" : {
        "frequency" : 0.5,
        "sound" : "no sound",
        "speak" : "Oh yeah! This is looking good. | Good start, but it needs some work. | You nailed it. | Wow! | You're the best!"
    },
    "cut" : {
        "frequency" : 0.1,
        "sound" : "no sound",
        "speak" : "Get that out of here!"
    },
    "fontDidGenerate" : {
        "frequency" : 0.6,
        "sound" : "no sound",
        "speak" : "Oh yeah! Oh yeah!"
    },
    "fontDidSave" : {
        "frequency" : 0.5,
        "sound" : "no sound",
        "speak" : "Great work! | Good idea. | This font is everything!"
    },
    "fontWillOpen" : {
        "frequency" : 0.4,
        "sound" : "no sound",
        "speak" : "Let's do this! | You got this! | That's what I'm talking about!"
    },
    "newFontDidOpen" : {
        "frequency" : 0.5,
        "sound" : "no sound",
        "speak" : "Fresh start! | Today is a new day!"
    }
}

verboseMode = {
    "applicationDidBecomeActive" : {
        "frequency" : 1.0,
        "sound" : "no sound",
        "speak" : "Application did become active."
    },
    "applicationDidFinishLaunching" : {
        "frequency" : 1.0,
        "sound" : "no sound",
        "speak" : "Application did finish launching."
    },
    "applicationScreenChanged" : {
        "frequency" : 1.0,
        "sound" : "no sound",
        "speak" : "Application screen changed."
    },
    "applicationWillResignActive" : {
        "frequency" : 1.0,
        "sound" : "no sound",
        "speak" : "Application will resign active."
    },
    "binaryFontWillOpen" : {
        "frequency" : 1.0,
        "sound" : "no sound",
        "speak" : "Binary font will open."
    },
    "currentGlyphChanged" : {
        "frequency" : 1.0,
        "sound" : "no sound",
        "speak" : "Glyph {glyphName} is now current."
    },
    "fontBecameCurrent" : {
        "frequency" : 1.0,
        "sound" : "no sound",
        "speak" : "Font {fontFamilyName} {fontStyleName} became current."
    },
    "fontDidAutoSave" : {
        "frequency" : 1.0,
        "sound" : "no sound",
        "speak" : "Font {fontFamilyName} {fontStyleName} did auto save."
    },
    "fontDidChangeExternally" : {
        "frequency" : 1.0,
        "sound" : "no sound",
        "speak" : "Font {fontFamilyName} {fontStyleName} changed externally."
    },
    "fontDidGenerate" : {
        "frequency" : 1.0,
        "sound" : "no sound",
        "speak" : "Font {fontFamilyName} {fontStyleName} did generate."
    },
    "fontDidOpen" : {
        "frequency" : 1.0,
        "sound" : "no sound",
        "speak" : "Font {fontFamilyName} {fontStyleName} did open."
    },
    "fontDidSave" : {
        "frequency" : 1.0,
        "sound" : "no sound",
        "speak" : "Font {fontFamilyName} {fontStyleName} did save."
    },
    "fontResignCurrent" : {
        "frequency" : 1.0,
        "sound" : "no sound",
        "speak" : "Font {fontFamilyName} {fontStyleName} resigned current."
    },
    "fontWillAutoSave" : {
        "frequency" : 1.0,
        "sound" : "no sound",
        "speak" : "Font {fontFamilyName} {fontStyleName} will auto save."
    },
    "fontWillClose" : {
        "frequency" : 1.0,
        "sound" : "no sound",
        "speak" : "Font {fontFamilyName} {fontStyleName} will close."
    },
    "fontWillGenerate" : {
        "frequency" : 1.0,
        "sound" : "no sound",
        "speak" : "Font {fontFamilyName} {fontStyleName} will generate."
    },
    "fontWillOpen" : {
        "frequency" : 1.0,
        "sound" : "no sound",
        "speak" : "Font will open."
    },
    "fontWillSave" : {
        "frequency" : 1.0,
        "sound" : "no sound",
        "speak" : "Font {fontFamilyName} {fontStyleName} will save."
    },
    "newFontDidOpen" : {
        "frequency" : 1.0,
        "sound" : "no sound",
        "speak" : "New font did open."
    },
    "newFontWillOpen" : {
        "frequency" : 1.0,
        "sound" : "no sound",
        "speak" : "New font will open."
    }
}

# --------
# Defaults
# --------

extensions.registerExtensionDefaults(
    {
        defaultStub + "audible" : True,
        defaultStub + "soundDirectory" : "",
        defaultStub + "events" : coachMode,
    }
)

# ----------
# Controller
# ----------

class _RoboSoundsController(object):

    def __init__(self):
        self.loadUserDefaults()
        self.loadSounds()

    # -----------
    # Observation
    # -----------

    def isListening(self):
        return self._isListening

    def startListening(self):
        if self.isListening():
            self.stopListening()
        for event in self._events.keys():
            addObserver(self, "eventCallback", event)
        self._isListening = True
        self._storeAudibleDefault()

    def stopListening(self):
        for event in self._events.keys():
            removeObserver(self, event)
        self._isListening = False
        self._storeAudibleDefault()

    def eventCallback(self, notification):
        event = notification["notificationName"]
        if event not in self._events:
            return
        data = self._events[event]
        if data is not None:
            frequency = data["frequency"]
            if frequency == 0:
                return
            elif frequency < 1.0:
                if frequency > random.random():
                    return
            self.playEvent(event, notification)

    # -------------
    # User Settings
    # -------------

    def loadUserDefaults(self):
        self._soundDirectory = extensions.getExtensionDefault(
            defaultStub + "soundDirectory"
        )
        self._isListening = extensions.getExtensionDefault(
            defaultStub + "audible"
        )
        self._events = extensions.getExtensionDefault(
            defaultStub + "events"
        )
        if self._isListening:
            self.startListening()

    def _storeAudibleDefault(self):
        extensions.setExtensionDefault(
            defaultStub + "audible",
            self.isListening()
        )

    def getUserDefinedEvents(self):
        return self._events

    def setUserDefinedEvents(self, events):
        self._events = events
        extensions.setExtensionDefault(
            defaultStub + "events",
            events
        )
        self.startListening()

    def getSoundDirectory(self):
        return self._soundDirectory

    def setSoundDirectory(self, path):
        self._soundDirectory = path
        extensions.setExtensionDefault(
            defaultStub + "soundDirectory",
            path
        )
        self.loadSounds()

    def loadSounds(self):
        self._sounds = {}
        directory = self.getSoundDirectory()
        if directory and os.path.exists(directory):
            for fileName in os.listdir(directory):
                path = os.path.join(directory, fileName)
                sound = NSSound.alloc().initWithContentsOfFile_byReference_(
                    path,
                    False
                )
                if sound is not None:
                    self._sounds[fileName] = sound

    def getSoundNames(self):
        return list(sorted(self._sounds.keys()))

    # ----
    # Play
    # ----

    def playEvent(self, event, notificationData=None):
        if event not in self._events:
            return
        if notificationData is None:
            notificationData = {}
        data = self._events[event]
        text = data.get("speak")
        if text:
            text = populateText(text, notificationData)
            synthesizer = NSSpeechSynthesizer.alloc().initWithVoice_(None)
            synthesizer.startSpeakingString_(text)
        sound = data.get("sound")
        if sound != "no sound" and sound in self._sounds:
            sound = self._sounds[sound]
            sound.play()


def populateText(text, data):
    if "|" in text:
        text = random.choice(text.split("|"))
    replacements = {
        "robofontVersion" : mojo.roboFont.version,
        "robofontBuild" : mojo.roboFont.buildNumber,
        "userName" : NSFullUserName(),
        "fontFileName" : "Unknown Font File Name",
        "fontFamilyName" : "Unknown Font Family Name",
        "fontStyleName" : "Unknown Font Style Name",
        "glyphName" : "Unknown Glyph Name",
        "glyphCharacter" : "Unknown Glyph Character",

    }
    if "font" in data and data["font"] is not None:
        font = data["font"]
        fileName = font.path
        if fileName is None:
            fileName = "unsaved file"
        else:
            fileName = os.path.basename(fileName)
        replacements["fontFileName"] = fileName
        replacements["fontFamilyName"] = font.info.familyName
        replacements["fontStyleName"] = font.info.styleName
    if "glyph" in data and data["glyph"] is not None:
        glyph = data["glyph"]
        replacements["glyphName"] = glyph.name
        if glyph.unicode is None:
            character = "undefined character"
        else:
            character = chr(glyph.unicode)
        replacements["glyphCharacter"] = character
    text = text.format(**replacements)
    return text


# ---------
# Interface
# ---------

class RoboSoundsWindowController(BaseWindowController):

    def __init__(self):
        self.soundTitles = ["no sound"] + RoboSoundsController.getSoundNames()

        self.w = vanilla.Window((800, 200), "RoboSounds", minSize=(200, 200))

        columnDescriptions = [
            dict(
                key="event",
                title="Event"
            ),
            dict(
                key="frequency",
                title="Frequency",
                cell=vanilla.SliderListCell(minValue=0, maxValue=1.0, tickMarkCount=20, stopOnTickMarks=True)
            ),
            dict(
                key="speak",
                title="Speak"
            ),
            dict(
                key="sound",
                title="Sound",
                cell=vanilla.PopUpButtonListCell(self.soundTitles),
                binding="selectedValue"
            )
        ]
        self.w.list = vanilla.List("auto", [], columnDescriptions=columnDescriptions, editCallback=self.listEditCallback)
        self.w.addButton = vanilla.GradientButton("auto", imageNamed=NSImageNameAddTemplate, callback=self.addButtonCallback)
        self.w.removeButton = vanilla.GradientButton("auto", imageNamed=NSImageNameRemoveTemplate, callback=self.removeButtonCallback)
        self.w.flex = vanilla.Group("auto")
        self.w.playButton = vanilla.Button("auto", title="▶︎", callback=self.playButtonCallback)
        self.w.playButton.getNSButton().setBordered_(False)
        options = [
            dict(title="Select Sound Directory…", callback=self.selectSoundDirectoryCallback),
            dict(title="Reload Sounds", callback=self.reloadSoundsCallback),
            "----",
            dict(title="Prebuilt Settings", items=[
                    dict(title="Verbose", callback=self.importSettingsVerboseCallback),
                    dict(title="Coach", callback=self.importSettingsCoachCallback),
                    dict(title="Boring", callback=self.importSettingsBoringCallback)
                ]
            ),
            dict(title="Import Settings…", callback=self.importSettingsCallback),
            dict(title="Export Settings…", callback=self.exportSettingsCallback)
        ]
        self.w.optionsButton = vanilla.ActionButton("auto", options, bordered=False)

        metrics = dict(
            border=15,
            space=10,
            button=20
        )
        rules = [
            "H:|-border-[list]-border-|",
            "H:|-border-[addButton(==button)][removeButton(==button)][flex(>=50)][playButton]-space-[optionsButton]-border-|",
            "V:|-border-[list(>=200)]-space-[addButton(==button)]-border-|",
            "V:|-border-[list(>=200)]-space-[removeButton(==button)]-border-|",
            "V:|-border-[list(>=200)]-space-[flex]-border-|",
            "V:|-border-[list(>=200)]-space-[playButton(==button)]-border-|",
            "V:|-border-[list(>=200)]-space-[optionsButton(==button)]-border-|"
        ]
        self.w.addAutoPosSizeRules(rules, metrics)

        self.populateList()
        self.setUpBaseWindowBehavior()
        RoboSoundsController.startListening()
        self.w.open()

    # List Interaction

    def populateList(self):
        self.populatingList = True
        order = list(knownEvents)
        storedEvents = RoboSoundsController.getUserDefinedEvents()
        for event in sorted(storedEvents.keys()):
            if event not in order:
                order.append(event)
        events = []
        for event in order:
            data = blankListItem()
            data["event"] = event
            data["locked"] = False
            if event in knownEvents:
                data["locked"] = event
            if event in storedEvents:
                stored = storedEvents[event]
                data["speak"] = stored["speak"]
                sound = stored["sound"]
                if sound not in self.soundTitles:
                    sound = "no sound"
                data["sound"] = sound
            events.append(data)
        self.w.list.set(events)
        del self.populatingList

    def listEditCallback(self, sender):
        if hasattr(self, "populatingList"):
            return
        events = {}
        for data in sender.get():
            event = data["event"]
            if data["locked"]:
                event = data["locked"]
            frequency = data["frequency"]
            if "speak" not in data:
                speak = ""
            else:
                speak = data["speak"].strip()
            sound = data["sound"]
            if not speak and not sound:
                continue
            events[event] = dict(frequency=frequency, speak=speak, sound=sound)
        RoboSoundsController.setUserDefinedEvents(events)

    def addButtonCallback(self, sender):
        data = blankListItem()
        self.w.list.append(data)

    def removeButtonCallback(self, sender):
        eventList = self.w.list
        selection = eventList.getSelection()
        toRemove = []
        for index in selection:
            data = eventList[index]
            if data["locked"]:
                NSBeep()
                continue
            toRemove.append(index)
        for index in reversed(toRemove):
            del eventList[index]

    # Audio Preview

    def playButtonCallback(self, sender):
        eventList = self.w.list
        selection = eventList.getSelection()
        for index in selection:
            event = eventList[index]["event"]
            RoboSoundsController.playEvent(event)

    # Sound Files

    def selectSoundDirectoryCallback(self, sender):
        self.showGetFolder(
            self._selectSoundDirectoryCallback
        )

    def _selectSoundDirectoryCallback(self, paths):
        if not paths:
            return
        path = paths[0]
        RoboSoundsController.setSoundDirectory(path)
        self.populateList()

    def reloadSoundsCallback(self, sender):
        RoboSoundsController.loadSounds()
        self.populateList()

    # Import/Export

    def importSettingsCallback(self, sender):
        self.showGetFile(
            ["robosounds"],
            self._importSettingsCallback
        )

    def _importSettingsCallback(self, paths):
        if not paths:
            return
        path = paths[0]
        settings = plistlib.readPlist(path)
        RoboSoundsController.setUserDefinedEvents(settings)
        self.populateList()

    def exportSettingsCallback(self, sender):
        self.showPutFile(
            ["robosounds"],
            self._exportSettingsCallback,
            fileName="My Awesome Sound Settings"
        )

    def _exportSettingsCallback(self, path):
        if not path:
            return
        settings = RoboSoundsController.getUserDefinedEvents()
        plistlib.writePlist(settings, path)

    # Prebuilt

    def importSettingsBoringCallback(self, sender):
        RoboSoundsController.setUserDefinedEvents(boringMode)
        self.populateList()

    def importSettingsCoachCallback(self, sender):
        RoboSoundsController.setUserDefinedEvents(coachMode)
        self.populateList()

    def importSettingsVerboseCallback(self, sender):
        RoboSoundsController.setUserDefinedEvents(verboseMode)
        self.populateList()


def blankListItem():
    return dict(event="anUnknownEvent", locked=False, frequency=1.0, speak="", sound="no sound")


# ------
# Launch
# ------

RoboSoundsController = _RoboSoundsController()
