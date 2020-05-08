import re, json
from typing import Tuple

from tradebot.messaging.message import Message, MessageHandler
from tradebot.objects.stockdescriptor import StockDescriptor
from tradebot.objects.limitdescriptor import LimitDescriptor


cli_handler = None


def __setup_handler(name: str = 'cli'):
    global cli_handler

    if cli_handler is None:
        cli_handler = MessageHandler(name)


def __is_keyword(s: str) -> bool:
    return s.find('=') >= 0


def __parse_variable(s: str) -> Tuple[str, str]:
    n, v = s.split('=')
    return n, v


def parse_command(s: str):
    if cli_handler is None:
        __setup_handler()

    args = s.split(' ')
    nargs = len(args)

    # TODO Add command parsing here...
    data = {}
    if args[0] == 'add':
        data['acronym'] = args[1]
        data['shares'] = 1
        data['buy_price'] = -1
        for a in range(2, len(args)):
            if __is_keyword(args[a]):
                n, v = __parse_variable(args[a])
                data[n] = v
            elif a == 2:
                data['shares'] = int(args[a])
            else:
                data['buy_price'] = args[a]
        cli_handler.send(Message('vault_request', 'add', StockDescriptor(data['acronym'],
                                                                         data['buy_price'], 0,
                                                                         int(data['shares']))))
    elif args[0] == 'remove':
        data['acronym'] = args[1]
        data['shares'] = -1
        if len(args) == 3:
            if __is_keyword(args[2]):
                _, v = __parse_variable(args[2])
                data['shares'] = v
            else:
                data['shares'] = args[2]
        cli_handler.send(Message('vault_request', 'remove', StockDescriptor(data['acronym'],
                                                                            0, 0,
                                                                            int(data['shares']))))
    elif args[0] == 'list':
        data['acronym'] = 'all'
        if len(args) == 2:
            if __is_keyword(args[1]):
                _, v = __parse_variable(args[1])
                data['acronym'] = v
            else:
                data['acronym'] = args[1]
        cli_handler.send(Message('vault_request', 'list', data['acronym']))
    elif args[0] == 'limit':
        data['id'] = args[1]
        if len(args) == 5:
            data['limit'] = LimitDescriptor(args[2], float(args[4]), float(args[3]))
        elif len(args) == 4:
            data['limit'] = LimitDescriptor('%', float(args[3]), float(args[2]))
        else:
            data['limit'] = LimitDescriptor('%', 0.95, 1.05)
        cli_handler.send(Message('monitor_config', 'limit', data))
    elif args[0] == 'buy':
        data['acronym'] = args[1]
        data['shares'] = 1
        data['bid_price'] = -1
        for a in range(2, len(args)):
            if __is_keyword(args[a]):
                n, v = __parse_variable(args[a])
                data[n] = v
            elif a == 2:
                data['shares'] = int(args[a])
            else:
                data['bid_price'] = args[a]
        cli_handler.send(Message('trade_request', 'buy', StockDescriptor(data['acronym'],
                                                                         data['bid_price'], 0,
                                                                         int(data['shares']))))
    elif args[0] == 'sell':
        data['id'] = args[1]
        data['shares'] = -1
        if len(args) == 3:
            if __is_keyword(args[2]):
                n, v = __parse_variable(args[2])
                data[n] = v
            else:
                data['shares'] = int(args[2])
        cli_handler.send(Message('trade_request', 'sell', data))
    elif args[0] == 'force-update':
        cli_handler.send(Message('monitor_config', 'update'))
    elif args[0] == 'export':
        cli_handler.send(Message('all', 'save'))
    elif args[0] == 'refresh':
        cli_handler.send(Message('all', 'load'))
    elif nargs == 1:
        cli_handler.send(Message(args[0]))
    elif nargs == 2:
        cli_handler.send(Message(args[0], args[1]))
    elif nargs == 3:
        cli_handler.send(Message(args[0], args[1], json.loads(args[2])))