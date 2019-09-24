#!/usr/bin/env python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import asyncio
import sys
from flask import Flask, request, Response
from botbuilder.core import (BotFrameworkAdapter, BotFrameworkAdapterSettings,
                             ConversationState,
                             MemoryStorage,
                             UserState,
                             TurnContext
                             )
from botbuilder.schema import Activity
from qna_bot import QnaBot

LOOP = asyncio.get_event_loop()
APP = Flask(__name__, instance_relative_config=True)
APP.config.from_object("config.DefaultConfig")

SETTINGS = BotFrameworkAdapterSettings(APP.config["APP_ID"], APP.config["APP_PASSWORD"])
ADAPTER = BotFrameworkAdapter(SETTINGS)


async def on_error(context: TurnContext, error: Exception):
    """Top level exception handler for errors."""
    # This check writes out errors to console log
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    print(f'\n [on_turn_error]: {error}', file=sys.stderr)
    # Send a message to the user
    await context.send_activity('Oops. Something went wrong!')


BOT = QnaBot(APP.config['KB_ID'], APP.config['ENDPOINT_KEY'], APP.config['HOST'])


@APP.route("/api/messages", methods=["POST"])
def messages():
    """Main bot message handler."""
    if request.headers["Content-Type"] == "application/json":
        body = request.json
    else:
        return Response(status=415)

    activity = Activity().deserialize(body)
    auth_header = (request.headers["Authorization"] if "Authorization" in request.headers else "")

    async def aux_func(turn_context):
        await BOT.on_turn(turn_context)

    try:
        task = LOOP.create_task(
            ADAPTER.process_activity(activity, auth_header, aux_func)
        )
        LOOP.run_until_complete(task)
        return Response(status=201)
    except Exception as exception:
        raise exception


if __name__ == "__main__":
    try:
        APP.run(debug=True, port=APP.config["PORT"])  # nosec debug
    except Exception as exception:
        raise exception
