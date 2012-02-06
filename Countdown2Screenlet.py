import screenlets
from screenlets.options import StringOption, FileOption
import cairo
import gtk
import pango
import time
from os import system
import gobject
import subprocess
import sys

class CountdownScreenlet(screenlets.Screenlet):
	
	# default meta-info for Screenlets
	__name__ = 'Countdown2Screenlet'
	__version__ = '1.0'
	__author__ = 'Patrik Kullman, Suhail Sherif'
	__desc__ = 'Display time left to a list of dates and times'

	# internals
	__timeout = None

	# editable options and defaults
	__update_interval = 1 # every second
	eventfile = sys.path[0]+"/eventfiles/countdownfile"
	alarm = sys.path[0]+"/sounds/alarm"
	eventlist=[]
	eventindex=0
	eventshown=0
	try:
		fin=file(eventfile,'r')
		linein=fin.readline()
		while(linein!=""):
			temp=linein.split(None, 2)
			temptime=temp[0]+" "+temp[1]
			itemptime = time.mktime(time.strptime(temptime, "%Y-%m-%d %H:%M:%S"))
			eventlist.append([itemptime, temp[2]])
			linein=fin.readline()
		eventlist.sort()
		for event in eventlist[:]:
			if time.time() > event[0]:
				eventlist.remove(event)
		fin.close()
	except:
		eventlist=[]
		eventindex=0
		eventlist.append([-1,"N/A"])					

	# constructor
	def __init__(self, **keyword_args):
		# call super
		screenlets.Screenlet.__init__(self, width=300, height=100, **keyword_args)
		# set themeNew Year
		self.theme_name = "default"
		self.add_menuitem("refresh", "Refresh eventlist", None)		
		self.add_menuitem("view", "Edit eventlist", None)
		# add default menu items
		self.add_default_menuitems()
		# add option groups
		self.add_options_group('Countdown', 'Countdown settings')
		self.add_option(FileOption('Countdown', 'eventfile', self.eventfile, 'Event file', 'Select event file'))
		self.add_option(FileOption('Alarm', 'alarm', self.alarm, 'Alarm to go off', 'Select alarm (wav format)'))
		self.__timeout = gobject.timeout_add(self.__update_interval * 1000, self.update)

	def __setattr__(self, name, value):
		# call Screenlet.__setattr__ in baseclass (ESSENTIAL!!!!)
		screenlets.Screenlet.__setattr__(self, name, value)
		# redraw the canvas when server-info is changed since a server host/ip addition/removal will change the size of the screenlet

	def update(self):
		gobject.idle_add(self.redraw_canvas)
		return True

	def on_draw(self, ctx):
		self.__timeleft = self.get_time_left(self.eventlist[self.eventindex][0])
		# scaling above 500% is very slow and might brake it (why?)
		if self.scale > 5:
			self.scale = 5
		# if theme is loaded
		if self.theme:
			# find out how many servers that are configured and force a update_shape() when they're changed from the last draw.
			# apparently the settings doesn't get loaded until the widget is first displayed, and no update_shape is performed at
			# that point
			# make sure that the background covers all the icons
			ctx.save()
			ctx.scale(self.scale * 1.5, self.scale)
			ctx.translate(0, 0)
			self.theme.render(ctx, 'background')
			ctx.restore()

			ctx.save()
			ctx.scale(self.scale, self.scale)
			self.draw_text(ctx, "Time left to: " + self.eventlist[self.eventindex][1], 10, 10, 12)
			self.draw_text(ctx, self.__timeleft, 10, 45, 18)
			ctx.restore()

			ctx.save()
			ctx.scale(self.scale * 1.5, self.scale)
			ctx.translate(0, 0)
			self.theme.render(ctx, 'glass')
			ctx.restore()
	
	def on_scroll_up (self):
		"""Called when mousewheel is scrolled up (button4)."""
		if self.eventshown != 0:
			self.eventindex=self.eventshown-1
			self.update()
		pass
	
	def on_scroll_down (self):
		"""Called when mousewheel is scrolled up (button4)."""
		if self.eventshown < len(self.eventlist)-1:
			self.eventindex=self.eventshown+1
			self.update()
		pass

	def on_menuitem_select (self, id):
			"""Called when a menuitem is selected."""
			if id == "refresh":
				self.eventlist=[]
				self.eventindex=0
				self.eventshown=0
				try:
					fin=file(self.eventfile,'r')
					linein=fin.readline()
					while(linein!=""):
						if(linein.strip()!=""):
							temp=linein.split(None, 2)
							temptime=temp[0]+" "+temp[1]
							itemptime = time.mktime(time.strptime(temptime, "%Y-%m-%d %H:%M:%S"))
							self.eventlist.append([itemptime, temp[2]])
						linein=fin.readline()
					self.eventlist.sort()
					for event in self.eventlist[:]:
						if time.time() > event[0]:
							self.eventlist.remove(event)
					self.fin.close()
				except:
					self.eventlist=[]
					self.eventindex=0
					self.eventlist.append([-1,"N/A"])					
			if id == "view":
				subprocess.call(['gnome-open', self.eventfile])
			pass

	def on_draw_shape(self, ctx):
		if self.theme:
			self.on_draw(ctx)

	def draw_text(self, ctx, value, x, y, size):
		# stolen from CalcScreenlet ;)
		ctx.save()
		ctx.translate(x, y)
		p_layout = ctx.create_layout()
		p_fdesc = pango.FontDescription()
		p_fdesc.set_family_static("Sans")
		p_fdesc.set_size(size * pango.SCALE)
		p_layout.set_font_description(p_fdesc)
		p_layout.set_width(280 * pango.SCALE)
		p_layout.set_alignment(pango.ALIGN_CENTER)
		p_layout.set_markup(value)
		ctx.set_source_rgba(1, 1, 1, 0.8)
		ctx.show_layout(p_layout)
		p_layout.set_alignment(pango.ALIGN_LEFT)
		ctx.restore()

	def get_time_left(self, date):
		if date < 0:
			return "Bad File"
		now = time.time()
		seconds_left = date - now
		self.eventshown=self.eventindex
		if (seconds_left > 0):
			days_left = int(seconds_left / 60 / 60 / 24)
			seconds_left = seconds_left - (days_left * 24 * 60 * 60)
			hours_left = int(seconds_left / 60 / 60)
			seconds_left = seconds_left - (hours_left * 60 * 60)
			minutes_left = int(seconds_left / 60)
			seconds_left = int(seconds_left - (minutes_left * 60))
			return str(days_left) + "d " + str(hours_left) + "h " + str(minutes_left) + "m " + str(seconds_left) + "s"
		else:
			subprocess.call(['aplay',self.alarm])
			subprocess.call(['espeak',self.eventlist[0][1]])
			subprocess.call(['aplay',self.alarm])
			self.eventlist.remove([self.eventlist[0][0],self.eventlist[0][1]])
			return self.eventlist[0][1] + "!"

# If the program is run directly or passed as an argument to the python
# interpreter then create a Screenlet instance and show it
if __name__ == "__main__":
	import screenlets.session
	screenlets.session.create_session(CountdownScreenlet)
