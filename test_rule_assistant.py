#!/usr/bin/env python3

import unittest
import os
import shutil
import importlib
import subprocess

from RuleAssistantTests import Utils

CreateApertiumRules = None

ParentFolder = os.path.dirname(__file__)
print(ParentFolder)
DataFolder = os.path.join(ParentFolder, 'Rule Assistant')
TestFolder = os.path.join(ParentFolder, 'RuleAssistantTests')

def setUpModule():
    global CreateApertiumRules
    script = 'CreateApertiumRules.py'
    with open(os.path.join(ParentFolder, script)) as fin:
        with open(os.path.join(TestFolder, script), 'w') as fout:
            fout.write(fin.read().replace('import Utils', 'from . import Utils'))
    CreateApertiumRules = importlib.import_module(
        'RuleAssistantTests.CreateApertiumRules')

class Reporter:
    def __init__(self):
        self.infos = []
        self.errors = []
    def Info(self, *args):
        self.infos.append(args)
    def Error(self, *args):
        self.errors.append(args)

class BaseTest:
    Data = {
        'adj': {
            'gender': {
                'affix': [('FEM.a', 'f'), ('MASC.a', 'm')],
            },
            'number': {
                'affix': [('PL', 'pl'), ('SG', 'sg')],
            },
        },
        'n': {
            'gender': {
                'lemma': [('bicicleta1.1', 'f'), ('coche1.1', 'm'),
                          ('carmelo1.1', 'm'), ('cosa1.1', 'f'),
                          ('niña1.1', 'f'), ('manzana1.1', 'f'),
                          ('luz1.1', 'f'), ('niño1.1', 'm'), ('camino1.1', 'm')],
            },
            'number': {
                'affix': [('PL', 'pl'), ('SG', 'sg')],
            },
        },
    }
    RuleFile = 'Ex3_Adj-Noun.xml'
    RuleNumber = None
    RuleCount = 1
    TransferFile = None
    TestPairs = [
        ('^long1.1<adj>/largo1.1<adj>$ ^road1.1<n><SG>/camino1.1<n><m><SG>$',
         '^camino1.1<n><SG>$ ^largo1.1<adj><MASC_a><SG>$'),
    ]

    @classmethod
    def fileName(cls, ext):
        return os.path.join(TestFolder, cls.__name__ + '.' + ext)

    @classmethod
    def setUpClass(cls):
        global Utils
        dest = cls.fileName('t1x')
        print(f'checking for {dest}')
        if os.path.exists(dest):
            print(f'removing {dest}')
            os.remove(dest)
        if cls.TransferFile is not None:
            shutil.copy(os.path.join(DataFolder, cls.TransferFile), dest)
        Utils.DATA = cls.Data

    @classmethod
    def tearDownClass(cls):
        global Utils
        Utils.DATA = {}

    def test_step1_create(self):
        report = Reporter()
        path = os.path.join(DataFolder, self.RuleFile)
        self.assertTrue(CreateApertiumRules.CreateRules(
            None, report, None, path, self.fileName('t1x'), self.RuleNumber,
        ))
        self.assertIn((f'Added {self.RuleCount} rule(s) from {path}.',),
                      report.infos)

    def test_step2_validate(self):
        proc = subprocess.run(
            ['apertium-validate-transfer', self.fileName('t1x')],
            text=True, check=False, capture_output=True,
        )
        self.assertEqual(0, proc.returncode)

    def test_step3_compile(self):
        proc = subprocess.run(
            ['apertium-preprocess-transfer',
             self.fileName('t1x'), self.fileName('bin')],
            text=True, check=False, capture_output=True,
        )
        self.assertEqual(0, proc.returncode)

    def test_step4_run(self):
        proc = subprocess.Popen(
            ['apertium-transfer', '-b', '-z',
             self.fileName('t1x'), self.fileName('bin')],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        for i, (inp, exp) in enumerate(self.TestPairs, 1):
            with self.subTest(input_line=i):
                proc.stdin.write(inp.encode('utf-8') + b'\0')
                proc.stdin.flush()
                out = b''
                while (c := proc.stdout.read(1)) != b'\0':
                    out += c
                self.assertEqual(exp, out.decode('utf-8'))
        proc.communicate()
        proc.stdin.close()
        proc.stdout.close()
        proc.stderr.close()
        self.assertEqual(proc.poll(), 0)

class SpanishAdjNoun(BaseTest, unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()
