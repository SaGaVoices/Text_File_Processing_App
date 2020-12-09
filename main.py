import PySimpleGUI as sg 
import nltk
import os
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def processfile(textfile):
    try:
        f = open(textfile, encoding="utf8")
        ftext = f.read()
        f.close()

        # Calculate number of lines
        no_of_lines = str(len(ftext.split('\n')))
    
        # Calculate number of sentences
        sentence_tokens = nltk.sent_tokenize(ftext)
        no_of_sentences = str(len(sentence_tokens))

        # Calculate number of words
        word_tokens = nltk.word_tokenize(ftext)
        punctuation_removed_word_tokens = [token for token in word_tokens if token.isalnum()]
        no_of_words = str(len(punctuation_removed_word_tokens))

        # Calculating most and least frequent words (excluding common words)
        lemma = nltk.WordNetLemmatizer()
        lemmatized_words = [lemma.lemmatize(token.lower()) for token in punctuation_removed_word_tokens]
        
        stop_words = set(nltk.corpus.stopwords.words('english'))
        relevant_words = [word for word in lemmatized_words if word not in stop_words and len(word)>2]

        freq_dist = nltk.FreqDist(relevant_words)
        freq_map = dict(freq_dist)

        sorted_freq_map = sorted(freq_map.items(), key = lambda elem: elem[1], reverse = True)
        most_freq = sorted_freq_map[0][0]
        least_freq = sorted_freq_map[-1][0]

        # Print stats
        window['_WORDS_'].update(no_of_words)
        window['_SENTENCES_'].update(no_of_sentences)
        window['_LINES_'].update(no_of_lines)
        window['_MF_'].update(most_freq)
        window['_LF_'].update(least_freq)
        
        # Plotting the frequency of 20 most frequent words
        f=[[x,y] for x,y in sorted_freq_map][:20]
        plt.clf()
        plt.bar([x[0] for x in f],[x[1] for x in f])
        plt.xticks(rotation=45)

    except FileNotFoundError:
        pass
    
def extractline(textfile,keyword):
    # Sentences
    f1 = open(textfile, encoding="utf8")
    sentences=nltk.sent_tokenize(f1.read())
    f1.close()
    
    # Keywords
    f2 = open(keyword, encoding="utf8")
    keywords=f2.read().split('\n')
    f2.close()

    for sentence in sentences:
        flag=False
        for keyword in keywords:
            if keyword in sentence:
                flag=True
                break
        if(flag):
            window['-EXTRACT-'].print(sentence)

def draw_figure(canvas, figure, loc=(0, 0)):
    # Standard function for drawing matplotlib figures in PySimpleGUI
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def prompt():
    # Prompt user for filename input
    prompt_layout = [[sg.Text("Please provide a file as input.",size=(30,1),justification='center')],[sg.Button("OK",size=(8,1))]]
    prompt_window = sg.Window('No File Selected',prompt_layout,font="Helvetica 12")
    event,values = prompt_window.read()
    if event == 'OK': prompt_window.close()

# GUI Theme
sg.theme("Black")

# GUI Layout
file_list_column = [
    [
        sg.Text("File:",size=(4,1)),
        sg.In(size=(36, 1), enable_events=True, key="-FOLDER-"),
        sg.FileBrowse(size=(8,1)),
        sg.Button("Edit",size=(8,1)),
        sg.Button("Go",size=(8,1))
    ],
    [
        sg.Text("Words: ",size=(6,1)),
        sg.Text("", size=(6, 1), justification='center', key='_WORDS_'),
        sg.Text("Lines: ",size=(6,1)),
        sg.Text("", size=(4, 1), justification='center', key='_LINES_'),
        sg.Text("Sentences: ",size=(9,1)),
        sg.Text("", size=(4, 1), justification='center', key='_SENTENCES_')
    ],
    [
        sg.Text("Most frequent: ",size=(12,1)),
        sg.Text("", size=(11, 1), key='_MF_'),
        sg.Text("Least freqeunt: ",size=(12,1)),
        sg.Text("", size=(11, 1), key='_LF_')
    ],
    [
        sg.Text("Keywords File:",size=(12,1)),
        sg.In(size=(38, 1), enable_events=True, key="-KeyWord-"),
        sg.FileBrowse(size=(8,1)),
        sg.Button("Extract",size=(8,1))
    ],
    [
        sg.Multiline(size=(74,15), key='-EXTRACT-')
    ]
]

layout = [
    [
        sg.Column(file_list_column,justification='center'),
    ]
]

# Initialize main window
window = sg.Window('Text Analysis', layout,font="Helvetica 9")  
window2 = 0

while True: 
    event, values = window.read() 
    
    if event in (None, 'Exit'): 
        break
    
    if event == 'Go':
        if(values['-FOLDER-']!=''):
            if(type(window2)!=int): window2.close()
            processfile(values['-FOLDER-'])
            layout2 = [[sg.Text("Histogram of word frequencies")],[sg.Canvas(key="-CANVAS-")]]
            window2 = sg.Window("Histogram",layout2,location=(0, 0),finalize=True,element_justification="center",font="Helvetica 18")
            fig=plt.gcf()
            fig_photo = draw_figure(window2['-CANVAS-'].TKCanvas, fig)
            window["Go"].Update("Refresh")
        else:
            prompt()


    if event == 'Edit':
        if(values['-FOLDER-']!=''):
            if sys.platform=='win32':
                os.system('Notepad '+values['-FOLDER-'])
            elif sys.platform=='Linux':
                os.system('gedit '+values['-FOLDER-'])
        else:
            prompt()

    if event == 'Extract':
        if(values['-FOLDER-']!='' and values['-KeyWord-']!=''):
            extractline(values['-FOLDER-'],values['-KeyWord-'])
        else:
            prompt()

if(type(window2)!=int): window2.close()
window.close()
