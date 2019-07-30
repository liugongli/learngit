import itchat
from itchat.content import TEXT


@itchat.msg_register(TEXT, isFriendChat=True, isGroupChat=True, isMpChat=True)
def simple_reply(msg):
    return 'I received: %s' % msg.text


itchat.auto_login()
itchat.run()
