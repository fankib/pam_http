import sys
import os
import client
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import Clock

is_linux = sys.platform == 'linux'
is_android = sys.platform == 'linux4'

if is_android:
	from plyer import vibrator

if is_linux:
	os.environ['JAVA_HOME'] = '/usr/lib/jvm/java-8-openjdk/'

class LockI(App):
	txtServer = TextInput(text='http://192.168.1.57:5000', hint_text='Server', padding=30, font_size=30, multiline=False)
	txtSecret = TextInput(text='', hint_text='Secret', padding=30, font_size=30, multiline=False, password=True)
	lblResult = Label(text='')
	
	def on_pause(self):
		return True
	
	def build(self):
		# initialize components
		lblHead = Label(text='LockI - v0.2', font_size=40)
		btnUnlock = Button(text='unlock', size_hint_x=None, width=260, background_color=(0.75, 0.87, 0.78, 1.0), on_press=self.unlock)
		btnLock = Button(text='lock', size_hint_x=None, width=200, on_press=self.lock)
		
		#'#8e9e93'
		
		# initialize containers		
		# Head row:
		anchor_head = AnchorLayout(anchor_x='center')
		anchor_head.add_widget(lblHead)
		
		anchor_btn = AnchorLayout(anchor_x='right')
		anchor_btn.add_widget(btnUnlock)
		
		anchor_btn_lock = AnchorLayout(anchor_x='left')
		anchor_btn_lock.add_widget(btnLock)
		
		float_btn = FloatLayout()
		float_btn.add_widget(anchor_btn)
		float_btn.add_widget(anchor_btn_lock)
		
		boxHead = BoxLayout(orientation='vertical', size_hint_y=None, height=400)
		boxHead.add_widget(anchor_head)
		boxHead.add_widget(self.txtServer)
		boxHead.add_widget(self.txtSecret)
		boxHead.add_widget(float_btn)
		# Main Box
		box = BoxLayout(orientation='vertical')
		box.add_widget(boxHead)
		#s = Scatter(do_rotation=False, do_scale=False, do_translation_x=False)
		#s.add_widget(self.lblResult)
		f = FloatLayout()
		f.add_widget(self.lblResult)
		box.add_widget(f)
		return box
		
	def resetResult(self, event):
		self.lblResult.text = ''
		
	def doAction(self, action):
		if is_android:			
			vibrator.vibrate(0.1)
		client.server = self.txtServer.text
		self.lblResult.text = action(self.txtSecret.text.encode('ASCII'))
		Clock.schedule_once(self.resetResult, 10)
	
	def unlock(self, event):
		self.doAction(client.unlock)
		
	def lock(self, event):
		self.doAction(client.lock)
		

if __name__ == '__main__':		
	app = LockI()
	app.run()
