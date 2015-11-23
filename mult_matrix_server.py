#!/usr/bin/env python

import threading
from mpi4py import MPI
import itertools

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    # starting soap server

    from pysimplesoap.server import SoapDispatcher, SOAPHandler
    from BaseHTTPServer import HTTPServer
    import time

    class TagGenerator:
        """TagGenerator generates unique tags"""

        def __init__(self):
            self.tags = []
            self.locker = threading.Lock()

        def genTag(self):
            """Generate unique tag"""

            self.locker.acquire()

            # try to find free tag
            for tag in xrange(len(self.tags)):
                if tag not in self.tags:
                    self.tags.append(tag)
                    self.locker.release()
                    return tag

            # create new tag with max tag value
            tag = len(self.tags)
            self.tags.append(tag)
            self.locker.release()

            return tag

        def freeTag(self, tag):
            if tag in self.tags:
                self.locker.acquire()
                self.tags.remove(tag)
                self.locker.release()

    class ReceiverCounter:

        def __init__(self, list):
            # list of receivers
            self.list = list
            self.counter = 0

        def next(self):
            next = self.list[self.counter]

            self.counter += 1
            if self.counter == len(self.list):
                self.counter = 0

            return next

    tagGenerator = TagGenerator()
    recCounter = ReceiverCounter(range(1, size))


    def multiplyMatrix(first_matrix, first_matrix_width, first_matrix_height,
        second_matrix, second_matrix_width, second_matrix_height):
        "multiply matrix"

        start_time = time.time()

        print "received connection"

        if first_matrix_width != second_matrix_height:
            raise ValueError('w != h')

        global tagGenerator, recCounter, comm


        tags = [0] * (first_matrix_height*second_matrix_width)
        i = 0

        while i < first_matrix_height:
            j = 0

            while j < second_matrix_width:
                row = first_matrix[i*first_matrix_width:i*first_matrix_width+first_matrix_width]
                col = second_matrix[j::second_matrix_width]

                tag = tagGenerator.genTag()
                dest = recCounter.next()

                comm.send((row, col), dest=dest, tag=tag)

                tags[i*second_matrix_width + j] = tag

                j += 1

            i += 1

        result_matrix = [0] * (first_matrix_height*second_matrix_width)

        status = MPI.Status()
        for _ in itertools.repeat(None, first_matrix_height*second_matrix_width):
            value = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
            tag = status.Get_tag()
            result_matrix[tags.index(tag)] = value
            tagGenerator.freeTag(tag)

        print "%s seconds" % (time.time() - start_time)

        return {'result_matrix': result_matrix, 'result_matrix_width': second_matrix_width,
                                                'result_matrix_height': first_matrix_height}

    dispatcher = SoapDispatcher(
        'multiplyMatrix',
        location = "http://localhost:8008/",
        action   = 'http://localhost:8008/',
        trace    = True,
        ns       = True
    )

    dispatcher.register_function(
        'multiplyMatrix',
        multiplyMatrix,
        returns = { 'result_matrix': [int], 'result_matrix_width': int, 'result_matrix_height': int},
        args    = { 'first_matrix': [int], 'first_matrix_width': int, 'first_matrix_height': int,
                    'second_matrix': [int], 'second_matrix_width': int, 'second_matrix_height': int}
    )

    httpd = HTTPServer(("", 8008), SOAPHandler)
    httpd.dispatcher = dispatcher

    httpd.serve_forever()

else:

    def calcThread(comm):
        status = MPI.Status()

        while True:
            (row, col) = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
            assert len(row) == len(col)
            tag = status.Get_tag()

            comm.send(sum([a*b for a, b in zip(row, col)]), dest=0, tag=tag)


    for _ in itertools.repeat(None, 1):
        t = threading.Thread(target=calcThread, args=(comm,))
        t.start()
