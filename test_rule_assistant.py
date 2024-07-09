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
        self.assertListEqual([], report.errors)
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

class PatternFeature(BaseTest, unittest.TestCase):
    RuleFile = 'PatternFeature.xml'
    Data = {
        None: {
            'number': {
                'source_features': ['pl', 'sg'],
            },
        },
        'def': {},
        'n': {
            'definiteness': {
                'target_affix': [('DEF', 'defid')],
            },
            'number': {
                'target_affix': [('PL', 'pl'), ('SG', 'sg')],
            },
        },
    }
    TestPairs = [
        ('^A<def><defid><sg>/A<def><defid><sg>$ ^B<n>/B<n>$',
         '^B<n><SG><DEF>$'),
        ('^A<def><defid><pl>/A<def><defid><pl>$ ^B<n>/B<n>$',
         '^B<n><PL><DEF>$'),
        ('^A<def><indf><sg>/A<def><indf><sg>$ ^B<n>/B<n>$',
         '^A<def><indf><sg>$ ^B<n>$'),
        ('^A<def><indf><pl>/A<def><indf><pl>$ ^B<n>/B<n>$',
         '^A<def><indf><pl>$ ^B<n>$'),
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

class ReuseMacro(FrenchSpanishDefAdjNoun):
    TransferFile = 'reuse_macro.t1x'
    TestPairs = [
        ('^the1.1<def>/el1.1<def>$ ^long1.1<adj>/largo1.1<adj>$ ^road1.1<n><SG>/camino1.1<n><m><SG>$',
         '^hi<xyz>$^potato<def>$ ^camino1.1<n><SG>$ ^largo1.1<adj><MASC_a><SG>$'),
        ('^the1.<def>/el1.1<def>$ ^long1.1<adj>/largo1.1<adj>$ ^road1.1<n><PL>/camino1.1<n><m><PL>$',
         '^hi<xyz>$^potato<def>$ ^camino1.1<n><PL>$ ^largo1.1<adj><MASC_a><PL>$'),
        ('^long1.1<adj>/largo1.1<adj>$ ^road1.1<n><SG>/camino1.1<n><m><SG>$',
         '^largo1.1<adj>$ ^camino1.1<n><m><SG>$'),
        ('^long1.1<adj>/largo1.1<adj>$ ^road1.1<n><PL>/camino1.1<n><m><PL>$',
         '^largo1.1<adj>$ ^camino1.1<n><m><PL>$'),
    ]

# This test isn't done yet, so it doesn't actually run
class BantuTakwaneMeetto: # TODO
    RuleFile = 'Takwane-Meetto.xml'
    Data = {} # TODO
    TestPairs = [
        ('^ttengu1.1<n><7~8><7~8_sg>/cipo1.1<n><5~6><7~8_sg>$',
         '^cipo1.1<n><5~6_sg>$'),
        ('^ttengu1.1<n><7~8><7~8_pl>/cipo1.1<n><5~6><7~8_pl>$',
         '^cipo1.1<n><5~6_pl>$'),
        ('^lobwana1.1<n><1~2><1~2_sg>/lopwana1.1<n><1~2><1~2_sg>$',
         '^lopwana1.1<n><1~2_sg>$'),
        ('^lobwana1.1<n><1~2><1~2_pl>/lopwana1.1<n><1~2><1~2_pl>$',
         '^lopwana1.1<n><1~2_pl>$'),
        ('^ru1.1<n><3~4><3~4_sg>/uru1.1<n><3~4><3~4_sg>$',
         '^uru1.1<n><3~4_sg>$'),
        ('^ru1.1<n><3~4><3~4_pl>/uru1.1<n><3~4><3~4_pl>$',
         '^uru1.1<n><3~4_pl>$'),
        ('^aalago1.1<n><3~4><3~4_sg>/vaka1.1<n><5~6><3~4_sg>$',
         '^vaka1.1<n><5~6_sg>$'),
        ('^aalago1.1<n><3~4><3~4_pl>/vaka1.1<n><5~6><3~4_pl>$',
         '^vaka1.1<n><5~6_pl>$'),
        ('^lobwana1.1<n><1~2><1~2_sg>/lopwana1.1<n><1~2><1~2_sg>$ ^ngono1.1<adj><1~2>/nkani1.1<adj><1~2>$',
         '^lopwana1.1<n><1~2_sg>$ ^nkani1.1<adj><1~2_sg_a>$'),
        ('^lobwana1.1<n><1~2><1~2_pl>/lopwana1.1<n><1~2><1~2_pl>$ ^ngono1.1<adj><1~2>/nkani1.1<adj><1~2>$',
         '^lopwana1.1<n><1~2_pl>$ ^nkani1.1<adj><1~2_pl_a>$'),
        ('^hobo1.1<n><3~4><3~4_sg>/nika2.1<n><3~4><3~4_sg>$ ^ngono1.1<adj><3~4>/nkani1.1<adj><3~4>$',
         '^nika2.1<n><3~4_sg>$ ^nkani1.1<adj><3~4_sg_a>$'),
        ('^hobo1.1<n><3~4><3~4_pl>/nika2.1<n><3~4><3~4_pl>$ ^ngono1.1<adj><3~4>/nkani1.1<adj><3~4>$',
         '^nika2.1<n><3~4_pl>$ ^nkani1.1<adj><3~4_pl_a>$'),
        ('^aalago1.1<n><3~4><3~4_sg>/vaka1.1<n><5~6><3~4_sg>$ ^ngono1.1<adj><3~4>/nkani1.1<adj><3~4>$',
         '^vaka1.1<n><5~6_sg>$ ^nkani1.1<adj><5~6_sg_a>$'),
        ('^aalago1.1<n><3~4><3~4_pl>/vaka1.1<n><5~6><3~4_pl>$ ^ngono1.1<adj><3~4>/nkani1.1<adj><3~4>$',
         '^vaka1.1<n><5~6_pl>$ ^nkani1.1<adj><5~6_pl_a>$'),
    ]

'''
^mbuzi1.1<n><9~10_sg>$ ^puri1.1<n><9~10_sg>$
^guwo1.1<n><9~10_pl>$ ^kuwo1.1<n><9~10_pl>$
^somba1.1<n><9~10_sg>$ ^hopa1.1<n><9~10_sg>$
^somba1.1<n><9~10_pl>$ ^hopa1.1<n><9~10_pl>$

^mbuzi1.1<n><9~10_sg>$ ^ngono1.1<adj><9~10_sg_a>$
=>
^puri1.1<n><9~10_sg>$ ^nkani1.1<adj><9~10_sg_a>$

^mbuzi1.1<n><9~10_pl>$ ^ngono1.1<adj><9~10_pl_a>$
=>
^puri1.1<n><9~10_pl>$ ^nkani1.1<adj><9~10_pl_a>$

^enwi1.1<n><9~10_sg>$ ^rawo1.1<n><11~10_sg>$
^ngame1.1<n><5~6><5~6_sg>$ ^kame1.1<n><11~10_sg>$
^bwe1.1<n><5~6><5~6_sg>$ ^nika1.1<n><9~10_sg>$
^bwe1.1<n><5~6><5~6_pl>$ ^nika1.1<n><9~10_pl>$
'''

class GermanSwedishDefToAffix(BaseTest, unittest.TestCase):
    RuleFile = 'GermanSwedishDefToAffix.xml'
    Data = {
        None: {
            'definiteness': {'source_features': ['defid']},
            'gender': {'source_features': ['f', 'm', 'neut']},
            'number': {'source_features': ['pl', 'sg']},
        },
        'n': {
            'definiteness': {
                'target_affix': [('DEF_SG_N', 'defid'), ('DEF_SG_C', 'defid')],
            },
            'number': {
                'target_affix': [('DEF_SG_N', 'sg'), ('DEF_SG_C', 'sg')],
            },
        },
    }
    TestPairs = [
        ('^der1.1<def><m><sg><defid>/$ ^Meer1.1<n>/hav1.1<n>$',
         '^hav1.1<n><multiple-affix-for-defid-sg>$'),
    ]

class Ranking(BaseTest, unittest.TestCase):
    RuleFile = 'ranking.xml'
    Data = {
        None: {
            'gender': {'source_features': ['f', 'm']},
            'number': {'source_features': ['pl', 'sg']},
        },
        'def': {
            'gender': {
                'target_lemma': [('la', 'f'), ('lo', 'm')],
            },
            'number': {
                'target_lemma': [('la', 'sg'), ('lo', 'sg'), ('les', 'pl')],
            },
        },
        'n': {
            'gender': {
                'target_lemma': [('camisa', 'f'), ('libro', 'm')],
            },
            'number': {
                'source_affix': [('SG', 'sg'), ('PL', 'pl')],
                'target_affix': [('SG', 'sg'), ('PL', 'pl')],
            },
        },
    }
    TestPairs = [
        ('^the<def>/la<def>$ ^shirt<n><SG>/camisa<n><f><SG>$',
         '^la<def>$ ^camisa<n><SG>$'),
        ('^the<def>/la<def>$ ^shirt<n><PL>/camisa<n><f><PL>$',
         '^les<def>$ ^camisa<n><PL>$'),
        ('^the<def>/la<def>$ ^book<n><SG>/libro<n><m><SG>$',
         '^lo<def>$ ^libro<n><SG>$'),
        ('^the<def>/la<def>$ ^book<n><PL>/libro<n><m><PL>$',
         '^les<def>$ ^libro<n><PL>$'),
    ]

class DefSuffixToDeterminer(BaseTest, unittest.TestCase):
    RuleFile = 'insert_word.xml'
    Data = {
        'def': {
            'definiteness': {
                'target_lemma': [('thems', 'defid'), ('themp', 'defid'),
                                 ('thefs', 'defid'), ('thefp', 'defid')],
            },
            'gender': {
                'target_lemma': [('thems', 'm'), ('themp', 'm'),
                                 ('thefs', 'f'), ('thefp', 'f')],
            },
            'number': {
                'target_lemma': [('thems', 'sg'), ('themp', 'pl'),
                                 ('thefs', 'sg'), ('thefp', 'pl')],
            },
        },
        'n': {
            'definiteness': {
                'source_affix': [('DEF_SG', 'defid'), ('DEF_PL', 'defid')],
            },
            'gender': {
                'target_lemma': [('apartment', 'm'), ('table', 'f')],
            },
            'number': {
                'source_affix': [('DEF_SG', 'sg'), ('DEF_PL', 'pl')],
            },
        },
    }
    TestPairs = [
        ('^leilighet<n><DEF_SG>/apartment<n><m><DEF_SG>$',
         '^thems<def>$ ^apartment<n>$'),
        ('^leilighet<n><DEF_PL>/apartment<n><m><DEF_PL>$',
         '^themp<def>$ ^apartment<n>$'),
        ('^bord<n><DEF_SG>/table<n><f><DEF_SG>$',
         '^thefs<def>$ ^table<n>$'),
        ('^bord<n><DEF_PL>/table<n><f><DEF_PL>$',
         '^thefp<def>$ ^table<n>$'),
    ]

if __name__ == '__main__':
    unittest.main()
