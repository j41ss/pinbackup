#!usr/bin/python
# -*- coding: utf-8 -*-
import pycurl
from StringIO import StringIO
from urlparse import urlparse
import json
import os
import colorama
import hashlib
import threading
import sys
import random
import string

class PAccess:
    apihost = 'https://api.pinterest.com/v1/'
    def __init__(self, token):
        self.token = token
        self.__raw_request = None
    def __pycurl_require( method='GET', fields='', url=False ):
      fields = fields
      def __pycurl_internal( func ):
        def wrap( self, *args, **kwargs):
            fld= ''
            if fields != '':
             fld = '&fields=' + fields
            if not url:
             url_partial = func( self, *args, **kwargs)
             url_ende = self.__class__.apihost + \
                             url_partial + 'access_token=' + self.token + fld
            else:
             url_ende = func( self, *args, **kwargs)

            buff = StringIO()
            attrs = { 'URL': url_ende,
                      'HEADER': False,
                      'HTTPGET': True,
                      'WRITEFUNCTION': buff.write,
                      'FOLLOWLOCATION': True,
                      'TIMEOUT': 10}
            conn = pycurl.Curl()
            [ conn.setopt( getattr( conn, key ),  val) for key,val in attrs.items() ]
            conn.perform()
            conn.close()
            return buff
        return wrap
      return __pycurl_internal

    @property
    def answer(self):
       dt = json.loads(self.__raw_request.getvalue())
       return dt

    @__pycurl_require('GET')
    def boards(self, *args, **kwargs):
      return 'me/boards/?'

    @__pycurl_require('GET')
    def user(self, *args, **kwargs):
      return 'me/?'

    @__pycurl_require('GET')
    def board(self, *args, **kwargs):
     return 'boards/{}/?'.format( args[0] )

    @__pycurl_require('GET','image')
    def pin(self, *args, **kwargs):
     return 'pins/{}/?'.format( args[0] )

    @__pycurl_require('GET',url=True)
    def wget_pic(self, *args, **kwargs):
     return args[0]

def color_output( color ):
     clr = getattr( colorama.Fore, color )
     def wrap( func ):
      def wrap1(*args,**kwargs):
       return "{c}{msg}{r}".format(
            c=clr, r=colorama.Fore.RESET,
             msg=func(*args,**kwargs) )
      return wrap1
     return wrap

class PBackup:

 def __init__(self):
   self.lpath = None
   self._apiobj = None
   self.location(os.environ['HOME'])

 @staticmethod
 @color_output('RED')
 def warn( msg ):
  return msg

 @staticmethod
 @color_output('GREEN')
 def easy( msg ):
  return msg

 @staticmethod
 @color_output('YELLOW')
 def info( msg ):
  return msg

 def location(self, base, loc='pinterest'):
     possible_path = base + os.sep + loc
     if not os.path.isdir( possible_path  ):
         print("Make directory {}".format(PBackup.warn(possible_path)))
         os.makedirs( possible_path )
     self.lpath = possible_path
     self._hashes = []
     for d, drs, fls in os.walk( self.lpath ):
        for i in fls:
         with open( d + os.sep + i) as wp:
             self._hashes.append(hashlib.sha256(wp.read()).hexdigest())

 def user_info(self):
  user = self._apiobj.user()
  buf = self.answ_parse(user)['data']
  self.username = buf['first_name']
  self.userid = urlparse(buf['url']).path.strip('/')

 def boards(self):
  boards = self._apiobj.boards()
  self._boards = self.answ_parse(boards)['data']

 def board_backup( self, *args, **kwargs ):
  name = args[0]
  rand_len = 10
  pins_all_from_boards = \
      self._apiobj.board(self.userid+'/'+ name +'/pins')
  pin_ids = [ i['id'] for i in
      self.answ_parse(pins_all_from_boards)['data'] ]
  if len(pin_ids):
    if len( args ) == 2:
     print("Backup board {}".format(self.info(args[1])))
    urls = dict()
    for i in pin_ids:
     single_pin = self._apiobj.pin( i )
     answ = self.answ_parse(single_pin)['data']
     urls[answ['id']] = answ['image']['original']['url']

    if urls:
     rand_str =  lambda x: "".join (
        [ random.SystemRandom().choice( string.ascii_lowercase + string.digits )  for x in range(x) ] )
     for i, j in urls.items():
      cont = self._apiobj.wget_pic(j)
      hash = hashlib.sha256( cont.getvalue() ).hexdigest()
      if not os.path.isdir( self.lpath + os.sep + args[1] ):
       os.makedirs( self.lpath + os.sep + args[1] )
      if hash not in self._hashes :
       with open(self.lpath + os.sep + args[1] + os.sep + i + rand_str(rand_len) + '.jpg' , 'w' ) as w:
         print('Save object {} from {}'.format(self.warn(i), self.info(args[1])))
         w.write( cont.getvalue() )

 def answ_parse(self, answ):
     enc_list = answ.getvalue() 
     if len( enc_list ) and isinstance(  enc_list[-1], dict) :
      enc_list =  [ { i:j.decode(sys.getfilesystemencoding() ) } for val in enc_list for i,j in val.items() ]
     return json.loads( enc_list )

 def dial(self):
  if not os.environ.get('PINTEREST_TOKEN'):
   print("Please insert enviroment variable PINTEREST_TOKEN")
   sys.exit(1)
  reload(sys)
  sys.setdefaultencoding(sys.getfilesystemencoding())
  token = os.environ['PINTEREST_TOKEN']
  self._token = token
  self._apiobj = PAccess( token )
  self.user_info()
  self.boards()
  user = self._apiobj.user()
  if self.username:
   print( "Hello, {}".format(self.easy(self.username.decode( sys.getfilesystemencoding()) )) )
  if self._boards:
   print("You have {} board:".format(len(self._boards) ))
  for i in self._boards:
   arg = os.path.basename( i['url'][0:-1] ).decode( sys.getfilesystemencoding() )
   task = threading.Thread(target=self.board_backup, name='thread_{}'.format(i['name']),
                           args=(arg, i['name']) )
   
   task.start()

 @property
 def answ(self):
     return self._apiobj.answer['data']

def main():
    a = PBackup()
    a.dial()
if __name__ == '__main__':
    main()
