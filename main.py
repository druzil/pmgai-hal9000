#
# This file is part of The Principles of Modern Game AI.
# Copyright (c) 2015, AiGameDev.com KG.
#

import vispy                    # Main application support.
import nltk.chat
import window                   # Terminal input and display.
import win32com.client
import speech_recognition as sr

class HAL9000(object):
    
    AGENT_RESPONSES = [
      (r'You are (worrying|scary|disturbing)',    # Pattern 1.
        ['Yes, I am %1.',                         # Response 1a.
         'Oh, sooo %1.']),

      (r'Are you ([\w\s]+)\?',                    # Pattern 2.
        ["Why would you think I am %1?",          # Response 2a.
         "Would you like me to be %1?"]),

      (r'',                                       # Pattern 3. (default)
        ["Is everything OK?",                     # Response 3a.
         "Can you still communicate?"])
    ]

    first = True

    def __init__(self, terminal):
        """Constructor for the agent, stores references to systems and initializes internal memory.
        """
        self.terminal = terminal
        self.location = 'unknown'
        self.chatbot = nltk.chat.Chat(self.AGENT_RESPONSES, nltk.chat.util.reflections)
        self.voice = win32com.client.Dispatch("SAPI.SpVoice")
        self.recog = sr.Recognizer()
        self.recog.energy_threshold = 1000           # Tune based on ambient noise levels [1000,4000].

    def on_input(self, evt):
        """Called when user types anything in the terminal, connected via event.
        """
        if evt.text == "Where am I?":
            self.terminal.log("On the Starship Entreprise.", align='right', color='#00805A')
        else:
            if self.first:
                self.terminal.log("Howdy! I'm HAL.", align='right', color='#00805A')
                self.voice.Speak('Good afternoon! My name is Hal.')
                self.first = False
            else:
                self.voice.Speak(evt.text)
                resp1 = self.chatbot.respond(evt.text)
                self.terminal.log(resp1, align='right', color='#00805A')

    def on_command(self, evt):
        """Called when user types a command starting with `/` also done via events.
        """
        if evt.text == 'quit':
            vispy.app.quit()

        elif evt.text.startswith('relocate'):
            self.terminal.log('', align='center', color='#404040')
            self.location = evt.text[9:]
            self.terminal.log('\u2014 Now in the {}. \u2014'.format(self.location), align='center', color='#404040')
             

        else:
            self.terminal.log('Command `{}` unknown.'.format(evt.text), align='left', color='#ff3000')    
            self.terminal.log("I'm afraid I can't do that.", align='right', color='#00805A')

    def update(self, _):
        """Main update called once per second via the timer.
        """
        #with sr.Microphone() as source:     # Use the default microphone as the audio source.
        #    audio = self.recog.listen(source)        # Listen for single phrase and extract as audio.

        #try:
        #    text = recog.recognize_google(audio)       # Extract text using Google Speech Recognition.
        #    #print(text)
        #    self.terminal.log(text, align='right', color='#00805A')
        #except LookupError:
        #    text = None                     # Could not recognize anything from audio...
        pass


class Application(object):
    
    def __init__(self):
        # Create and open the window for user interaction.
        self.window = window.TerminalWindow()

        # Print some default lines in the terminal as hints.
        self.window.log('Operator started the chat.', align='left', color='#808080')
        self.window.log('HAL9000 joined.', align='right', color='#808080')

        # Construct and initialize the agent for this simulation.
        self.agent = HAL9000(self.window)

        # Connect the terminal's existing events.
        self.window.events.user_input.connect(self.agent.on_input)
        self.window.events.user_command.connect(self.agent.on_command)

    def run(self):
        timer = vispy.app.Timer(interval=1.0)
        timer.connect(self.agent.update)
        timer.start()
        
        vispy.app.run()


if __name__ == "__main__":
    vispy.set_log_level('WARNING')
    vispy.use(app='glfw')
    
    app = Application()
    app.run()
