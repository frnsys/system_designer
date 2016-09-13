import json
import logging
import flask_socketio


class SocketIO():
    def __init__(self, redis_host='redis://localhost:6379'):
        self.redis_host = redis_host
        self.socketio = flask_socketio.SocketIO(message_queue=redis_host)

    def emit(self, chan, data, namespace='/simulation'):
        self.socketio.emit(chan, data, namespace=namespace)


class SocketIOHandler(logging.Handler):
    def __init__(self, redis_host='redis://localhost:6379', namespace='/simulation'):
        self.namespace = namespace
        self.socketio = SocketIO(redis_host)

    def emit(self, record):
        try:
            # format: 'CHAN:DATA'
            chan, datastr = record.getMessage().split(':', 1)
            self.socketio.emit(chan, json.loads(datastr), namespace=self.namespace)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
