#!/usr/bin/env python

import threading
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

if rank == 0:
    # starting soap server

    from pysimplesoap.server import SoapDispatcher, SOAPHandler
    from BaseHTTPServer import HTTPServer

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

        def __init__(self):
            # self.size = size
            # self.counter = first
            pass

        def next(self):
            return 1

    tagGenerator = TagGenerator()
    recCounter = ReceiverCounter()

    def multiplyMatrix(first_matrix, first_matrix_width, first_matrix_height,
        second_matrix, second_matrix_width, second_matrix_height):
        "multiply matrix"
        
        global tagGenerator, recCounter, comm

        if first_matrix_width != second_matrix_height:
            raise ValueError('w != h')

        i = 0

        # [(src, tag, index of value), ...]
        srcTagsI = []

        while i < first_matrix_height:
            j = 0

            while j < second_matrix_width:
                row = first_matrix[i*first_matrix_width:i*first_matrix_width+first_matrix_width]
                col = second_matrix[j::second_matrix_width]

                tag = tagGenerator.genTag()
                dest = recCounter.next()

                comm.send((row, col), dest=dest, tag=tag)

                srcTagsI.append((dest, tag, i*second_matrix_width + j))
                j += 1
            
            i += 1

        # empty list [0, 0, 0, ...]
        result_matrix = [0] * (first_matrix_height*second_matrix_width)

        for src, tag, i in srcTagsI:
            result_matrix[i] = comm.recv(source=src, tag=tag)

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

    def calcThread(tag, row, col):
        global comm
        assert len(row) == len(col)
        comm.send(sum([a*b for a, b in zip(row, col)]), dest=0, tag=tag)

    status = MPI.Status()
    while True:
        (row, col) = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
        tag = status.Get_tag()

        t = threading.Thread(target=calcThread, args=(tag, row, col))
        t.start()
