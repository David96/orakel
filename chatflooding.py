# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

from module import Module, MUC
from time import time
from threading import Timer

class ChatFlooding(Module):
	def __init__(self, maxlonglines, longlperiod, maxshortlines, \
			shortlperiod, shortlmaxchars, **keywords):
		super(ChatFlooding, self).__init__([MUC], name=__name__, **keywords)
		self.maxlonglines = maxlonglines
		self.longlperiod = longlperiod
		self.maxshortlines = maxshortlines
		self.shortlperiod = shortlperiod
		self.shortlmaxchars = shortlmaxchars
		self.storage = {}
		self.muted = []

	def muc_msg(self, msg, nick, **keywords):
		try:
			self.storage[nick]
		except:
			self.storage[nick] = {}
			self.storage[nick]['shortlines'] = []
			self.storage[nick]['longlines'] = []
		curtime = time()
		shortmessage = len(msg) <= self.shortlmaxchars
		
		times = self.storage[nick]['shortlines' if shortmessage\
						else 'longlines']
		times.append(curtime)

		diff = curtime - times[0]
		lines = len(times)
		period = self.shortlperiod if shortmessage \
				else self.longlperiod
		maxlines = self.maxshortlines if shortmessage \
				else self.maxlonglines
		if diff <= period and lines > maxlines:
			self.mute(nick)
			self.storage.pop(nick)

		while curtime - times[0] > period:
			times.pop(0)

	def mute(self, nick):
		self.send_muc(nick + ', you fucked up!')
		if not nick in self.muted:
			self.muted += [ nick ]
		self.send_cfg(key="muted", value=self.muted)
		self.set_role(nick, 'visitor')
		t = Timer(30.0, self.unmute, [nick])
		t.start()

	def unmute(self, nick):
		self.send_muc('Unmuting ' + nick)
		if not nick in self.muted:
			return
		index = self.muted.index(nick)
		del self.muted[index]
		self.send_cfg(key="muted", value=self.muted)
		self.set_role(nick, 'participant')
