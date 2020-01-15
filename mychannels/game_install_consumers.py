# -*- encoding: utf-8 -*-

from channels import Group


def game_install_connect(message):
    # Work out room name from path (ignore slashes)
    # Accept the connection request
    Group('game_install').add(message.reply_channel)
    # Accept the connection request
    message.reply_channel.send({"accept": True})


def game_install_disconnect(message):
    Group('game_install').discard(message.reply_channel)


def game_install_receive(message):
    # ASGI WebSocket packet-received and send-packet message types
    # both have a "text" key for their textual data.
    Group('game_install').send({
        "text": "ok"
    })


def game_install_update(message):
    Group('game_install').send({
        "text": message.content['message'],
    })
