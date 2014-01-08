#!/usr/bin/python
# Author kaushik gandhi
# email kaushikfrnd@gmail.com
import sys, traceback
import MySQLdb
import config
import json
import urllib2
from xml.dom import minidom
import simplejson as json
#----------------------- Class for hacker news integration ----------------------------

class HN_Integration(object):
    """This class is to scrape the whole HN posts and its user base """
    def __init__(self):
        try :
            self.db = MySQLdb.connect(config.db_config['SERVER'], # your host, usually localhost
                     config.db_config['USERNAME'], # your username
                      config.db_config['PASSWORD'], # your password
                      config.db_config['NAME']) # name of the data base
            self.cursor=self.db.cursor()
        except:
            print "Database connection error"
    #----------------------------detructor------------------------------
    def __del__(self):
          self.db.close()

#----------------------------------------get front page news------------------------------------
    def get_news(self):
      while True:
        try :
        #print 'starting' , config.appspot_url+'news'
          news_json=json.load(urllib2.urlopen(config.news_url))
          return news_json["results"]
          break
        except:
          print "exception in feeding posts"
          traceback.print_exc(file=sys.stdout)
#-----------------------------------------get comments------------------------------------------------

    def flatten_comments(self,node, acc = []):
      acc += [node['items']]
      if 'children' in node:
        for child in node['children']:
            self.flatten_comments(child, acc)

    def get_comments(self,post_id):
      while True:
        try :
        #print 'starting' , config.appspot_url+'news'
          news_json=json.load(urllib2.urlopen(config.comments_url+post_id))
          # print news_json
          return news_json["results"]
          break
        except:
          print "exception in feeding posts"
          traceback.print_exc(file=sys.stdout)

    def feed_comments(self,post_id):
      comments=self.get_comments(post_id)
      for comment in comments:
        try:
          self.cursor.execute('''INSERT into COMMENTS (id ,discussion_id ,discussion_sigid ,parent_id ,username,comment_text,comment_time,karma_points ) 
            values (%s,%s,%s,%s,%s,%s,%s,%s)''',
            (comment['item']['_id'],comment['item']['discussion']['id'],comment['item']['discussion']['sigid'],comment['item']['parent_id'],comment['item']['username'],comment['item']['text'],comment['item']['create_ts'],comment['item']['points']))
          self.db.commit()
          self.feed_user(comment['item']['username'])

        #print "feeded user" , user_id
        except:
          print "exception caught"
          traceback.print_exc(file=sys.stdout)

#------------------------------------------------feed user in database------------------------------------

    def feed_user(self,user_id) :
      try:
       user = self.get_user(user_id) 
       self.cursor.execute('''INSERT into USERINFO (id ,karma_points ,created_utc ,username ,flag,about ) 
          values (%s,%s,%s,%s,%s,%s)''',
         (user['_id'],user['karma'],user['create_ts'],user['username'],"false",user['about']))
       self.db.commit()
      #print "feeded user" , user_id
      except:
        print "exception caught"
        #traceback.print_exc(file=sys.stdout)

    def get_user(self,user_id):
      try:
        user_details=json.load(urllib2.urlopen(config.user_details_url+user_id))
        return user_details
      except:
        print 'exception in fetching user'
#----------------------------------------------feed posts in database------------------------------------------
    def feed_posts(self):
      try:
        posts=self.get_news()
        for post in posts:
          self.cursor.execute('''INSERT into POSTS (id,title,permalink,karma_points,url,author,self_text,published_time,num_comments)
              values (%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(post['item']['_id'],post['item']['title'],'https://news.ycombinator.com/item?id='+str(post['item']['id']),post['item']['points'],post['item']['url'],post['item']['username'],post['item']['text'],post['item']['create_ts'],post['item']['num_comments']))
          self.db.commit()
          self.feed_user(post['item']['username'])
          self.feed_comments(post['item']['_id'])
      except:
        print 'exception occurred'
        traceback.print_exc(file=sys.stdout)

#---------------------------------------------feed users,comments,posts in database starting from posts-----------------------------------------------
    def get_submitted(self,username):
      try:
        user_posts=json.load(urllib2.urlopen(config.user_posts_url+username))
        print user_posts
        return user_posts["results"]
      except:
        print 'exception in fetching user'
        traceback.print_exc(file=sys.stdout)


    def feed_by_user(self) :
     while True:
        try :
         rows_count=self.cursor.execute('''SELECT username from USERINFO WHERE flag=%s''',('false'))
         if rows_count > 0:
            results = self.cursor.fetchall()
         else :
           break
         for user_name in results:
           #print user_name[0] , 'in progress'
           posts = self.get_submitted(user_name[0])
           self.cursor.execute('''UPDATE USERINFO SET flag=%s
              WHERE username=%s''',('true',user_name[0]))
           self.db.commit()
           #print posts
           for post in posts :
              self.cursor.execute('''INSERT into POSTS (id,title,permalink,karma_points,url,author,self_text,published_time,num_comments)
              values (%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(post['item']['_id'],post['item']['title'],'https://news.ycombinator.com/item?id='+str(post['item']['id']),post['item']['points'],post['item']['url'],post['item']['username'],post['item']['text'],post['item']['create_ts'],post['item']['num_comments']))
              self.db.commit()
              
              self.feed_comments(post['item']['_id'])
              self.feed_user(post['item']['username'])
        
        except:
          print "exception caught" 
          traceback.print_exc(file=sys.stdout)

#---------------------------------------------------------parse dom ---------------------------
    def parse_element(self,element):
      dict_data = dict()
      if element.nodeType == element.TEXT_NODE:
        dict_data['data'] = element.data
      if element.nodeType not in [element.TEXT_NODE, element.DOCUMENT_NODE, 
                                element.DOCUMENT_TYPE_NODE]:
        for item in element.attributes.items():
            dict_data[item[0]] = item[1]
      if element.nodeType not in [element.TEXT_NODE, element.DOCUMENT_TYPE_NODE]:
        for child in element.childNodes:
            child_name, child_dict = self.parse_element(child)
            if child_name in dict_data:
                try:
                    dict_data[child_name].append(child_dict)
                except AttributeError:
                    dict_data[child_name] = [dict_data[child_name], child_dict]
            else:
                dict_data[child_name] = child_dict 
      return element.nodeName, dict_data

    def hn_front_page(self):
      dom = minidom.parse(urllib2.urlopen('https://www.hnsearch.com/rss'))
      news_json= json.dumps(self.parse_element(dom))
      parsed_json = json.loads(news_json)
      posts =parsed_json[1]['rss']['channel']['item']
      for post in posts:
          try:
            self.cursor.execute('''INSERT into POSTS (id,title,permalink,karma_points,url,author,published_time,num_comments)
              values (%s,%s,%s,%s,%s,%s,%s,%s)''',(post['hnsearch_id']['#text']['data'],post['title']['#text']['data'],post['comments']['#text']['data'],post['points']['#text']['data'],post['link']['#text']['data'],post['username']['#text']['data'],post['create_ts']['#text']['data'],post['num_comments']['#text']['data']))
            self.db.commit()
            self.feed_user(post['username']['#text']['data'])
            self.feed_comments(post['hnsearch_id']['#text']['data'])
          except:
            print 'exception occurred'
          # self.feed_user(post['item']['username'])
          # self.feed_comments(post['item']['_id']

      
#-------------------------------------End---------------------------------------------------



    
    
