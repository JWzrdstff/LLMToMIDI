# LLMToMIDI
Workflow for creating MIDI files using an input (text, image, video, audio) with an LLM.

Copy and paste contents of AnalysisToMidiVectorPrompt.txt into a new LLM chat window and send.
LLM will assume the role of analyst/JSON generator. Give the prompt an input to analyze. Give it as much or as little additional instruction as you'd like. 
Copy and paste json output into a plain text file and save it. You will use the name of your json file in the python script, replacing placeholder "OrangeChairs."
When you run the python script it will export the .mid files in whichever directory it is in. The json and the python file must be in the same folder.
