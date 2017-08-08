# -*- coding: utf-8 -*-

# ############################
#
# Imports
#
# ############################

from translate import Translator
import threading
import hexchat
import os

# ############################
#
# Module name
#
# ############################

__module_name__ = "google translator"
__module_version__ = "1.1"
__module_description__ = "Translates from one language to others using Google Translate."
__module_author__ = "EpicJhon"

# ############################
#
# Globals
#
# ############################

Bold = '\002'
Color = '\003'
Hidden = '\010'
Underline = '\037'
NormalText = '\017'
ReverseColor = '\026'
Beep = '\007'
Italics = '\035'

default_from = 'en'
default_to = 'es'

AUTOUSER = {}
AUTOCHANNEL = {}


# ############################
#
# Persistence
#
# ############################

def save_config(filename, dic):
    config_dir = hexchat.get_info('configdir') + '/google_translator/'
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    f = open(config_dir + filename + '.db', 'w')
    f.write(str(dic))
    f.close()


def load_config(filename):
    config_dir = hexchat.get_info('configdir') + '/google_translator/'
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    f = open(config_dir + filename + '.db', 'r')
    dic = f.read()
    f.close()
    return eval(dic)


# ############################
#
# Translate function
#
# ############################

def translate(message, _from=default_from, to=default_to):
    if _from == '':
        _from = 'auto'
    t = Translator()
    return t.translate(message, from_lang=_from, to_lang=to)


# ############################
#
# Worker functions for thread
#
# ############################

def worker_hook_print_message(context, message, nick, _from=default_from, to=default_to):
    # translate message
    translation = translate(message, _from, to)
    context.prnt(Bold + nick + NormalText + Color + '08 ' + translation)


def worker_hook_tr(message, _from=default_from, to=default_to):
    # translate message
    translation = translate(message, _from, to)
    print(Bold + hexchat.get_info('nick') + NormalText + Color + '08 ' + translation)


# translate your message and send to server
def worker_hook_str(context, message, _from=default_from, to=default_to):
    # translate message
    final_text = translate(message, to, _from)
    # print and send translated message to server
    context.command('SAY ' + final_text)


# ############################
#
# Hook functions
#
# ############################

def hook_add_channel(word, word_eol, userdata):
    dest_lang = default_to
    src_lang = default_from

    if len(word) > 1:
        channel = word[1]
    else:
        channel = hexchat.get_info('channel')

    if len(word) > 2:
        dest_lang = word[2]

    if len(word) > 3:
        src_lang = word[3]

    AUTOCHANNEL[hexchat.get_info('network') + ' ' + channel.lower()] = (dest_lang, src_lang)
    save_config('google_tr_auto_channel', str(AUTOCHANNEL))
    hexchat.prnt("Added channel %s to the watch list." % channel)

    return hexchat.EAT_ALL


def hook_remove_channel(word, word_eol, userdata):
    if len(word) > 1:
        channel = hexchat.strip(word[1])
    else:
        channel = hexchat.get_info('channel')

    if AUTOCHANNEL.pop(hexchat.get_info('network') + ' ' + channel.lower(), None) is not None:
        save_config('google_tr_auto_channel', str(AUTOCHANNEL))
        hexchat.prnt('Channel ' + channel + ' has been removed from the watch list.')

    return hexchat.EAT_ALL


def hook_add_user(word, word_eol, userdata):
    if len(word) < 2:
        hexchat.prnt("You must specify a user.")
        return hexchat.EAT_ALL

    user = word[1]
    dest_lang = default_to
    src_lang = ''

    if len(word) > 2:
        dest_lang = word[2]

    if len(word) > 3:
        src_lang = word[3]

    AUTOUSER[hexchat.get_info('network') + ' ' + hexchat.get_info('channel') + ' ' + user.lower()] = (dest_lang, src_lang)
    save_config('google_tr_auto_user', str(AUTOUSER))
    hexchat.prnt("Added user %s to the watch list." % user)

    return hexchat.EAT_ALL


def hook_remove_user(word, word_eol, userdata):
    if len(word) < 2:
        hexchat.prnt("You must specify a user.")
        return hexchat.EAT_ALL

    user = hexchat.strip(word[1])

    if AUTOUSER.pop(hexchat.get_info('network') + ' ' + hexchat.get_info('channel') + ' ' + user.lower(), None) is not None:
        save_config('google_tr_auto_user', str(AUTOUSER))
        hexchat.prnt('User ' + user + ' has been removed from the watch list.')

    return hexchat.EAT_ALL


def hook_print_user_list(word, word_eol, userdata):
    hexchat.prnt("Auto translate users")
    for key, value in AUTOUSER.items():
        hexchat.prnt("\t" + key + ' => %s' % (value,))
    return hexchat.EAT_ALL


def hook_print_channel_list(word, word_eol, userdata):
    hexchat.prnt("Auto translate channels")
    for key, value in AUTOCHANNEL.items():
        hexchat.prnt("\t" + key + ' => %s' % (value,))
    return hexchat.EAT_ALL


def hook_tr(word, word_eol, userdata):
    _from = default_from
    to = default_to
    message = word_eol[1]
    threading.Thread(target=worker_hook_tr, args=(message, _from, to)).start()
    return hexchat.EAT_ALL


def hook_tra(word, word_eol, userdata):
    _from = word[1]
    to = word[2]
    message = word_eol[3]
    threading.Thread(target=worker_hook_tr, args=(message, _from, to)).start()
    return hexchat.EAT_ALL


def hook_str(word, word_eol, userdata):
    message = word_eol[1]
    context = hexchat.get_context()
    print(Bold + hexchat.get_info('nick') + NormalText + Color + '08 > ' + message)
    threading.Thread(target=worker_hook_str, args=(context, message,)).start()
    return hexchat.EAT_ALL


def hook_say(word, word_eol, userdata):
    message = hexchat.strip(word_eol[0])
    channel = hexchat.get_info('channel')
    context = hexchat.get_context()

    key = hexchat.get_info('network') + ' ' + channel.lower()

    if key in AUTOCHANNEL and message[:2] == '!!':
        print(Bold + hexchat.get_info('nick') + NormalText + Color + '13 > ' + message[2:])
        dest_lang, src_lang = AUTOCHANNEL[key]
        threading.Thread(target=worker_hook_str, args=(context, message[2:], src_lang, dest_lang)).start()
        return hexchat.EAT_ALL

    return hexchat.EAT_NONE


def hook_print_message(word, word_eol, userdata):
    nick = hexchat.strip(word[0])
    message = hexchat.strip(word[1])
    channel = hexchat.get_info('channel')
    context = hexchat.get_context()

    key = hexchat.get_info('network') + ' ' + channel + ' ' + nick.lower()

    if key in AUTOUSER:
        dest_lang, src_lang = AUTOUSER[key]
        threading.Thread(target=worker_hook_print_message, args=(context, message, nick, src_lang, dest_lang)).start()

    return hexchat.EAT_NONE


def hook_unload(userdata):
    print('google Translator unloaded!')


# ############################
#
# Hook definitions
#
# ############################

# commands

hexchat.command('MENU ADD "$TAB/[+] AutoTranslate" "ADDTRC %s"')
help_message = '/ADDTR <channel> <target_language> <source_language> - adds the channel to the watch list for automatic translations.  If target_language is not specified, then the DEFAULT_LANG set will be used.  If source_language is not specified, then language detection will be used. Starts your message with "!!" to auto translate.'
hexchat.hook_command('ADDTRC', hook_add_channel, help=help_message, priority=hexchat.PRI_HIGHEST)

hexchat.command('MENU ADD "$TAB/[-] AutoTranslate" "RMTRC %s"')
help_message = '/RMTR <channel> - removes channel from the watch list for automatic translations.'
hexchat.hook_command('RMTRC', hook_remove_channel, help=help_message, priority=hexchat.PRI_HIGHEST)

hexchat.command('MENU ADD "$NICK/[+] AutoTranslate" "ADDTR %s"')
help_message = '/ADDTR <user_nick> <target_language> <source_language> - adds the user to the watch list for automatic translations.  If target_language is not specified, then the DEFAULT_LANG set will be used.  If source_language is not specified, then language detection will be used.'
hexchat.hook_command('ADDTR', hook_add_user, help=help_message, priority=hexchat.PRI_HIGHEST)

hexchat.command('MENU ADD "$NICK/[-] AutoTranslate" "RMTR %s"')
help_message = '/RMTR <user_nick> - removes user_nick from the watch list for automatic translations.'
hexchat.hook_command('RMTR', hook_remove_user, help=help_message, priority=hexchat.PRI_HIGHEST)

help_message = '/LSUSERS - prints out all users on the watch list for automatic translations to the screen locally.'
hexchat.hook_command('LSUSERS', hook_print_user_list, help=help_message, priority=hexchat.PRI_HIGHEST)

help_message = '/LSCHANNELS - prints out all channels on the watch list for automatic translations to the screen locally.'
hexchat.hook_command('LSCHANNELS', hook_print_channel_list, help=help_message, priority=hexchat.PRI_HIGHEST)

help_message = '/TR <message> - translates message into the language according to form "to-from".  This auto detects the source language.'
hexchat.hook_command('TR', hook_tr, help=help_message, priority=hexchat.PRI_HIGHEST)

help_message = '/TRA <source language> <target language> <message> - translates message into the language specified.  This auto detects the source language.'
hexchat.hook_command('TRA', hook_tra, help=help_message, priority=hexchat.PRI_HIGHEST)

help_message = '/STR <message> - sends a message translated according to form "to-from", where "from" is the default language of origin and "to" is the default language destination.'
hexchat.hook_command('STR', hook_str, help=help_message, priority=hexchat.PRI_HIGHEST)

hexchat.hook_command('', hook_say, priority=hexchat.PRI_HIGHEST)

# prints

hexchat.hook_print('Private Message to Dialog', hook_print_message, priority=hexchat.PRI_HIGHEST)
hexchat.hook_print('Channel Message', hook_print_message, priority=hexchat.PRI_HIGHEST)
hexchat.hook_print('Channel Msg Hilight', hook_print_message, priority=hexchat.PRI_HIGHEST)

# unload

hexchat.hook_unload(hook_unload)

# ############################
#
# Main
#
# ############################

print('Google Translator loaded!')

try:
    AUTOUSER = load_config('google_tr_auto_user')
except:
    pass

try:
    AUTOCHANNEL = load_config('google_tr_auto_channel')
except:
    pass
