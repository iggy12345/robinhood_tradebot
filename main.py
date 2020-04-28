from tradebot.controllers import *
from tradebot.adapters.timer_relay import TimerRelay
from tradebot.adapters.pyrh_adapter import PyrhAdapter
from tradebot.file_io import *
from tradebot.messaging.message import Message, MessageHandler
from tradebot.messaging.socket_console_interaction import SocketConsoleServer


if __name__ == '__main__':
    print('Reading in stock info')
    stocks = read_stocks('./stocks.txt')

    print('Configuring limit info')
    limit_dict = {}
    for s in stocks:
        print('configuring {}'.format(s[0]))
        limit_dict[s[0].acronym] = s[1]

    print('Creating modules')
    term = SocketConsoleServer()
    t = timer.Timer('update_trigger', interval=3600)
    relay = TimerRelay('timer_relay', Message('monitor_config', 'update'))
    rx = MessageHandler('receiver', ['monitor_config'])
    p = PyrhAdapter(stdin_port=term.port())
    dm = monitor.StockMonitor('monitor', [t[0] for t in stocks], limit_dict, p, term.port())
    dc = datacontroller.DataController('data_controller')
    tc = tradecontroller.TradeController('trade_controller')

    print('Starting modules')
    relay.start()
    p.start()
    dm.start()
    dc.start()
    tc.start()
    t.start()

    print('Waiting for timer to finish')
    t.join()
    # while True:
    #     if rx.receive() is not None:
    #         print('Relay fired')
