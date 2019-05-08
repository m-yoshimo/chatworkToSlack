#-*- coding: utf-8 -*-
from __future__ import print_function

import requests
import os
from pytz import timezone
from datetime import datetime

cwtoken = os.environ['CHATWORK_API_TOKEN']
sltoken = os.environ['SLACK_API_TOKEN']

cwapiurl = 'https://api.chatwork.com/v2'
slapiurl = 'https://slack.com/api'

def lambda_handler(event, context):
    fromto = event['fromto']
    mentions = event['mention']

    for list in fromto:
        roomid  = list['cwroomid']
        channel = list['slchannel']

        url1     = cwapiurl + '/rooms/' + roomid + '/messages'
        headers1 = {'X-ChatWorkToken': cwtoken }

        try :
            req1 = requests.get(url1, headers=headers1)
            if req1.status_code == 204 :
                print('204' )
            else :
                res_json = req1.json()
                i = 0
                l = len(res_json) - 1
                while i <= l :
                    body = res_json[i]['body']
                    name = res_json[i]['account']['name']
                    msid = res_json[i]['message_id']
                    time = res_json[i]['send_time']

                    try :
                        jst_time = datetime.fromtimestamp(time).as_timezone(timezone('Asia/Tokyo'))
                        text = '*' + str(jst_time) + ' message from: ' + name + '*\n'
                        for mention in mentions:
                            cw_to = mention['cwto']
                            sl_to = mention['slto']
                            if body.find(cw_to) > 0 :
                                text += '<@' + sl_to + '>\n'
                        text += '```' + body + '```'
                        url2 = slapiurl + '/chat.postMessage'
                        params2 = {
                            'token' : sltoken,
                            'channel' : channel,
                            'text' : text,
                            'as_user': 'false',
                            'username': 'ChatWork(auto)'
                        }
                        req2 = requests.put(url2, params=params2)

                    except Exception as e :
                        print('[error][put]' + str(e))

                    i += 1

        except Exception as e :
            print('[error][get]' + str(e))

if __name__ == "__main__":
    lambda_handler({}, {})
