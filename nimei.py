# -*- encoding: utf8 -*-

import urllib.request
import urllib.parse
import json
import time
import random

checkMentionToken = ''
replyToken = ''

def log(message):
    print(message)



def writeCurrentMessageId(messageId):
    messageId = messageId
    log('Writing current message id ' + messageId + ' to file')

    currentMessageFileHandler = open('current-message-id.txt', 'w')
    currentMessageFileHandler.write(messageId)
    currentMessageFileHandler.close()



def getCurrentMessageId():
    log('Try to get message id from file')
    currentMessageFileHandler = open('current-message-id.txt', 'r')
    currentMessageId = currentMessageFileHandler.readline()
    currentMessageFileHandler.close()


    if currentMessageId == '':
        currentMessageId = '0'

    log('Current message id is ' + currentMessageId)

    return currentMessageId



def saveLatestMetionId():
    log('Try to get latest mention id')
    responseHandler = urllib.request.urlopen('https://api.weibo.com/2/statuses/mentions/ids.json?count=1&access_token=' + checkMentionToken)

    jsonData = json.loads(responseHandler.readall().decode('utf-8'))

    currentMessageId = '0'

    if len(jsonData['statuses']) > 0:
        currentMessageId = str(jsonData['statuses'][0])

    log('Current message id is ' + currentMessageId)

    writeCurrentMessageId(currentMessageId)



def getLatestMentions():
    currentMessageId = getCurrentMessageId()
    #currentMessageId = '0'
    log('Current message id is ' + currentMessageId)

    responseHandler = urllib.request.urlopen('https://api.weibo.com/2/statuses/mentions.json?count=1&access_token=' + checkMentionToken + '&since_id=' + currentMessageId)

    responseContent = responseHandler.readall()

    jsonData = json.loads(responseContent.decode('utf-8'))

    if len(jsonData['statuses']) > 0:
        writeCurrentMessageId(jsonData['statuses'][0]['idstr'])

    return jsonData['statuses']


def getFirstLetter(text):
    if len(text) == 0:
        return ''

    if text[0] == '[':
        text = text.partition(']')[2]


    if text[0] == '@':
        text = getFirstLetter(text.partition(' ')[2])
    elif text[0] == '/':
        text = '转'
    else:
        text = text[0]

    if len(text) == 0:
        text = ''
    else:
        text = text[0]

    return text


def replyMessage(message):
    if message['user']['screen_name'] == 'iworm':
        return

    text = message['text'].strip()
    text = getFirstLetter(text)

    text = text + '你妹！' + ' //@' + message['user']['screen_name'] + ': ' + message['text']

    text = text[0:135]

    postData = urllib.parse.urlencode({'status': text, 'id': message['idstr'], 'access_token': replyToken}).encode('utf-8')

    urllib.request.urlopen('https://api.weibo.com/2/statuses/repost.json', postData)

    print(text)

    print()



def wait(seconds):
    print('wait for ' + str(seconds) + ' seconds')
    time.sleep(seconds)



def tryToReplyNewMentions():
    while(True):
        log('Checking for new mentions')

        messages = getLatestMentions()

        if len(messages) > 0:
            log('You have new mentions')

        for message in messages:
            replyMessage(message)

        log('Waiting for new mentions')
        wait(60)



if __name__ == '__main__':
    log('Ready to boot up, make all mentions as read')
    saveLatestMetionId()

    log('Bot started successfuly')
    wait(5)

    tryToReplyNewMentions()
