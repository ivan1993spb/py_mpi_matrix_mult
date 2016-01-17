#!/usr/bin/env python

from pysimplesoap.client import SoapClient, SoapFault

MATRIX_W=100
MATRIX_H=100


# create a simple consumer
client = SoapClient(
    location = "http://localhost:8008/",
    action = 'http://localhost:8008/',
    soap_ns = 'soap',
    # trace = True,
    ns = False)


response = client.multiplyMatrix(
    first_matrix=range(0, MATRIX_W*MATRIX_H),
    first_matrix_width=MATRIX_W,
    first_matrix_height=MATRIX_H,
    second_matrix=range(0,  MATRIX_W*MATRIX_H),
    second_matrix_width=MATRIX_W,
    second_matrix_height=MATRIX_H)

l = []
for i in range(1, len(response.result_matrix)):
    l.append(int(response.result_matrix[i]))
print l

print int(response.result_matrix_width)
print int(response.result_matrix_height)
