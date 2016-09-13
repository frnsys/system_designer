import syd
import sys
import time
import examples


if __name__ == '__main__':
    choices = ['deepthought', 'schelling', 'sir', 'gameoflife']
    if len(sys.argv) < 2:
        print('choose one of:', choices)
        sys.exit()

    example = sys.argv[1]
    if example not in choices:
        print('choose one of:', choices)
        sys.exit(0)

    try:
        node = syd.Node.create(('localhost', 5001))
        # node = syd.Cluster(
            # 8000,
            # [('localhost', 'ftseng', 5001)],
            # venv='/home/ftseng/env/syd')

        s = time.time()
        getattr(examples, example).run(node)
        # deepthought.run(node)
        print('elapsed:', time.time() - s)
    finally:
        node.shutdown()
