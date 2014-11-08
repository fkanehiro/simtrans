import unittest
import doctest
import simtrans.utils
import simtrans.collada
import simtrans.urdf
import simtrans.sdf
import simtrans.vrml
import simtrans.graphviz


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(simtrans.utils))
    tests.addTests(doctest.DocTestSuite(simtrans.collada))
    tests.addTests(doctest.DocTestSuite(simtrans.urdf))
    tests.addTests(doctest.DocTestSuite(simtrans.sdf))
    tests.addTests(doctest.DocTestSuite(simtrans.vrml))
    tests.addTests(doctest.DocTestSuite(simtrans.graphviz))
    return tests
