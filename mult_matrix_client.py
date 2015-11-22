#!/usr/bin/env python

from pysimplesoap.client import SoapClient, SoapFault

# create a simple consumer
client = SoapClient(
    location = "http://localhost:8008/",
    action = 'http://localhost:8008/',
    soap_ns = 'soap',
    # trace = True,
    ns = False)

# call the remote method
response = client.multiplyMatrix(
    first_matrix=[1, 2, 3, 4, 5, 6, 7, 8, 9],
    first_matrix_width=3,
    first_matrix_height=3,
    second_matrix=[10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
    second_matrix_width=5,
    second_matrix_height=3)

l = []
for i in range(1, len(response.result_matrix)):
    l.append(int(response.result_matrix[i]))
print l

print int(response.result_matrix_width)
print int(response.result_matrix_height)


response = client.multiplyMatrix(
    first_matrix=range(0, 900),
    first_matrix_width=30,
    first_matrix_height=30,
    second_matrix=range(0, 900),
    second_matrix_width=30,
    second_matrix_height=30)

l = []
for i in range(1, len(response.result_matrix)):
    l.append(int(response.result_matrix[i]))
print l

print int(response.result_matrix_width)
print int(response.result_matrix_height)
