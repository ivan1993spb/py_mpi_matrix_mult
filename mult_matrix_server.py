#!/usr/bin/env python

# from mpi4py import MPI

# comm = MPI.COMM_WORLD
rank = 0
# rank = comm.Get_rank()

if rank == 0:
    # starting soap server

    from pysimplesoap.server import SoapDispatcher, SOAPHandler
    from BaseHTTPServer import HTTPServer

    def multiplyMatrix(first_matrix, first_matrix_width, first_matrix_height,
        second_matrix, second_matrix_width, second_matrix_height):
        "multiply matrix"

        if first_matrix_width != second_matrix_height:
            raise ValueError('w != h')

        print first_matrix
        print first_matrix_width
        print first_matrix_height
        print second_matrix
        print second_matrix_width
        print second_matrix_height

        return {'result_matrix': [99, 2, 3, 4, 5], 'result_matrix_width': 3, 'result_matrix_height': 3}

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
    pass
