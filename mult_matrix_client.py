#!/usr/bin/env python

from pysimplesoap.client import SoapClient, SoapFault
import numpy

# create a simple consumer
client = SoapClient(
    location = "http://localhost:8008/",
    action = 'http://localhost:8008/',
    soap_ns = 'soap',
    trace = True,
    ns = False)

# call the remote method
response = client.multiplyMatrix(
    first_matrix=[1, 2, 3, 4, 5],
    first_matrix_width=1,
    first_matrix_height=1,
    second_matrix=[1, 2, 99],
    second_matrix_width=1,
    second_matrix_height=1)

l = []
for i in range(1, len(response.result_matrix)):
    l.append(int(response.result_matrix[i]))
print l

print int(response.result_matrix_width)
print int(response.result_matrix_height)