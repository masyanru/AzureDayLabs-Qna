# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Implements bot Activity handler base."""
import sys
from botbuilder.ai.qna import QnAMakerEndpoint, QnAMaker
from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
import json
import http.client, urllib.request, urllib.parse, urllib.error


class QnaBot(ActivityHandler):
    """Main activity handler for the bot."""
    def __init__(self, kb_id: str, endpoint_key: str, host: str):
        print(f'kb_id: {kb_id}, endpoint: {endpoint_key}, host: {host}', file=sys.stderr)
        self._qna_endpoint = QnAMakerEndpoint(kb_id,
                                              endpoint_key,
                                              host)
        self._qna_maker = QnAMaker(self._qna_endpoint)

    async def on_message_activity(self, turn_context: TurnContext):
        """Called when a message received from user."""
        print(f'Received message activity. {turn_context.activity.text}', file=sys.stderr)
        print(turn_context.activity.text)
        response = self.qamaker(turn_context.activity.text)

        if response:
            print(f'Received response from qna. {response}', file=sys.stderr)
            await turn_context.send_activity(MessageFactory.text(response))
        else:
            print(f'No answer from QNA')
            await turn_context.send_activity(MessageFactory.text("No QnA Maker answers were found."))

    def qamaker(self, message):

        question = message

        header = {
            'Content-Type': 'application/json',
            'Authorization': 'Endpointkey f5c7a375-d540-4dec-bc6a-6b8ef68b9d78'}
        params = urllib.parse.urlencode({})

        body = {
            "question": question,
            "top": 1
        }

        conn = http.client.HTTPSConnection('qnmakertest12.azurewebsites.net')

        conn.request("POST",
                     "/qnamaker/knowledgebases/c6e768f5-7358-4352-aad6-338ff69f56ac/generateAnswer?%s" % params,
                     str(body).encode('utf-8'), header)
        response = conn.getresponse()
        data = response.read()
        data = json.loads(data)
        resp = "{0}".format(data['answers'][0]['answer'])
        return resp


