#! /usr/bin/python

#create table or open it
#Author : Kaushik Gandhi 
#Author Email : kaushikfrnd@gmail.com
import config
import MySQLdb,sys,traceback

def create_POSTS_table():
   
     try :
        db = MySQLdb.connect(config.db_config['SERVER'], # your host, usually localhost
                      config.db_config['USERNAME'], # your username
                      config.db_config['PASSWORD'], # your password
                      config.db_config['NAME'])
        cursor = db.cursor()
        #create table or open it
        print "Table POSTS created" 
        sql = """CREATE TABLE POSTS( 
        id varchar(20) NOT NULL,
        permalink varchar(200),
        title varchar(100),
        self_text varchar(2000),
        published_time varchar(20),
        num_comments INT,
        comments_link varchar(100),
        karma_points INT,
        url varchar(150),
        author varchar(50)
        )"""
    
        cursor.execute(sql)
        db.close()
     except MySQLdb.Error:
            traceback.print_exc(file=sys.stdout)
#------------------------------------------------user table for HN_integration ------------------------------

def user_db():
   
     try :
        db = MySQLdb.connect(config.db_config['SERVER'], # your host, usually localhost
                      config.db_config['USERNAME'], # your username
                      config.db_config['PASSWORD'], # your password
                      config.db_config['NAME'])
        cursor = db.cursor()
        #create table or open it
        print "Table userInfo created" 
        sql = """CREATE TABLE USERINFO ( 
        	id varchar(20),
        karma_points INT,
        	created_utc varchar(20),
          username varchar(100),
          about text,
          flag varchar(8),
        	PRIMARY KEY (id)
            )"""
        cursor.execute(sql)
        db.close()
     except MySQLdb.Error:
        traceback.print_exc(file=sys.stdout)
#------------------------------------------------comments table---------------------------

def create_comments_table():
   
     try :
        db = MySQLdb.connect(config.db_config['SERVER'], # your host, usually localhost
                      config.db_config['USERNAME'], # your username
                      config.db_config['PASSWORD'], # your password
                      config.db_config['NAME'])
        cursor = db.cursor()
        #create table or open it
        print "Table comments created" 
        sql = """CREATE TABLE COMMENTS ( 
        	id varchar(20) ,
        	discussion_id varchar(20),
        	discussion_sigid varchar(20),
            parent_id varchar(20),
        	username varchar(20),
        	comment_text varchar(400),
        	comment_time varchar(20),
          	karma_points INT,
          PRIMARY KEY (id)
            )"""
        cursor.execute(sql)
        db.close()
     except MySQLdb.Error:
        traceback.print_exc(file=sys.stdout)

create_POSTS_table()
user_db()
create_comments_table()