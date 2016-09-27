import os
import click
import aiomas
import logging
import multiprocessing
from .front import front_app
from .node import Node, serializers
from concurrent.futures import ProcessPoolExecutor
from daemonize import Daemonize

logging.basicConfig(level=logging.INFO, format='%(message)s')


@click.group()
def cli():
    pass


@cli.command()
@click.argument('port', 'port to run server on', default=5000)
@click.argument('working_dir', 'working dir', type=click.Path(exists=True, file_okay=False), default=os.getcwd())
@click.argument('redis_host', 'redis host', default='redis://localhost:6379')
def front(port, working_dir, redis_host):
    """start the frontend server"""
    import eventlet
    eventlet.monkey_patch() # for flask_socketio message queue support
    from flask_socketio import SocketIO
    static = os.path.abspath(os.path.join(working_dir, 'static'))
    templs = os.path.abspath(os.path.join(working_dir, 'templates'))
    app = front_app(static_folder=static, template_folder=templs)
    socketio = SocketIO(app, message_queue=redis_host)
    socketio.run(app, host='0.0.0.0', port=port) # doesn't seem to work if debug=True


@cli.command()
@click.argument('port', 'port to run node on', default=5555)
def node(port):
    """start a node process"""
    start_node(port)


@cli.command()
@click.argument('start_port', 'starting port to run nodes on', default=5555)
@click.argument('cores', 'number of cores to use; 0 for all', default=0)
@click.option('-d', '--daemonize', is_flag=True, help='daemonize')
def nodes(start_port, cores, daemonize):
    """start multiple nodes"""

    cpus = multiprocessing.cpu_count()
    if cores > 0:
        cores = min(cpus, cores)
    else:
        cores = max(1, cpus - cores)
    click.echo('starting {} nodes'.format(cores))

    if daemonize:
        def action():
            start_nodes(start_port, cores)
        daemon = Daemonize(app='syd', pid='/tmp/syd.pid', action=action)
        daemon.start()
    else:
        start_nodes(start_port, cores)


def start_nodes(start_port, cores):
    """start multiple nodes"""
    with ProcessPoolExecutor(max_workers=cores) as executor:
        futs = []
        for i in range(cores):
            fut = executor.submit(start_node, start_port+i)
            futs.append(fut)

        try:
            # this waits until all subprocesses have completed
            # i.e. when all nodes are terminated
            for fut in futs:
                fut.result()
        except KeyboardInterrupt:
            click.echo('Goodbye')


def start_node(port):
    """start a node"""
    task = Node.start(('0.0.0.0', port),
                      codec=aiomas.codecs.MsgPackBlosc,
                      extra_serializers=[serializers.get_np_serializer])

    # terminates when the node's manager is given the 'stop' command
    aiomas.run(until=task)
