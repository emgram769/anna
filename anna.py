from time import sleep
from livechanapi import *
import wikipedia
import duckduckgo
import re
import sys
import wolframalpha
import random
from datetime import datetime
import config

if (len(sys.argv) < 2):
    print "Usage: python anna.py [channel]"
    exit()
channel = sys.argv[1]
wolfram = wolframalpha.Client(config.wolframAPI)

# globals
users = {}

def process_chat(*args):
    img = "anna" + str(random.randint(6,8)) + ".png"
    try:
        ident = args[0]["identifier"]
        global users
        if ident in users:
            interval = (datetime.now() - users[ident]).total_seconds()
            if interval < 7:
                return
        message = args[0]["body"]
        name = args[0]["name"]
        count = str(args[0]["count"])
        if "trip" in args[0]:
            trip = args[0]["trip"]
        else:
            trip = ""
        if trip == "!!.w5vzYxkv6":
            return
        # default message
        out_message = ""

        # helpful
        t = re.compile('[wW]hat (is|are) (.+)\?').match(message)
        if (t):
            try:
                res = wolfram.query(t.group(2))
                out_message = next(res.results).text
                #out_message = wikipedia.summary(t.group(1), sentences=1)
            except Exception as e:
                print res.__dict__
                print out_message
                out_message = ""
                print "wolfram error",e

        # wolfram
        t = re.compile('\.wa (.+)').match(message)
        if (t):
            try:
                res = wolfram.query(t.group(1))
                out_message = next(res.results).text
            except Exception as e:
                out_message = "That query was ambiguous, Onii-chan"
                img = "anna" + str(random.randint(1,5)) + ".png"
                print e
         
        # wiki
        t = re.compile('\.wiki(pedia)? (.+)').match(message)
        if (t):
            try:
                out_message = wikipedia.summary(t.group(2), sentences=3)
            except Exception as e:
                out_message = "That query was ambiguous, Onii-chan"
                img = "anna" + str(random.randint(1,5)) + ".png"
                print e
     
        # google
        t = re.compile('\.google( (.+))?').match(message)
        if (t):
            try:
                r = duckduckgo.query(t.group(2))
                for i in xrange(len(r.related) if len(r.related) < 4 else 3):
                    result = r.related[i]
                    out_message += '\n'+ result.text + '\n'
                    out_message += '[i]' + result.url + ' [/i]\n'
            except Exception as e:
                out_message = "That query was ambiguous, Onii-chan"
                img = "anna" + str(random.randint(1,5)) + ".png"
                print e

        # random
        t = re.compile('\.random( (.+))?').match(message)
        if (t):
            try:
                if t.group(1) and t.group(2).isdigit():
                    out_message += str(random.randint(0, int(t.group(2))))
                else:
                    out_message += str(random.randint(0, 100))
                    if int(out_message)%10 == int(out_message)/10:
                        out_message += " (you got doubles :3)"
            except Exception as e:
                out_message = "That was ambiguous, Onii-chan"
                img = "anna" + str(random.randint(1,5)) + ".png"
                print e

        #out_message = (">>"+str(args[0]["count"])+
        #"\n\ryou said my name, Onii-chan?")

        if out_message != "":
            users[ident] = datetime.now()
            if (count):
                out_message = ">>"+count+"\n"+out_message#.encode('ascii', 'ignore')
            post_chat(out_message, channel,
                    name="anna", trip=config.annaTrip,
                    convo=args[0]["convo"], file=img)
    except Exception as e:
        print e

login(callback=process_chat)
join_chat(channel)

while 1:
    sleep(10)
