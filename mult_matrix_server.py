#!/usr/bin/env python

import itertools
import threading
import multiprocessing
import time

from mpi4py import MPI
from pysimplesoap.server import SoapDispatcher, SOAPHandler
from BaseHTTPServer import HTTPServer

CULC_THREAD_COUNT = multiprocessing.cpu_count()

comm = MPI.COMM_WORLD

RANK = comm.Get_rank()
SIZE = comm.Get_size()

SERVER_PORT = int("8%03d" % RANK)

def calculatorThread(comm):
    status = MPI.Status()

    while True:
        (row, col) = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)

        if len(row) == len(col):
            tag = status.Get_tag()
            src = status.Get_source()

            res = sum([a*b for a, b in zip(row, col)])

            comm.send(res, dest=src, tag=tag)

for _ in itertools.repeat(None, CULC_THREAD_COUNT):
    threading.Thread(target=calculatorThread, args=(comm,)).start()

NEXT_MPI_RECEIVER = RANK

def getMPIDest():
    global SIZE, NEXT_MPI_RECEIVER
    next_receiver = NEXT_MPI_RECEIVER

    if NEXT_MPI_RECEIVER+1 < SIZE:
        NEXT_MPI_RECEIVER += 1
    else:
        NEXT_MPI_RECEIVER = 0

    return next_receiver

def sendTask(index, row, col):
    # use index as message tag
    comm.send((row, col), dest=getMPIDest(), tag=index)

def sendMatrices(first_matrix, first_matrix_width, first_matrix_height,
    second_matrix, second_matrix_width, second_matrix_height):
    assert first_matrix_width == second_matrix_height
    i = 0
    while i < first_matrix_height:
        j = 0
        while j < second_matrix_width:
            index = i*second_matrix_width + j
            row = first_matrix[i*first_matrix_width:i*first_matrix_width+first_matrix_width]
            col = second_matrix[j::second_matrix_width]
            sendTask(index, row, col)
            j += 1
        i += 1

def receiveResult():
    status = MPI.Status()
    res = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
    # tag is index in matrix elem list
    tag = status.Get_tag()
    return tag, res # is index, value

def multiplyMatrix(first_matrix, first_matrix_width, first_matrix_height,
    second_matrix, second_matrix_width, second_matrix_height):

    start_time = time.time()

    print "accepted connection"

    if first_matrix_width != second_matrix_height:
        raise ValueError('w1 != h2')

    threading.Thread(target=sendMatrices, args=(first_matrix, first_matrix_width, first_matrix_height,
        second_matrix, second_matrix_width, second_matrix_height)).start()

    result_matrix = [0] * (first_matrix_height*second_matrix_width)

    for _ in itertools.repeat(None, len(result_matrix)):
        index, res = receiveResult()
        result_matrix[index] = res

    print "%s seconds" % (time.time() - start_time)

    return {'result_matrix': result_matrix, 'result_matrix_width': second_matrix_width,
        'result_matrix_height': first_matrix_height}

dispatcher = SoapDispatcher(
    'multiplyMatrix',
    location = "http://localhost:%d/" % SERVER_PORT,
    action   = "http://localhost:%d/" % SERVER_PORT,
    trace    = True,
    ns       = True
)

dispatcher.register_function(
    'multiplyMatrix',
    multiplyMatrix,
    returns = { 'result_matrix': [int], 'result_matrix_width': int, 'result_matrix_height': int },
    args    = { 'first_matrix':  [int], 'first_matrix_width':  int, 'first_matrix_height':  int,
                'second_matrix': [int], 'second_matrix_width': int, 'second_matrix_height': int }
)

httpd = HTTPServer(("", SERVER_PORT), SOAPHandler)
httpd.dispatcher = dispatcher

httpd.serve_forever()
