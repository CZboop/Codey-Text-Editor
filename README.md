# Text-Editor
Text editor intended for creative/human language writing but with features inspired by code editors. Made with Python, using PyQt, NLTK and Regex. 

Uses multithreading to enable processes to run in the background without impacting user experience. Worker threads emit signals to pass information back to the main GUI application.

Key features:
- Able to 'comment out' lines of text using the Ctrl + / keyboard shortcut or by adding the # character to the start of a line
- Verbs, nouns, adjectives and adverbs are automatically highlighted in different colours based on their part of speech

Highlighting based on part of speech is achieved by overriding the highlightBlock method of the QSyntaxHighlighter class in a child class. This method goes through the formatting conditions, first checking if they are callable. Part of speech highlighting conditions will be callable and return true or false for the corresponding part of speech using some NLTK logic. The index of the words that meet the condition are found using regex and highlighted using the built in methods of the parent QSyntaxHighlighter class. Standard regex conditions are also used to highlight out comments.

Other functionality:
- Save and load files
- Highlighting colours are customisable, with the default inspired by the Dracula colour scheme
- Quotes and brackets are automatically closed when an opening one is typed
- Italicise and bold text with Ctrl + i and Ctrl + b keyboard shortcuts or from the menu
- Increase or decrease font size with Ctrl + = and Ctrl + - keyboard shortcuts or from the menu
