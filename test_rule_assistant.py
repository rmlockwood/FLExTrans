#!/usr/bin/env python3

import unittest
import os
import shutil
import importlib
import subprocess

from RuleAssistantTests import Utils

CreateApertiumRules = None

ParentFolder = os.path.dirname(__file__)
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
    Data = {}
    RuleFile = 'Ex3_Adj-Noun.xml'
    RuleNumber = None
    RuleCount = 1
    TransferFile = None
    TestPairs = []

    def runTest(self):
        global Utils
        prefix = os.path.join(TestFolder, self.__class__.__name__)
        t1xFile = prefix + '.t1x'
        binFile = prefix + '.bin'

        if os.path.exists(t1xFile):
            os.remove(t1xFile)
        if self.TransferFile is not None:
            shutil.copy(os.path.join(DataFolder, self.TransferFile), t1xFile)
        Utils.DATA = self.Data
        
        # Create rules
        report = Reporter()
        path = os.path.join(DataFolder, self.RuleFile)
        self.assertTrue(CreateApertiumRules.CreateRules(
            'source', 'target', report, None, path, t1xFile, self.RuleNumber,
        ))
        self.assertIn((f'Added {self.RuleCount} rule(s) from {path}.',),
                      report.infos)

        # Validate rules
        validate = subprocess.run(
            ['apertium-validate-transfer', t1xFile],
            text=True, check=False, capture_output=True,
        )
        self.assertEqual(0, validate.returncode)

        # Compile rules
        preproc = subprocess.run(
            ['apertium-preprocess-transfer', t1xFile, binFile],
            text=True, check=False, capture_output=True,
        )
        self.assertEqual(0, preproc.returncode)

        # Apply rules
        proc = subprocess.Popen(
            ['apertium-transfer', '-b', '-z', t1xFile, binFile],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        for inp, exp in self.TestPairs:
            with self.subTest(input_line=inp):
                proc.stdin.write(inp.encode('utf-8') + b'\0')
                proc.stdin.flush()
                out = b''
                while (c := proc.stdout.read(1)) != b'\0':
                    out += c
                self.assertEqual(exp, out.decode('utf-8'))
        # End process
        proc.communicate()
        proc.stdin.close()
        proc.stdout.close()
        proc.stderr.close()
        self.assertEqual(proc.poll(), 0)

        Utils.DATA = {}

class FrenchSpanishAdjNoun(BaseTest, unittest.TestCase):
    Data = {
        None: {
            'gender': {
                'source_features': ['f', 'm'],
            },
        },
        'adj': {
            'gender': {
                'target_affix': [('FEM.a', 'f'), ('MASC.a', 'm')],
            },
            'number': {
                'target_affix': [('PL', 'pl'), ('SG', 'sg')],
            },
        },
        'n': {
            'gender': {
                'target_lemma': [('bicicleta1.1', 'f'), ('coche1.1', 'm'),
                                 ('carmelo1.1', 'm'), ('cosa1.1', 'f'),
                                 ('niña1.1', 'f'), ('manzana1.1', 'f'),
                                 ('luz1.1', 'f'), ('niño1.1', 'm'),
                                 ('camino1.1', 'm')],
            },
            'number': {
                'source_affix': [('PL', 'pl'), ('SG', 'sg')],
                'target_affix': [('PL', 'pl'), ('SG', 'sg')],
            },
        },
    }
    TestPairs = [
        ('^long1.1<adj>/largo1.1<adj>$ ^road1.1<n><SG>/camino1.1<n><m><SG>$',
         '^camino1.1<n><SG>$ ^largo1.1<adj><MASC_a><SG>$'),
        ('^long1.1<adj>/largo1.1<adj>$ ^road1.1<n><PL>/camino1.1<n><m><PL>$',
         '^camino1.1<n><PL>$ ^largo1.1<adj><MASC_a><PL>$'),
        ('^long1.1<adj>/largo1.1<adj>$ ^bike1.1<n><SG>/bicicleta1.1<n><f><SG>$',
         '^bicicleta1.1<n><SG>$ ^largo1.1<adj><FEM_a><SG>$'),
        ('^long1.1<adj>/largo1.1<adj>$ ^bike1.1<n><PL>/bicicleta1.1<n><f><PL>$',
         '^bicicleta1.1<n><PL>$ ^largo1.1<adj><FEM_a><PL>$'),
    ]

class FrenchSpanishDefNoun_MissingSG(BaseTest, unittest.TestCase):
    Data = {
        None: {
            'gender': {
                'source_features': ['f', 'm'],
            },
        },
        'def': {
            'gender': {
                'target_lemma': [('el1.1', 'm'), ('los1.1', 'm'),
                                 ('las1.1', 'f'), ('la1.1', 'f')],
            },
            'number': {
                'target_lemma': [('el1.1', 'sg'), ('los1.1', 'pl'),
                                 ('las1.1', 'pl'), ('la1.1', 'sg')]
            },
        },
        'n': {
            'gender': {
                'target_lemma': [('bicicleta1.1', 'f'), ('coche1.1', 'm'),
                                 ('carmelo1.1', 'm'), ('cosa1.1', 'f'),
                                 ('niña1.1', 'f'), ('manzana1.1', 'f'),
                                 ('luz1.1', 'f'), ('niño1.1', 'm'),
                                 ('camino1.1', 'm')],
            },
            'number': {
                'source_affix': [('PL', 'pl')],
                'target_affix': [('PL', 'pl')],
            },
        },
    }
    RuleFile = 'Ex1b_Def-Noun.xml'
    TestPairs = [
        ('^the1.1<def>/el1.1<def>$ ^road1.1<n><SG>/camino1.1<n><m><SG>$',
         '^no-lemma-for-m<def>$ ^camino1.1<n>$'),
        ('^the1.1<def>/el1.1<def>$ ^road1.1<n><PL>/camino1.1<n><m><PL>$',
         '^los1.1<def>$ ^camino1.1<n><PL>$'),
        ('^the1.1<def>/el1.1<def>$ ^bike1.1<n><SG>/bicicleta1.1<n><f><SG>$',
         '^no-lemma-for-f<def>$ ^bicicleta1.1<n>$'),
        ('^the1.1<def>/el1.1<def>$ ^bike1.1<n><PL>/bicicleta1.1<n><f><PL>$',
         '^las1.1<def>$ ^bicicleta1.1<n><PL>$'),
    ]

class FrenchSpanishDefNoun_NullSG(BaseTest, unittest.TestCase):
    Data = {
        None: {
            'gender': {
                'source_features': ['f', 'm'],
            },
        },
        'def': {
            'gender': {
                'target_lemma': [('el1.1', 'm'), ('los1.1', 'm'),
                                 ('las1.1', 'f'), ('la1.1', 'f')],
            },
            'number': {
                'target_lemma': [('el1.1', 'sg'), ('los1.1', 'pl'),
                                 ('las1.1', 'pl'), ('la1.1', 'sg')]
            },
        },
        'n': {
            'gender': {
                'target_lemma': [('bicicleta1.1', 'f'), ('coche1.1', 'm'),
                                 ('carmelo1.1', 'm'), ('cosa1.1', 'f'),
                                 ('niña1.1', 'f'), ('manzana1.1', 'f'),
                                 ('luz1.1', 'f'), ('niño1.1', 'm'),
                                 ('camino1.1', 'm')],
            },
            'number': {
                'source_affix': [('PL', 'pl'), ('SG', 'sg')],
                'target_affix': [('PL', 'pl'), ('SG', 'sg')],
            },
        },
    }
    RuleFile = 'Ex1b_Def-Noun.xml'
    TestPairs = [
        ('^the1.1<def>/el1.1<def>$ ^road1.1<n><SG>/camino1.1<n><m><SG>$',
         '^el1.1<def>$ ^camino1.1<n><SG>$'),
        ('^the1.1<def>/el1.1<def>$ ^road1.1<n><PL>/camino1.1<n><m><PL>$',
         '^los1.1<def>$ ^camino1.1<n><PL>$'),
        ('^the1.1<def>/el1.1<def>$ ^bike1.1<n><SG>/bicicleta1.1<n><f><SG>$',
         '^la1.1<def>$ ^bicicleta1.1<n><SG>$'),
        ('^the1.1<def>/el1.1<def>$ ^bike1.1<n><PL>/bicicleta1.1<n><f><PL>$',
         '^las1.1<def>$ ^bicicleta1.1<n><PL>$'),
    ]

class FrenchSpanishDefAdjNoun(BaseTest, unittest.TestCase):
    Data = {
        None: {
            'gender': {
                'source_features': ['f', 'm'],
            },
            'number': {
                'source_features': ['sg', 'pl'],
            },
        },
        'adj': {
            'gender': {
                'target_affix': [('FEM.a', 'f'), ('MASC.a', 'm')],
            },
            'number': {
                'target_affix': [('PL', 'pl'), ('SG', 'sg')],
            },
        },
        'def': {
            'gender': {
                'target_lemma': [('el1.1', 'm'), ('los1.1', 'm'),
                                 ('las1.1', 'f'), ('la1.1', 'f')],
            },
            'number': {
                'target_lemma': [('el1.1', 'sg'), ('los1.1', 'pl'),
                                 ('las1.1', 'pl'), ('la1.1', 'sg')]
            },
        },
        'n': {
            'gender': {
                'target_lemma': [('bicicleta1.1', 'f'), ('coche1.1', 'm'),
                                 ('carmelo1.1', 'm'), ('cosa1.1', 'f'),
                                 ('niña1.1', 'f'), ('manzana1.1', 'f'),
                                 ('luz1.1', 'f'), ('niño1.1', 'm'),
                                 ('camino1.1', 'm')],
            },
            'number': {
                'source_affix': [('PL', 'pl'), ('SG', 'sg')],
                'target_affix': [('PL', 'pl'), ('SG', 'sg')],
            },
        },
    }
    RuleFile = 'Ex4a_Def-Adj-Noun.xml'
    TestPairs = [
        ('^the1.1<def>/el1.1<def>$ ^long1.1<adj>/largo1.1<adj>$ ^road1.1<n><SG>/camino1.1<n><m><SG>$',
         '^el1.1<def>$ ^camino1.1<n><SG>$ ^largo1.1<adj><MASC_a><SG>$'),
        ('^the1.1<def>/el1.1<def>$ ^long1.1<adj>/largo1.1<adj>$ ^road1.1<n><PL>/camino1.1<n><m><PL>$',
         '^los1.1<def>$ ^camino1.1<n><PL>$ ^largo1.1<adj><MASC_a><PL>$'),
        ('^the1.1<def>/el1.1<def>$ ^long1.1<adj>/largo1.1<adj>$ ^bike1.1<n><SG>/bicicleta1.1<n><f><SG>$',
         '^la1.1<def>$ ^bicicleta1.1<n><SG>$ ^largo1.1<adj><FEM_a><SG>$'),
        ('^the1.1<def>/el1.1<def>$ ^long1.1<adj>/largo1.1<adj>$ ^bike1.1<n><PL>/bicicleta1.1<n><f><PL>$',
         '^las1.1<def>$ ^bicicleta1.1<n><PL>$ ^largo1.1<adj><FEM_a><PL>$'),
    ]

class UnmarkedDefault(BaseTest, unittest.TestCase):
    RuleFile = 'unmarked_default.xml'
    Data = {
        None: {
            'gender': {
                'source_features': ['f', 'm'],
            },
        },
        'adj': {
            'gender': {
                'target_affix': [('FEM.a', 'f'), ('MASC.a', 'm')],
            },
            'number': {
                'target_affix': [('PL', 'pl'), ('SG', 'sg')],
            },
        },
        'n': {
            'gender': {
                'target_lemma': [('bicicleta1.1', 'f'), ('coche1.1', 'm'),
                                 ('carmelo1.1', 'm'), ('cosa1.1', 'f'),
                                 ('niña1.1', 'f'), ('manzana1.1', 'f'),
                                 ('luz1.1', 'f'), ('niño1.1', 'm'),
                                 ('camino1.1', 'm')],
            },
            'number': {
                'source_affix': [('PL', 'pl'), ('SG', 'sg')],
                'target_affix': [('PL', 'pl'), ('SG', 'sg')],
            },
        },
    }
    TestPairs = [
        # normal inputs
        ('^long1.1<adj>/largo1.1<adj>$ ^road1.1<n><SG>/camino1.1<n><m><SG>$',
         '^camino1.1<n><SG>$ ^largo1.1<adj><MASC_a><SG>$'),
        ('^long1.1<adj>/largo1.1<adj>$ ^road1.1<n><PL>/camino1.1<n><m><PL>$',
         '^camino1.1<n><PL>$ ^largo1.1<adj><MASC_a><PL>$'),
        ('^long1.1<adj>/largo1.1<adj>$ ^bike1.1<n><SG>/bicicleta1.1<n><f><SG>$',
         '^bicicleta1.1<n><SG>$ ^largo1.1<adj><FEM_a><SG>$'),
        ('^long1.1<adj>/largo1.1<adj>$ ^bike1.1<n><PL>/bicicleta1.1<n><f><PL>$',
         '^bicicleta1.1<n><PL>$ ^largo1.1<adj><FEM_a><PL>$'),
        # missing gender
        ('^long1.1<adj>/largo1.1<adj>$ ^road1.1<n><SG>/camino1.1<n><SG>$',
         '^camino1.1<n><SG>$ ^largo1.1<adj><MASC_a><SG>$'),
        ('^long1.1<adj>/largo1.1<adj>$ ^road1.1<n><PL>/camino1.1<n><PL>$',
         '^camino1.1<n><PL>$ ^largo1.1<adj><MASC_a><PL>$'),
        # missing number
        ('^long1.1<adj>/largo1.1<adj>$ ^road1.1<n>/camino1.1<n><m>$',
         '^camino1.1<n>$ ^largo1.1<adj><MASC_a><SG>$'),
        ('^long1.1<adj>/largo1.1<adj>$ ^bike1.1<n>/bicicleta1.1<n><f>$',
         '^bicicleta1.1<n>$ ^largo1.1<adj><FEM_a><SG>$'),
        # missing both
        ('^long1.1<adj>/largo1.1<adj>$ ^road1.1<n>/camino1.1<n>$',
         '^camino1.1<n>$ ^largo1.1<adj><MASC_a><SG>$'),
    ]

class UnmarkedDefault_WithBlanks(BaseTest, unittest.TestCase):
    RuleFile = 'unmarked_default.xml'
    Data = {
        None: {
            'gender': {
                'source_features': ['f', 'm'],
            },
        },
        'adj': {
            'gender': {
                'target_affix': [('FEM.a', 'f'), ('MASC.a', 'm')],
            },
            'number': {
                'target_affix': [('PL', 'pl')],
            },
        },
        'n': {
            'gender': {
                'target_lemma': [('bicicleta1.1', 'f'), ('coche1.1', 'm'),
                                 ('carmelo1.1', 'm'), ('cosa1.1', 'f'),
                                 ('niña1.1', 'f'), ('manzana1.1', 'f'),
                                 ('luz1.1', 'f'), ('niño1.1', 'm'),
                                 ('camino1.1', 'm')],
            },
            'number': {
                'source_affix': [('PL', 'pl')],
                'target_affix': [('PL', 'pl')],
            },
        },
    }
    TestPairs = [
        # normal inputs
        ('^long1.1<adj>/largo1.1<adj>$ ^road1.1<n><PL>/camino1.1<n><m><PL>$',
         '^camino1.1<n><PL>$ ^largo1.1<adj><MASC_a><PL>$'),
        ('^long1.1<adj>/largo1.1<adj>$ ^bike1.1<n><PL>/bicicleta1.1<n><f><PL>$',
         '^bicicleta1.1<n><PL>$ ^largo1.1<adj><FEM_a><PL>$'),
        # missing gender
        ('^long1.1<adj>/largo1.1<adj>$ ^road1.1<n><PL>/camino1.1<n><PL>$',
         '^camino1.1<n><PL>$ ^largo1.1<adj><MASC_a><PL>$'),
        # missing number
        ('^long1.1<adj>/largo1.1<adj>$ ^road1.1<n>/camino1.1<n><m>$',
         '^camino1.1<n>$ ^largo1.1<adj><MASC_a>$'),
        ('^long1.1<adj>/largo1.1<adj>$ ^bike1.1<n>/bicicleta1.1<n><f>$',
         '^bicicleta1.1<n>$ ^largo1.1<adj><FEM_a>$'),
        # missing both
        ('^long1.1<adj>/largo1.1<adj>$ ^road1.1<n>/camino1.1<n>$',
         '^camino1.1<n>$ ^largo1.1<adj><MASC_a>$'),
    ]

if __name__ == '__main__':
    unittest.main()
