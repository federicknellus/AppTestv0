import keyboard
from kivy.app import App
from kivy.uix.button import Button
from kivy.properties import ListProperty, StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
import sqlalchemy as sql
import pandas as pd
from datetime import date
from kivy.core.window import Window
from kivy.uix.textinput import Clipboard
from kivy.uix.widget import Widget
from keyboard import *
from supermemo2 import SMTwo
# Bisogna implementare una variabile che tenga conto se ci sono o meno domande disponibili:
# Se non ci sono deve far vedere la scritta : non ci sono domande disponibili
# Se ci sono deve far vedere le domande
# Una volta terminate le domande deve far vedere la stessa schermata di quando non ci sono domande disponibili
# Un bottone "Show Answer" e poi n=5 bottoni per quanto riguarda la valutazione che si baserà su algoritmo SMTwo
# Serve una funzione che prenda dal database SQL le card con data review antecedente ad oggi e le immagazzini in un
# dizionario con chiave domanda e valore risposta. Poi si deve accedere alle chiavi e relative risposte, successivamente
# una funzione aggiornerà nel DB la review date futura in questo modo se l'app si restarta prenderà solo i valori nuovi
# e sul dizionario si tiene traccia delle domande perchè si percorre la lista delle keys.
# Le card devono avere un attributo "new" per contare numero totale, da revieware e nuove (volendo si può comprendere
# in quelle da revieware).
# Poi implementare funzioni per aggiungere card/immagini/ aggiungere tante card usando file csv.
days= {0:"Monday", 1:"Tuesday", 2:"Wednesday", 3: "Thursday", 4:"Friday", 5:"Saturday",6:"Sunday"}
months={'01': "January", '02':'February','03': "March", '04':'April','05': "May", '06':'June','07': "July",
        '08':'August','09': "September", '10':'October','11': "November", '12':'December'}

if f('Command') == True and f('a') == True:
    print('fa')
class SpacedRepetitionMenu(Screen):
    oggi = StringProperty(str(date.today()))
    menuinterval = 5
    numberofcards = StringProperty()
    numberofcardstostudy = StringProperty()
    therearequestions = BooleanProperty()
    showanswerlock = BooleanProperty()
    question = StringProperty("")
    answer = StringProperty("")
    showanswertext = StringProperty("Show Answer")
    questions = ListProperty()
    macro = []


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update()
        Clock.schedule_interval(self.update, self.menuinterval)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down, on_key_up=self._on_keyboard_up)

    def test(self):
        print("HA FUNTO")
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == '0' and not self.showanswerlock:
            print("0")
            self.vote0()
        elif keycode[1] == '1' and not self.showanswerlock:
            print("1")
            self.vote1()
        elif keycode[1] == '2' and not self.showanswerlock:
            print("2")
            self.vote1()
        elif keycode[1] == '3' and not self.showanswerlock:
            print("3")
            self.vote3()
        elif keycode[1] == '4' and not self.showanswerlock:
            print("4")
            self.vote4()
        elif keycode[1] == '5' and not self.showanswerlock:
            print("5")
            self.vote5()
        if keycode[1] not in self.macro:
            self.macro.append(keycode[1])
            print(keycode,self.manager.current,keyboard,text,modifiers)
        if self.addmacro(['super','1']):
            self.manager.current = 'home'
        if self.addmacro((['super','enter'])) and self.manager.current == 'addareaspacedrepetition':
            self.addbuttonspacedrepetition()
        if self.addmacro(['super','2']):
            self.manager.current = 'spacedrepetitionmenu'
        if self.addmacro(['super','shift','a']):
            self.manager.current = 'addareaspacedrepetition'
        return True

    def _on_keyboard_up(self, keyboard, keycode):
        try:
            self.macro.remove(keycode[1])
        except:
            pass
    def addmacro(self,l):
        return all(i in self.macro for i in l)


    def update(self, dt=0):
        self.oggi = str(date.today())
        self.numberofcards = str(self.countcards())
        self.numberofcardstostudy = str(self.countcardstostudy())
        self.therearequestions = self.istheretostudy()
        self.questions = self.ottienidomandedaldb()

    def askquestion(self):
        if 'showanswerbutton' not in self.ids.votearea.ids:
            self.question = self.questions[0][0]
            self.sbloccashowanser()
            self.addshowanswerbutton()

    def ottienidomandedaldb(self):
        query = 'SELECT * FROM Cards WHERE review <= "' + self.oggi + '" OR new == "1" ORDER BY review;'
        result = pd.read_sql_query(query, sql.create_engine('sqlite:///spacedrepetition.sqlite'))
        domande_disponibili = []
        for index, row in result.iterrows():
            card = (str(row.front), str(row.back), str(row.added), str(row.review), str(row.new), str(row.easiness),
                    str(row.interval),str(row.repetitions))
            domande_disponibili.append(card)
        return domande_disponibili

    def addshowanswerbutton(self):
        b = Button(text=self.showanswertext if not self.showanswerlock else '',
                   on_press=self.showvotebuttons)
        self.ids['showanswerbutton'] = b
        self.ids.votearea.add_widget(b)

    def hideshowanswerbutton(self):
        self.ids.votearea.remove_widget(self.ids.showanswerbutton)

    def hidevotebuttons(self,*args):
        self.ids.votearea.clear_widgets()

    def showvotebuttons(self,*args):
        if not self.showanswerlock:
            self.ids.votearea.remove_widget(self.ids.showanswerbutton)
            self.ids.votearea.add_widget(Button(text='0', on_press=self.vote0))
            self.ids.votearea.add_widget(Button(text='1', on_press=self.vote1))
            self.ids.votearea.add_widget(Button(text='2', on_press=self.vote2))
            self.ids.votearea.add_widget(Button(text='3', on_press=self.vote3))
            self.ids.votearea.add_widget(Button(text='4', on_press=self.vote4))
            self.ids.votearea.add_widget(Button(text='5', on_press=self.vote5))
            self.answer = self.questions[0][1]

    def vote0(self,*args):
        print("vote0")
        self.calcolaspaced(0,self.questions[0][4])
        self.voted()
    def vote1(self,*args):
        print("vote1")
        self.calcolaspaced(1,self.questions[0][4])
        self.voted()

    def vote2(self,*args):
        print("vote2")
        self.calcolaspaced(2,self.questions[0][4])
        self.voted()

    def vote3(self,*args):
        print("vote3")
        self.calcolaspaced(3,self.questions[0][4])
        self.voted()

    def vote4(self,*args):
        print("vote4")
        self.calcolaspaced(4,self.questions[0][4])
        self.voted()

    def vote5(self,*args):
        print("vote5")
        self.calcolaspaced(5,self.questions[0][4])
        self.voted()

    def calcolaspaced(self, value,new):
        review =None
        if new == "1":
            query = 'UPDATE Cards SET new = "0" WHERE front == "' + self.questions[0][0] \
                    + '" AND back == "' + self.questions[0][1] + '";'
            sql.create_engine('sqlite:///spacedrepetition.sqlite').execute(query)
            review = SMTwo.first_review(value, self.oggi)
        else:
            review = SMTwo(float(self.questions[0][5]),int(self.questions[0][6]),int(self.questions[0][7])).review(value)
        query = 'UPDATE Cards SET review = "' + str(review.review_date) + '", easiness = "'+str(review.easiness)+'", \
                interval = "'+str(review.interval)+'", repetitions = "'+str(review.repetitions)+'" WHERE front == "' \
                + self.questions[0][0] + '" AND back == "' + self.questions[0][1] + '";'
        sql.create_engine('sqlite:///spacedrepetition.sqlite').execute(query)
    def voted(self, *args):
        self.hidevotebuttons()
        self.answer = ''
        self.hideshowanswerbutton()
        self.update()
        if len(self.questions) == 0 :
            self.hideshowanswerbutton()
            self.bloccashowanswer()
            self.question = ''
            self.therearequestions = False
            self.hideshowanswerbutton()
        else:
            self.addshowanswerbutton()
            self.question = self.questions[0][0]
    def sbloccashowanser(self):
        self.showanswerlock = False
    def bloccashowanswer(self):
        self.showanswerlock = True
    def countcards(self):
        query = 'SELECT COUNT(ROWID) AS count FROM Cards;'
        return int(pd.read_sql_query(query, sql.create_engine('sqlite:///spacedrepetition.sqlite'))['count'])

    def countcardstostudy(self):
        query = 'SELECT * FROM Cards WHERE review <= "' + self.oggi + '" OR new == "1" ORDER BY review;'
        result = pd.read_sql_query(query, sql.create_engine('sqlite:///spacedrepetition.sqlite'))
        return len(list(result['front']))

    def istheretostudy(self):
        if int(self.numberofcardstostudy) > 0:
            return True
        else:
            return False

class NellusMenu(Screen):
    data = StringProperty()
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.data = days[date.today().weekday()] +", " + str(date.today()).split('-')[2]+ ' ' +\
                    months[str(date.today()).split('-')[1]]+ ' '+ str(date.today()).split('-')[0]
        print(self.data)

class Header(GridLayout):
    pass

class AddAreaSpacedRepetition(Screen):
    today = StringProperty(str(date.today()))
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update,60)

    def addbuttonspacedrepetition(self):
        if len(self.ids.frontlabelti.text)>0 and len(self.ids.backlabelti.text)>0:
            query = 'INSERT INTO Cards (front, back, added, new) VALUES ("'+self.ids.frontlabelti.text+'","' \
                +self.ids.backlabelti.text+'","'+self.today+'","' + "1" + '");'
            sql.create_engine('sqlite:///spacedrepetition.sqlite').execute(query)
            self.ids.frontlabelti.text = ""
            self.ids.backlabelti.text = ""
    def update(self, dt=0):
        self.today = str(date.today())
class SpacedRepetitionQA(Screen):
    pass

class ScreenManager(ScreenManager):
    pass
class MyApp(App):
    def build(self):

        return

MyApp().run()
