# RoboSounds

Have you ever wanted RoboFont to sound like a video game? _Of course you have._

## Interface

### Event List

- Event: This is the event that will initiate the audio. The standard RoboFont events are built in. You can define your own.
- Frequency: This defines how often the audio should be played when the event is observed. All the way to the right is "always," all the way to the left is "never," and somewhere in the middle is "somewhere in the middle."
- Speak: The phrase to speak. This can be blank. See below fgor exciting options.
- Sound: The sound file to play. This can be "no sound" or a known sound file.

### Action Menu

- "Select Sound Directory…" All of the sounds must be in one directory. Choose the directory with this.
- "Reload Sounds" Reload all the sounds in the directory. You only need to do this if you add a sound file after RoboSounds has started.
- "Import Settings…" Did your friend tell you that their settings are awesome? Import them with this.
- "Export Settings…" Did you tell your friend that your settings are awesome? Export them with this.

### "Speak" Options

#### |

If you have more than one phrase assigned to an event, use a `|` as delimiter between phrases in the string. RoboSounds will choose one to play.

#### Dynamic Text

RoboSounds can insert text based on the current state of RoboFont. These are the options:

- {robofontVersion}
- {robofontBuildNumber}
- {userName}
- {fontFileName}
- {fontFamilyName}
- {fontStyleName}
- {glyphName}
- {glyphCharacter}

---

### Defining Your Own Events

RoboSounds uses [mojo.events](https://robofont.com/documentation/building-tools/api/mojo/mojo-events/) to observer event notifications. Any event that passes through [mojo.events.postEvent](https://robofont.com/documentation/building-tools/api/mojo/mojo-events/#mojo.events.postEvent) can be an event in RoboSounds.