import poster
import urllib2
import cookielib
import re
from socketIO_client import SocketIO
import json
import thread
import config

cookies = cookielib.LWPCookieJar()

handlers = [
    urllib2.HTTPHandler(),
    urllib2.HTTPSHandler(),
    urllib2.HTTPCookieProcessor(cookies)
    ]
#opener = urllib2.build_opener(*handlers)
# Register the streaming http handlers with urllib2
opener = poster.streaminghttp.register_openers()
for handler in handlers:
    opener.add_handler(handler)

curr_chat_room = None
socketIO = None
mesg_queue = []
def fetch(uri):
    req = urllib2.Request(uri)
    return opener.open(req)

def post(uri, params):
    datagen, headers = poster.encode.multipart_encode(params)
    req = urllib2.Request(uri, datagen, headers)
    return opener.open(req)

def get_password():
    for cookie in cookies:
        if cookie.name == "password_livechan":
            cookie.value = config.nolimitCookie
            return cookie.value
    return ""

def post_chat(body, chat, name="Anonymous", convo="General", trip="", file="" ):
    post_params = []

    name = name if trip == "" else name+"##"+trip
    post_params.append(poster.encode.MultipartParam("name", name))
    post_params.append(poster.encode.MultipartParam("trip", trip))
    post_params.append(poster.encode.MultipartParam("body", body))
    post_params.append(poster.encode.MultipartParam("convo", convo))
    post_params.append(poster.encode.MultipartParam("chat", chat))

    if not file == "":
        post_params.append(poster.encode.MultipartParam.from_file("image", file))

    datagen, headers = poster.encode.multipart_encode(post_params)
    uri = 'https://livechan.net/chat/'+chat
    req = urllib2.Request(uri, datagen, headers)
    return opener.open(req)
    #return post('https://livechan.net/chat/'+chat, post_params)


def join_chat(chat_room):
    global curr_chat_room
    global socketIO
    if (curr_chat_room != None):
        socketIO.emit('unsubscribe', curr_chat_room);
    socketIO.emit('subscribe', chat_room);

def display_chat(chat_obj):
    print chat_obj["name"]
    print chat_obj["body"]
    print

def get_data(chat):
    data_response = fetch('https://livechan.net/data/'+chat)
    json_data = json.loads(data_response.read())
    for i in json_data[::-1]:
        display_chat(i)

def main_chat(chat_room):
    chat_body = raw_input("> ")
    if (chat_body == "/quit"):
        return True # break
    mainresp = post_chat(chat_body, chat_room)
    return False
    #print mainresp.read()

def on_chat(*args):
    if (args[0]["name"] == "IRCBot"):
        return
    msg = args[0]["name"]+"~ "
    if ("image" in args[0]):
        filename = "https://livechan.net/tmp/uploads/"+re.compile('[\w\-\.]*$').search(args[0]["image"]).group(0)
        msg += "file: "+filename+" "
    msg += (" ".join(args[0]["body"].splitlines()))
    livechanBot.sendMsg(channel, msg)

def on_user_count(*args):
    print args[0], "users online"
    print

def on_request_location(*args):
    global chat_room
    socketIO.emit('subscribe', curr_chat_room);

def login(callback=on_chat):
    #image_response = fetch('https://livechan.net/captcha.jpg')
    #image_data = image_response.read()

    #with open('captcha.jpg', 'w') as f:
    #    f.write(image_data)
    #os.system("open captcha.jpg")

    #digits = int(raw_input("enter the captcha: "))
    #post_params = {}
    #post_params["digits"] = digits
    #login_response = post('https://livechan.net/login', post_params)
    #login_html = login_response.read()

    cookie = cookielib.Cookie(version=0, name='password_livechan', value=config.nolimitCookie, port=None, port_specified=False, domain='livechan.net',
            domain_specified=False, domain_initial_dot=False,
            path='/', path_specified=True, secure=False, expires=None,
            discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
    cookies.set_cookie(cookie)
    livechan_pass = get_password()
    if livechan_pass == "":
        print "wrong password"
        login()

    global socketIO
    socketIO = SocketIO('https://livechan.net',
        cookies={'password_livechan': livechan_pass})
    socketIO.on('chat', callback)
    socketIO.on('request_location', on_request_location)
    
    thread.start_new_thread ( socketIO.wait, () )
 
