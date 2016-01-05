#coding=utf-8
import hashlib
import json
import time
import requests

UMENGPUSH_URL = 'http://msg.umeng.com/api/send'
my_app_key = 'myappkey'
my_app_master_secret = 'myappmastersecret'

class UmengPush():
	app_key = ""
	app_master_secret = ""
	start_time = ""
	expire_time = ""
	max_send_num = ""
	out_biz_no = ""
	production_mode = "true"
	description = ""
	thirdpartyid = ""
	is_setPolicy = False

	def md5(self,s):
		m = hashlib.md5(s)
		return m.hexdigest()

	def setPolicy(self, start_time="", expire_time="", max_send_num="", out_biz_no=""):#"YYYY-MM-DD HH:mm:ss"
		self.start_time = start_time
		self.expire_time = expire_time
		self.max_send_num = max_send_num
		self.out_biz_no = out_biz_no
		self.is_setPolicy = True

	def createPolicyDict(self):
		re = {}
		for each in ['start_time', 'expire_time', 'max_send_num', 'out_biz_no']:
			if getattr(self, each):
				re[each] = getattr(self, each)
		return re

	def setMode(self, test=False):
		self.production_mode = 'true' if not test else 'false'

	def setDescription(self, description):
		self.description = description
	def setThirdpartyId(self, id):
		self.thirdpartyid = id


	def getUrl(self, params):
		app_master_secret = self.app_master_secret

		method = 'POST'
		url = UMENGPUSH_URL

		post_body = json.dumps(params)
		sign = self.md5('%s%s%s%s' % (method,url,post_body,app_master_secret))
		whole_url = '%s?sign=%s' % (url, sign)
		return whole_url


	def sendMessage(self, ummessage, device_tokens, filter=None):
		params = {'appkey': self.app_key, 'timestamp': '%s' % int(time.time())}
		if len(device_tokens) > 1:
			params['type'] = 'listcast'
		elif len(device_tokens) == 1:
			params['type'] = 'unicast'
		else:
			params['type'] = 'broadcast'
		if device_tokens:
			params['device_tokens'] = ','.join(device_tokens)
		if filter:
			params['filter'] = filter
		params['payload'] = ummessage.getParams()
		if self.is_setPolicy:
			params['policy'] = self.createPolicyDict()
		params['production_mode'] = self.production_mode
		if self.description:
			params['description'] = self.description
		if self.thirdpartyid:
			params['thirdparty_id'] = self.thirdpartyid
		url = self.getUrl(params)
		try:
			re = requests.post(url, data=json.dumps(params)).json()
		except Exception as e:
			return e
		return re


	def __init__(self, app_key, app_master_secret):
		self.app_key = app_key
		self.app_master_secret = app_master_secret


UNKNOW = 0
UNICAST = 1
LISTCAST = 2
FILECAST = 3
BROADCAST = 4
GROUPCAST = 5

class UMMessageBody():

	class OPEN_ACTION():
		GO_APP = 'go_app'
		GO_URL = 'go_url'
		GO_ACTIVITY = 'go_activity'
		GO_CUSTOM = 'go_custom'

	title = ''
	text = ''
	ticker = ''
	icon = ''
	largeIcon = ''
	img = ''

	sound = ''
	builder_id = ''
	play_vibrate = 'true'
	play_lights = 'true'
	play_sound = 'true'

	after_open = ''
	url = ''
	activity = ''
	custom = ''

	@classmethod
	def soundParams(obj):
		return ['sound', 'builder_id', 'play_vibrate', 'play_lights', 'play_sound',]

	def setOpenAction(self, type, param):
		self.after_open = type
		if type == self.OPEN_ACTION.GO_URL:
			self.url = param
		elif type == self.OPEN_ACTION.GO_ACTIVITY:
			self.activity = param
		elif type == self.OPEN_ACTION.GO_CUSTOM:
			self.customs = param

	def getParams(self):
		body = {}
		for each in ['title', 'text', 'ticker', 'icon', 'largeIcon', 'img', 'sound', 'builder_id', 'play_vibrate',
		             'play_lights', 'play_sound', 'after_open', 'url', 'activity', 'custom']:
			if getattr(self,each):
				body[each] = getattr(self,each)
		return body


class UmengPushMessage():

	class TYPE():
		NOTIFY = 'notification'
		MESSAGE = 'message'

	display_type = ""
	body = UMMessageBody()

	is_set_title = False

	def __init__(self, type):
		self.display_type = type

	def setMessageCustom(self, text):
		self.body.custom = text
	def setNotifyTitle(self, title, text, ticker):
		if text and ticker and title:
			self.body.text = text
			self.body.title = title
			self.body.ticker = ticker
			self.is_set_title = True
		else:
			raise Exception("setNotifyTitle params must is not empty")
	def setNotifySound(self, **kwargs):
		for each in kwargs:
			if each in self.body.soundParams():
				setattr(self.body, each, kwargs[each])

	def setNotifyAfterOpen(self, type, params):
		self.body.setOpenAction(type, params)


	def setExtra(self, **kwargs):
		self.extra = kwargs

	def getParams(self):
		message = {'display_type': self.display_type, 'body': {}}
		if self.display_type == self.TYPE.NOTIFY:
			if not self.is_set_title:
				raise Exception("setNotifyTitle params must is not empty")
			message['body'] = self.body.getParams()
		elif self.display_type == self.TYPE.MESSAGE:
			message['body'] = {'custom': self.body.custom}
		message['extra'] = self.extra
		return message


def test():
	upm = UmengPushMessage(type=UmengPushMessage.TYPE.NOTIFY)
	upm.setNotifyTitle(title='testtitle', text='testtext', ticker='testticker')
	upm.setNotifyAfterOpen(UMMessageBody.OPEN_ACTION.GO_APP,params='')
	upm.setExtra(id='1',type='2')
	up = UmengPush(app_key=my_app_key, app_master_secret=my_app_master_secret)
	return up.sendMessage(upm, ['fdsafdsafds','fdsafdsafds'])


if __name__ == '__main__':
	print(test())
