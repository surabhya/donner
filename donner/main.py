#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os
import hashlib
import hmac
import re
import json
import urllib2
import random
import json,httplib
from string import letters
#from google.appengine.ext import db
import db
SECMES="du10A010F0Tny89810lkd4n5"
PARSE_API_KEY = "1yQIRpJR8lacwgyqfnW1DPHx7gB7TadGZ772VM83"
APP_KEY = "VAX09Xo9xpFdA78ppgVki2u5Fnzr0VQTnXrkftUz"
#joins the path of current direcotry with template
temp_dir=os.path.join(os.path.dirname(__file__),'templates')

#loads the file in jinja environment from temp_dir path
jinja_env=jinja2.Environment(loader = jinja2.FileSystemLoader(temp_dir),autoescape=True)
connection = httplib.HTTPSConnection('api.parse.com', 443)

def render_str(self,template,**params):
    t=jinja_env.get_template(template)
    return t.render(params)
def hash_str(s):            
    return hmac.new(SECMES,s).hexdigest()
def make_secure_val(s):
    return "%s|%s"%(s,hash_str(s))
def check_secure_val(h):
    s=h.split('|')[0]
    if(h==make_secure_val(s)):
        return s

class Handler(webapp2.RequestHandler):
    def write(self,*a,**kw):
        self.response.out.write(*a,**kw)
    def render_str(self, template, **params):
        params['user'] = self.user
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self,template,**kw):
        self.write(self.render_str(template,**kw))
    def set_secure_cookie(self,name,val):
        cookie_val=str(make_secure_val(val))
        self.response.headers.add_header('Set-Cookie','%s=%s; Path=/'%(name,cookie_val))
    def read_secure_cookie(self,name):
        cookie_val=self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)
    def login(self,user):
        self.set_secure_cookie('user_id',str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie','user_id=; Path=/')
    def check_match(self,booktitle,iswish):
        if iswish:
                return iswish,db.user_book.check_by_name(booktitle,False)
                
        else:
                return iswish,db.user_book.check_by_name(booktitle,True)
                
        
    def initialize(self,*a,**kw):
        #called by app engine framework for every page
        webapp2.RequestHandler.initialize(self,*a,**kw)
        uid=self.read_secure_cookie('user_id')
        #self.response.out.write(uid)
        self.user=uid and db.user_acc.by_id(int(uid)) #
def gen_rand():
    length=5
    return ''.join(random.choice(letters) for x in xrange(length))
def gen_hash_pw(name,pw,salt=None):
    if not salt:
        salt=gen_rand()
    hashp=hashlib.sha256(name+pw+salt).hexdigest()
    return '%s,%s'%(salt,hashp)
def valid_pw(name,password,h):
    salt=h.split(',')[0]
    return h==gen_hash_pw(name,password,salt)


class MainHandler(Handler):
    def get(self):
        user=""
        if self.user:
           user=self.user.username
        self.render("index.html", userperson=user)
    def post(self):
        error="The Username you provided already exist"

class org_signupHandler(Handler):
    def get(self):
        user = ""
        if self.user:
            user = self.user.username
            self.render("index.html", userperson = user)
        else:
            self.render("sign-up-org.html")
    def post(self):
        if self.org_person:
            self.redirect("/start")
        else:
            error="The Username you provided already exist"
            org_name = self.request,get("org_name")
            username= self.request.get("username")
            password = self.request.get("password")
            repass=self.request.get('repassword')
            email=self.request.get("email")
            catogery = self.request.get('catogery')
            Phone_Number= self.request.get('Phone_Number')
            if password != repass:
                    self.render('index.html', pass_message="Password do not match")
            else:
                params = urllib.urlencode(
                    {"loginname" : username,
                     "email" : email,
                     "name" : org_name,
                     "loginpassword" : password,    
                     "catogery" : catogery,
                     "phone" : Phone_Number,
                    }
                    )
                connection.connect()
                connection.request('GET', '/1/login?%s' % params, '',
                    {
                    'X-Parse-Application-Id' : APP_KEY,
                    'X-Parse-REST-API-Key' : PARSE_API_KEY,
                    'X-Parse-Revocable-Session': '1'
                    })
                result = json.loads(connection.getresponse().read())
                self.response.write(result)
            
class SignupHandler(Handler):
	def get(self):
		user = ""
		if self.user:
			user = self.user.username
			self.render("index.html", userperson = user)
		else:
			self.render("sign-up-user.html")
	def post(self):
		if self.user:
			self.redirect("/start")
		else:
			error="The Username you provided already exist"
			username= self.request.get("username")
	        password = self.request.get("password")
	        repass=self.request.get('repassword')
	        email=self.request.get("email")
	        first_name = self.request.get('first_name')
	        last_name = self.request.get('last_name')
	        if password != repass:
	                self.render('index.html', pass_message="Password do not match")
	        else:
	        	params = urllib.urlencode(
	        		{"User Name" : username,
	        		 "Email" : email,
	        		 "Password" : password,
	        		 "first_name" : first_name,
	        		 "last_name" : last_name,
	        		}
	        		)
	        	connection.connect()
	        	connection.request('GET', '/1/login?%s' % params, '',
	        		{
	        		'X-Parse-Application-Id' : APP_KEY,
	        		'X-Parse-REST-API-Key' : PARSE_API_KEY,
	        		'X-Parse-Revocable-Session': '1'
	        		})
	        	result = json.loads(connection.getresponse().read())
	        	self.response.write(result)
	            #p=db.user_acc.by_name(username)
	            # if p:
	            #     self.render("index.html",message=error)
	            # else: #
	            #     p=db.user_acc.register(username=username,password=password,email=email)
	            #     p.put()
	            #     self.set_secure_cookie('user_id',str(p.key().id()))
	            #     self.redirect('/start')

class UserInfoHandler(Handler):
	def post(self):
		pass
	def get(self):
        user_name = "Parasher Ghimire"
	    organizations_donated = ["Brease Awareness", "HIV awareness"]
		sectors = { 'Health' : 15,'Environment' : 35, 'Community Development' : 10 ,'Human Civil Rights' : 15, 'Research & Public Policy' : 20 ,'Religion' : 20 }
        sectors = json.dump(sectors);
		donated_over_months = [120, 130, 10, 13, 12, 12, 12 ,12 ,13, 14, 30, 14];
		self.render("user-info.html", user_name = user_name, organizations_donated = organizations_donated, sectors = sectors, donated_over_months = donated_over_months)
class LoginHandler(Handler):
	def get(self):
		self.render("")
	def post(self):
		if self.user:
			self.redirect("/start")
		else:
			usertype = self.request.get("utype")
			username=self.request.get("uname")
	        password=self.request.get("pass")
	        if usertype == "donor":
	        	u = db.user_acc.login(username, password)
	        elif usertype == "organization":
				params = urllib.urlencode({"username":username,"password": password})
				connection.connect()
				connection.request('GET', '/1/login?%s' % params, '', {
		   		"X-Parse-Application-Id": APP_KEY,
		   		"X-Parse-REST-API-Key": PARSE_API_KEY,
		   		"X-Parse-Revocable-Session": "1"
		 		})
				result = json.loads(connection.getresponse().read())
				print result
	            #self.login(u)
	            #self.redirect('/start')
	        else:
	            msg="Invalid Login Info"
	            self.redirect('/')
class UserPageHandler(Handler):
	def get(self):
		self.render("", username = self.user.username)
	def post(self):
		pass

class Logout(Handler):#handles user logout 
    def get(self):
        self.logout()
        self.redirect('/')
class books(Handler): #display user books
    def get(self):
        cursor=db.user_book.get_all(self.user.username)
        book_list=list(cursor)
        self.render("mybs.html",book_list=book_list, username=self.user.username)
class Repository(Handler):
    def get(self):
        search_query=self.request.get('query')
        if search_query:
                result=db.user_book.get_by_query(search_query)
                book_list=list(result)
        self.render("repo.html")
         
class Match(Handler):
    def get(self):
            if self.user:
                    match=db.user_match.get_all(self.user.username)
                    self.render("match.html",match=match)
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/sign-up-user',SignupHandler),
    ('/sign-up-org',org_signupHandler),
    ('/start',UserPageHandler),
    ('/user-info', UserInfoHandler),
    ('/logout',Logout),
	('/mbs',books),
    ('/match',Match),
], debug=True)
