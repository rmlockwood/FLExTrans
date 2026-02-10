#!/usr/bin/env python3

import unittest
import os
import shutil
import importlib
import subprocess

ParentFolder = os.path.dirname(__file__)
DataFolder = os.path.join(ParentFolder, 'Rule Assistant')
TestFolder = os.path.join(ParentFolder, 'RuleAssistantTests')
DevFolder = os.path.join(ParentFolder, '..')
LibFolder = os.path.join(DevFolder, '..\\Lib')
script = 'CreateApertiumRules.py'
with open(os.path.join(LibFolder, script)) as fin:
    with open(os.path.join(TestFolder, script), 'w') as fout:
        fout.write(fin.read().replace('import Utils', 'from . import Utils'))

from RuleAssistantTests import CreateApertiumRules

class Reporter:
    def __init__(self):
        self.infos = []
        self.errors = []
    def Info(self, *args):
        self.infos.append(args)
    def Error(self, *args):
        self.errors.append(args)

class BaseTest(unittest.TestCase):
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
            'number': {
                'source_affix': [('PL', 'pl'), ('SG', 'sg')],
                'target_affix': [('PL', 'pl'), ('SG', 'sg')],
            },
        },
    }
    RuleFile = 'Ex3_Adj-Noun.xml'
    RuleNumber = None
    RuleCount = 1
    TransferFile = None
    TestPairs = []

    def runTest(self):
        prefix = os.path.join(TestFolder, self.__class__.__name__)
        self.t1xFile = prefix + '.t1x'
        binFile = prefix + '.bin'

        if os.path.exists(self.t1xFile):
            os.remove(self.t1xFile)
        if self.TransferFile is not None:
            shutil.copy(os.path.join(DataFolder, self.TransferFile), self.t1xFile)
        CreateApertiumRules.Utils.DATA = self.Data

        # Create rules (with debug output on failure)
        report = Reporter()
        path = os.path.join(DataFolder, self.RuleFile)
        result = CreateApertiumRules.CreateRules(
            'source', 'target', report, None, path, self.t1xFile, self.RuleNumber,
        )
        if not result:
            print('CreateRules returned falsy result:', result)
            print('Reporter.infos:')
            for i in report.infos:
                print('  ', i)
            print('Reporter.errors:')
            for e in report.errors:
                print('  ', e)
        self.assertTrue(result)
        self.assertListEqual([], report.errors)
        self.assertIn((f'Added {self.RuleCount} rule(s) from {path}.',),
                      report.infos)

        if os.name == 'posix':
            # Validate rules
            validate = subprocess.run(
                ['apertium-validate-transfer', self.t1xFile],
                text=True, check=False, capture_output=True,
            )
            self.assertEqual(0, validate.returncode)
            # We don't install apertium-validate-transfer with FLExTrans,
            # so don't run this check on Windows.

        comp_cmd = 'apertium-preprocess-transfer'
        run_cmd = 'apertium-transfer'
        if os.name == 'nt':
            comp_cmd = f'InstallerResources\\Apertium4Windows\\{comp_cmd}.exe'
            run_cmd = f'InstallerResources\\Apertium4Windows\\{run_cmd}.exe'

        # Compile rules
        preproc = subprocess.run(
            [comp_cmd, self.t1xFile, binFile],
            text=True, check=False, capture_output=True,
        )
        if preproc.returncode != 0:
            print(preproc.stdout)
            print(preproc.stderr)
        self.assertEqual(0, preproc.returncode)

        # Apply rules
        proc = subprocess.Popen(
            [run_cmd, '-b', '-z', self.t1xFile, binFile],
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

        CreateApertiumRules.Utils.DATA = {}

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

class SpanishFrenchRev2(BaseTest, unittest.TestCase):
    RuleCount = 5
    Data = {
        None: {
            'number': {
                'source_features': ['pl', 'sg']},
            'gender': {
                'source_features': ['?', 'f', 'm']}},
        'indf': {
            'number': {
                'target_lemma': [('des1.1', 'pl'), ('un1.1', 'sg'), ('une1.1', 'sg')]},
            'gender': {
                'target_lemma': [('un1.1', 'm'), ('une1.1', 'f')]}},
        'def': {
            'number': {
                'target_lemma': [('la1.1', 'sg'), ('le1.1', 'sg'), ('les1.1', 'pl')]},
            'gender': {
                'target_lemma': [('la1.1', 'f'), ('le1.1', 'm')]}},
        'adj': {
            'number': {
                'target_affix': [('PL3', 'pl')]},
            'gender': {
                'target_affix': [('FEM.a', 'f')]}},
        'n': {
            'number': {
                'source_affix': [('PL', 'pl')], 'target_affix': [('PL', 'pl')]},
            'gender': {
                'target_lemma': [('voiture1.1', 'f'), ('train1.1', 'm'), ('garçon1.1', 'm'), ('pomme1.1', 'f'), ('poisson1.1', 'm'), ('œuf1.1', 'm'), ('fille1.1', 'f'), ('chose1.1', 'f'), ('vélo1.1', 'm'), ('bonbon1.1', 'm'), ('route1.1', 'f')]}}}
    RuleFile = 'SpanishFrenchRev2.xml'
    TestPairs = [
        ('^un1.1<indf><MASC><PL>/un1.1<indf><m><sg><MASC><PL>$ ^coche1.1<n><m><PL>/voiture1.1<n><f><PL>$ ^pequeño1.1<adj><MASC_a><PL>/petit1.1<adj><MASC_a><PL>$',
         '^des1.1<indf>$ ^petit1.1<adj><FEM_a><PL3>$ ^voiture1.1<n><PL>$'),
        ('^Los1.1<def><m><pl>/Les1.1<def><pl>$ ^niño1.1<n><m><PL>/garçon1.1<n><m><PL>$ ^pequeño1.1<adj><MASC_a><PL>/petit1.1<adj><MASC_a><PL>$',
         '^Les1.1<def>$ ^petit1.1<adj><PL3>$ ^garçon1.1<n><PL>$'),
        ('^Las1.1<def><f><pl>/Les1.1<def><pl>$ ^niña1.1<n><f><PL>/fille1.1<n><f><PL>$ ^pequeño1.1<adj><FEM_a><PL>/petit1.1<adj><FEM_a><PL3>$',
         '^Les1.1<def>$ ^petit1.1<adj><FEM_a><PL3>$ ^fille1.1<n><PL>$'),
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

@unittest.skip('Disabling functionality per #661')
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
                'target_lemma': [('lo', 'defid'), ('la', 'defid')],
            },
            'gender': {
                'target_lemma': [('lo', 'm'), ('la', 'f')],
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
                'target_affix': [('PL', 'pl')],
            },
        },
    }
    TestPairs = [
        ('^leilighet<n><DEF_SG>/apartment<n><m><DEF_SG>$',
         '^lo<def>$ ^apartment<n>$'),
        ('^leilighet<n><DEF_PL>/apartment<n><m><DEF_PL>$',
         '^lo<def>$ ^apartment<n><PL>$'),
        ('^bord<n><DEF_SG>/table<n><f><DEF_SG>$',
         '^la<def>$ ^table<n>$'),
        ('^bord<n><DEF_PL>/table<n><f><DEF_PL>$',
         '^la<def>$ ^table<n><PL>$'),
    ]

class GermanEnglishDoubleDefault(BaseTest, unittest.TestCase):
    RuleFile = 'GermanEnglishDoubleDefault.xml'
    Data = {
        'n': {
            'case': {
                'source_affix': [('NOM', 'nom'), ('GEN', 'gen'), ('ACC', 'acc')],
                'target_affix': [('GEN', 'gen')],
            },
            'number': {
                'source_affix': [('SG', 'sg'), ('PL', 'pl')],
                'target_affix': [('PL', 'pl')],
            },
        },
    }
    TestPairs = [
        ('^hund<n><NOM><SG>/dog<n><NOM><SG>$', '^dog<n>$'),
        ('^hund<n><NOM><PL>/dog<n><NOM><PL>$', '^dog<n><PL>$'),
        ('^hund<n><ACC><SG>/dog<n><ACC><SG>$', '^dog<n><no-affix-for-sg-acc>$'),
        ('^hund<n><ACC><PL>/dog<n><ACC><PL>$', '^dog<n><no-affix-for-pl-acc>$'),
        ('^hund<n><GEN><SG>/dog<n><GEN><SG>$', '^dog<n><GEN>$'),
        ('^hund<n><GEN><PL>/dog<n><GEN><PL>$', '^dog<n><no-affix-for-pl-gen>$'),
    ]

class SplitBantu(BaseTest, unittest.TestCase):
    RuleFile = 'SplitBantu.xml'
    RuleCount = 2
    Data = {
        None: {
            'BantuSG': {
                'source_features': ['1', '3', '5'],
            },
            'BantuPL': {
                'source_features': ['2', '4', '6'],
            },
        },
        'adj': {
            'BantuSG': {
                'target_affix': [('1A', '1'), ('5A', '5'), ('7A', '7'),
                                 ('14A', '14')],
            },
            'BantuPL': {
                'target_affix': [('2A', '2'), ('6A', '6'), ('8A', '8')],
            },
        },
        'n': {
            'BantuSG': {
                'source_affix': [('1P', '1'), ('3P', '3'), ('5P', '5')],
                'target_affix': [('1P', '1'), ('5P', '5'), ('7P', '7'),
                                 ('14P', '14')],
                'target_lemma': [('X', '1'), ('Y', '5'), ('Z', '7'),
                                 ('S', '14')],
            },
            'BantuPL': {
                'source_affix': [('2P', '2'), ('4P', '4'), ('6P', '6')],
                'target_affix': [('2P', '2'), ('6P', '6'), ('8P', '8')],
                'target_lemma': [('X', '2'), ('Y', '6'), ('Z', '8'),
                                 ('S', 'NApl')],
            },
        },
    }
    TestPairs = [
        ('^N12<n><1><2><1P>/X<n><1><2><1P>$', '^X<n><1P>$'),
        ('^N12<n><1><2><2P>/X<n><1><2><2P>$', '^X<n><2P>$'),
        ('^N34<n><3><4><3P>/Y<n><5><6><3P>$', '^Y<n><5P>$'),
        ('^N34<n><3><4><4P>/Y<n><5><6><4P>$', '^Y<n><6P>$'),
        ('^N56<n><5><6><5P>/Z<n><7><7><5P>$', '^Z<n><7P>$'),
        ('^N56<n><5><6><6P>/Z<n><7><8><6P>$', '^Z<n><8P>$'),
        ('^N12<n><1><2><1P>/Y<n><5><6><1P>$', '^Y<n><5P>$'),
        ('^N12<n><1><2><2P>/Y<n><5><6><2P>$', '^Y<n><6P>$'),
        ('^N34<n><3><4><3P>/Z<n><7><8><3P>$', '^Z<n><7P>$'),
        ('^N34<n><3><4><4P>/Z<n><7><8><4P>$', '^Z<n><8P>$'),

        # singletons
        ('^N12<n><1><2><1P>/S<n><14><NApl><1P>$', '^S<n><14P>$'),
        ('^N12<n><1><2><2P>/S<n><14><NApl><2P>$', '^S<n><14P>$'),

        # adjectives
        ('^N12<n><1><2><1P>/X<n><1><2><1P>$ ^J<adj><1A>/K<adj><1A>$',
         '^X<n><1P>$ ^K<adj><1A>$'),
        ('^N12<n><1><2><2P>/X<n><1><2><2P>$ ^J<adj><1A>/K<adj><2A>$',
         '^X<n><2P>$ ^K<adj><2A>$'),
        ('^N34<n><3><4><3P>/Y<n><5><6><3P>$ ^J<adj><1A>/K<adj><3A>$',
         '^Y<n><5P>$ ^K<adj><5A>$'),
        ('^N34<n><3><4><4P>/Y<n><5><6><4P>$ ^J<adj><1A>/K<adj><4A>$',
         '^Y<n><6P>$ ^K<adj><6A>$'),
        ('^N56<n><5><6><5P>/Z<n><7><7><5P>$ ^J<adj><1A>/K<adj><5A>$',
         '^Z<n><7P>$ ^K<adj><7A>$'),
        ('^N56<n><5><6><6P>/Z<n><7><8><6P>$ ^J<adj><1A>/K<adj><6A>$',
         '^Z<n><8P>$ ^K<adj><8A>$'),
        ('^N12<n><1><2><1P>/Y<n><5><6><1P>$ ^J<adj><1A>/K<adj><1A>$',
         '^Y<n><5P>$ ^K<adj><5A>$'),
        ('^N12<n><1><2><2P>/Y<n><5><6><2P>$ ^J<adj><1A>/K<adj><2A>$',
         '^Y<n><6P>$ ^K<adj><6A>$'),
        ('^N34<n><3><4><3P>/Z<n><7><8><3P>$ ^J<adj><1A>/K<adj><3A>$',
         '^Z<n><7P>$ ^K<adj><7A>$'),
        ('^N34<n><3><4><4P>/Z<n><7><8><4P>$ ^J<adj><1A>/K<adj><4A>$',
         '^Z<n><8P>$ ^K<adj><8A>$'),

        # singletons with adjectives
        ('^N12<n><1><2><1P>/S<n><14><NApl><1P>$ ^J<adj><1A>/K<adj><1A>$',
         '^S<n><14P>$ ^K<adj><14A>$'),
        ('^N12<n><1><2><2P>/S<n><14><NApl><2P>$ ^J<adj><1A>/K<adj><2A>$',
         '^S<n><14P>$ ^K<adj><14A>$'),
    ]

class EnglishGermanTripleRanking(BaseTest, unittest.TestCase):
    RuleFile = 'EnglishGermanTripleRanking.xml'
    Data = {
        'def': {
            'case': {
                'target_lemma': [('den1.1', 'acc'), ('die1.4', 'dat'),
                                 ('der1.4', 'gen'),
                                 ('die1.3', 'acc'), ('den1.2', 'acc'),
                                 ('das1.2', 'acc'), ('der1.2', 'dat'),
                                 ('dem1.1', 'dat'), ('dem1.2', 'dat'),
                                 ('der1.3', 'gen'), ('des1.2', 'gen'),
                                 ('des1.1', 'gen')],
            },
            'gender': {
                'target_lemma': [('die1.3', 'f'), ('den1.2', 'm'),
                                 ('das1.2', 'nt'), ('der1.2', 'f'),
                                 ('dem1.1', 'm'), ('dem1.2', 'nt'),
                                 ('der1.3', 'f'), ('des1.2', 'm'),
                                 ('des1.1', 'nt'), ('die1.2', 'f'),
                                 ('der1.1', 'm'), ('das1.1', 'nt')],
            },
            'number': {
                'target_lemma': [('den1.1', 'pl'), ('die1.4', 'pl'),
                                 ('der1.4', 'pl'), ('die1.1', 'pl'),
                                 ('die1.3', 'sg'), ('den1.2', 'sg'),
                                 ('das1.2', 'sg'), ('der1.2', 'sg'),
                                 ('dem1.1', 'sg'), ('dem1.2', 'sg'),
                                 ('der1.3', 'sg'), ('des1.2', 'sg'),
                                 ('des1.1', 'sg'), ('die1.2', 'sg'),
                                 ('der1.1', 'sg'), ('das1.1', 'sg')],
            },
        },
        'n': {
            'case': {
                'source_affix': [('ACC', 'acc'), ('DAT', 'dat'), ('GEN', 'gen'),
                                 ('ACC_PL', 'acc'), ('DAT_PL', 'dat'),
                                 ('GEN_PL', 'gen')],
                'target_affix': [('ACC', 'acc'), ('DAT', 'dat'), ('GEN', 'gen'),
                                 ('ACC_PL', 'acc'), ('DAT_PL', 'dat'),
                                 ('GEN_PL', 'gen')],
            },
            'gender': {
                'target_lemma': [('Nm', 'm'), ('Nf', 'f'), ('Nn', 'nt')],
            },
            'number': {
                'source_affix': [('ACC_PL', 'pl'), ('DAT_PL', 'pl'),
                                 ('GEN_PL', 'pl'), ('PL', 'pl')],
                'target_affix': [('ACC_PL', 'pl'), ('DAT_PL', 'pl'),
                                 ('GEN_PL', 'pl'), ('PL', 'pl')],
            },
        },
    }
    TestPairs = [
        ('^the<def>/the<def>$ ^thing1<n><m>/Nm<n><m>$',
         '^der1.1<def>$ ^Nm<n>$'),
        ('^the<def>/the<def>$ ^thing2<n><f>/Nf<n><f>$',
         '^die1.2<def>$ ^Nf<n>$'),
        ('^the<def>/the<def>$ ^thing3<n><nt>/Nn<n><nt>$',
         '^das1.1<def>$ ^Nn<n>$'),
        ('^the<def>/the<def>$ ^thing1<n><m><PL>/Nm<n><m><PL>$',
         '^die1.1<def>$ ^Nm<n><PL>$'),
        ('^the<def>/the<def>$ ^thing2<n><f><PL>/Nf<n><f><PL>$',
         '^die1.1<def>$ ^Nf<n><PL>$'),
        ('^the<def>/the<def>$ ^thing3<n><nt><PL>/Nn<n><nt><PL>$',
         '^die1.1<def>$ ^Nn<n><PL>$'),

        ('^the<def>/the<def>$ ^thing1<n><m><ACC>/Nm<n><m><ACC>$',
         '^den1.2<def>$ ^Nm<n><ACC>$'),
        ('^the<def>/the<def>$ ^thing2<n><f>/Nf<n><f><ACC>$',
         '^die1.3<def>$ ^Nf<n><ACC>$'),
        ('^the<def>/the<def>$ ^thing3<n><nt><ACC>/Nn<n><nt><ACC>$',
         '^das1.2<def>$ ^Nn<n><ACC>$'),
        ('^the<def>/the<def>$ ^thing1<n><m><ACC_PL>/Nm<n><m><ACC_PL>$',
         '^den1.1<def>$ ^Nm<n><ACC_PL>$'),
        ('^the<def>/the<def>$ ^thing2<n><f><ACC_PL>/Nf<n><f><ACC_PL>$',
         '^den1.1<def>$ ^Nf<n><ACC_PL>$'),
        ('^the<def>/the<def>$ ^thing3<n><nt><ACC_PL>/Nn<n><nt><ACC_PL>$',
         '^den1.1<def>$ ^Nn<n><ACC_PL>$'),

        ('^the<def>/the<def>$ ^thing1<n><m><DAT>/Nm<n><m><DAT>$',
         '^dem1.1<def>$ ^Nm<n><DAT>$'),
        ('^the<def>/the<def>$ ^thing2<n><f>/Nf<n><f><DAT>$',
         '^der1.2<def>$ ^Nf<n><DAT>$'),
        ('^the<def>/the<def>$ ^thing3<n><nt><DAT>/Nn<n><nt><DAT>$',
         '^dem1.2<def>$ ^Nn<n><DAT>$'),
        ('^the<def>/the<def>$ ^thing1<n><m><DAT_PL>/Nm<n><m><DAT_PL>$',
         '^die1.4<def>$ ^Nm<n><DAT_PL>$'),
        ('^the<def>/the<def>$ ^thing2<n><f><DAT_PL>/Nf<n><f><DAT_PL>$',
         '^die1.4<def>$ ^Nf<n><DAT_PL>$'),
        ('^the<def>/the<def>$ ^thing3<n><nt><DAT_PL>/Nn<n><nt><DAT_PL>$',
         '^die1.4<def>$ ^Nn<n><DAT_PL>$'),

        ('^the<def>/the<def>$ ^thing1<n><m><GEN>/Nm<n><m><GEN>$',
         '^des1.2<def>$ ^Nm<n><GEN>$'),
        ('^the<def>/the<def>$ ^thing2<n><f>/Nf<n><f><GEN>$',
         '^der1.3<def>$ ^Nf<n><GEN>$'),
        ('^the<def>/the<def>$ ^thing3<n><nt><GEN>/Nn<n><nt><GEN>$',
         '^des1.1<def>$ ^Nn<n><GEN>$'),
        ('^the<def>/the<def>$ ^thing1<n><m><GEN_PL>/Nm<n><m><GEN_PL>$',
         '^der1.4<def>$ ^Nm<n><GEN_PL>$'),
        ('^the<def>/the<def>$ ^thing2<n><f><GEN_PL>/Nf<n><f><GEN_PL>$',
         '^der1.4<def>$ ^Nf<n><GEN_PL>$'),
        ('^the<def>/the<def>$ ^thing3<n><nt><GEN_PL>/Nn<n><nt><GEN_PL>$',
         '^der1.4<def>$ ^Nn<n><GEN_PL>$'),
    ]

class EnglishGermanTripleRankingPartialDefault(BaseTest, unittest.TestCase):
    RuleFile = 'EnglishGermanTripleRankingPartialDefault.xml'
    RuleCount = 3
    Data = {
        'adj': {
            'case': {
                'target_affix': [('ADJ_AGR_F_ACC', 'acc'),
                                 ('ADJ_AGR_M_ACC', 'acc'),
                                 ('ADJ_AGR_N_ACC', 'acc'),
                                 ('ADJ_AGR_DAT', 'dat'), ('ADJ_AGR_GEN', 'gen'),
                                 ('ADJ_AGR', 'nom')],
            },
            'gender': {
                'target_affix': [('ADJ_AGR_F_ACC', 'f'),
                                 ('ADJ_AGR_M_ACC', 'm'),
                                 ('ADJ_AGR_N_ACC', 'nt')],
            },
            'number': {
                'target_affix': [('ADJ_AGR_PL', 'pl'), ('ADJ_AGR_F_ACC', 'sg'),
                                 ('ADJ_AGR_M_ACC', 'sg'),
                                 ('ADJ_AGR_N_ACC', 'sg'),
                                 ('ADJ_AGR_DAT', 'sg'), ('ADJ_AGR_GEN', 'sg'),
                                 ('ADJ_AGR', 'sg')],
            },
        },
        'def': {
            'case': {
                'target_lemma': [('den1.1', 'acc'), ('die1.4', 'dat'),
                                 ('der1.4', 'gen'),
                                 ('die1.3', 'acc'), ('den1.2', 'acc'),
                                 ('das1.2', 'acc'), ('der1.2', 'dat'),
                                 ('dem1.1', 'dat'), ('dem1.2', 'dat'),
                                 ('der1.3', 'gen'), ('des1.2', 'gen'),
                                 ('des1.1', 'gen')],
            },
            'gender': {
                'target_lemma': [('die1.3', 'f'), ('den1.2', 'm'),
                                 ('das1.2', 'nt'), ('der1.2', 'f'),
                                 ('dem1.1', 'm'), ('dem1.2', 'nt'),
                                 ('der1.3', 'f'), ('des1.2', 'm'),
                                 ('des1.1', 'nt'), ('die1.2', 'f'),
                                 ('der1.1', 'm'), ('das1.1', 'nt')],
            },
            'number': {
                'target_lemma': [('den1.1', 'pl'), ('die1.4', 'pl'),
                                 ('der1.4', 'pl'), ('die1.1', 'pl'),
                                 ('die1.3', 'sg'), ('den1.2', 'sg'),
                                 ('das1.2', 'sg'), ('der1.2', 'sg'),
                                 ('dem1.1', 'sg'), ('dem1.2', 'sg'),
                                 ('der1.3', 'sg'), ('des1.2', 'sg'),
                                 ('des1.1', 'sg'), ('die1.2', 'sg'),
                                 ('der1.1', 'sg'), ('das1.1', 'sg')],
            },
        },
        'n': {
            'case': {
                'source_affix': [('ACC', 'acc'), ('DAT', 'dat'), ('GEN', 'gen'),
                                 ('ACC_PL', 'acc'), ('DAT_PL', 'dat'),
                                 ('GEN_PL', 'gen')],
                'target_affix': [('ACC_SG', 'acc'), ('DAT_SG', 'dat'),
                                 ('GEN_F_SG', 'gen'), ('GEN_M_SG', 'gen'),
                                 ('GEN_N_SG', 'gen')],
            },
            'gender': {
                'target_lemma': [('Nm', 'm'), ('Nf', 'f'), ('Nn', 'nt')],
                'target_affix': [('GEN_F_SG', 'f'), ('GEN_M_SG', 'm'),
                                 ('GEN_N_SG', 'nt')],
            },
            'number': {
                'source_affix': [('ACC_PL', 'pl'), ('DAT_PL', 'pl'),
                                 ('GEN_PL', 'pl'), ('PL', 'pl')],
                'target_affix': [('ACC_SG', 'sg'), ('DAT_SG', 'sg'),
                                 ('GEN_F_SG', 'sg'), ('GEN_M_SG', 'sg'),
                                 ('GEN_N_SG', 'sg'), ('PL', 'pl')],
            },
        },
    }
    TestPairs = [
        ('^the<def>/the<def>$ ^thing1<n><m>/Nm<n><m>$',
         '^der1.1<def>$ ^Nm<n>$'),
        ('^the<def>/the<def>$ ^thing2<n><f>/Nf<n><f>$',
         '^die1.2<def>$ ^Nf<n>$'),
        ('^the<def>/the<def>$ ^thing3<n><nt>/Nn<n><nt>$',
         '^das1.1<def>$ ^Nn<n>$'),
        ('^the<def>/the<def>$ ^thing1<n><m><PL>/Nm<n><m><PL>$',
         '^die1.1<def>$ ^Nm<n><PL>$'),
        ('^the<def>/the<def>$ ^thing2<n><f><PL>/Nf<n><f><PL>$',
         '^die1.1<def>$ ^Nf<n><PL>$'),
        ('^the<def>/the<def>$ ^thing3<n><nt><PL>/Nn<n><nt><PL>$',
         '^die1.1<def>$ ^Nn<n><PL>$'),

        ('^the<def>/the<def>$ ^thing1<n><m><ACC>/Nm<n><m><ACC>$',
         '^den1.2<def>$ ^Nm<n><ACC_SG>$'),
        ('^the<def>/the<def>$ ^thing2<n><f>/Nf<n><f><ACC>$',
         '^die1.3<def>$ ^Nf<n><ACC_SG>$'),
        ('^the<def>/the<def>$ ^thing3<n><nt><ACC>/Nn<n><nt><ACC>$',
         '^das1.2<def>$ ^Nn<n><ACC_SG>$'),
        ('^the<def>/the<def>$ ^thing1<n><m><ACC_PL>/Nm<n><m><ACC_PL>$',
         '^den1.1<def>$ ^Nm<n><PL>$'),
        ('^the<def>/the<def>$ ^thing2<n><f><ACC_PL>/Nf<n><f><ACC_PL>$',
         '^den1.1<def>$ ^Nf<n><PL>$'),
        ('^the<def>/the<def>$ ^thing3<n><nt><ACC_PL>/Nn<n><nt><ACC_PL>$',
         '^den1.1<def>$ ^Nn<n><PL>$'),

        ('^the<def>/the<def>$ ^thing1<n><m><DAT>/Nm<n><m><DAT>$',
         '^dem1.1<def>$ ^Nm<n><DAT_SG>$'),
        ('^the<def>/the<def>$ ^thing2<n><f>/Nf<n><f><DAT>$',
         '^der1.2<def>$ ^Nf<n><DAT_SG>$'),
        ('^the<def>/the<def>$ ^thing3<n><nt><DAT>/Nn<n><nt><DAT>$',
         '^dem1.2<def>$ ^Nn<n><DAT_SG>$'),
        ('^the<def>/the<def>$ ^thing1<n><m><DAT_PL>/Nm<n><m><DAT_PL>$',
         '^die1.4<def>$ ^Nm<n><PL>$'),
        ('^the<def>/the<def>$ ^thing2<n><f><DAT_PL>/Nf<n><f><DAT_PL>$',
         '^die1.4<def>$ ^Nf<n><PL>$'),
        ('^the<def>/the<def>$ ^thing3<n><nt><DAT_PL>/Nn<n><nt><DAT_PL>$',
         '^die1.4<def>$ ^Nn<n><PL>$'),

        ('^the<def>/the<def>$ ^thing1<n><m><GEN>/Nm<n><m><GEN>$',
         '^des1.2<def>$ ^Nm<n><GEN_M_SG>$'),
        ('^the<def>/the<def>$ ^thing2<n><f>/Nf<n><f><GEN>$',
         '^der1.3<def>$ ^Nf<n><GEN_F_SG>$'),
        ('^the<def>/the<def>$ ^thing3<n><nt><GEN>/Nn<n><nt><GEN>$',
         '^des1.1<def>$ ^Nn<n><GEN_N_SG>$'),
        ('^the<def>/the<def>$ ^thing1<n><m><GEN_PL>/Nm<n><m><GEN_PL>$',
         '^der1.4<def>$ ^Nm<n><PL>$'),
        ('^the<def>/the<def>$ ^thing2<n><f><GEN_PL>/Nf<n><f><GEN_PL>$',
         '^der1.4<def>$ ^Nf<n><PL>$'),
        ('^the<def>/the<def>$ ^thing3<n><nt><GEN_PL>/Nn<n><nt><GEN_PL>$',
         '^der1.4<def>$ ^Nn<n><PL>$'),

        ('^big<adj>/big<adj>$ ^thing1<n><m>/Nm<n><m>$',
         '^big<adj><ADJ_AGR>$ ^Nm<n>$'),
        ('^big<adj>/big<adj>$ ^thing2<n><f>/Nf<n><f>$',
         '^big<adj><ADJ_AGR>$ ^Nf<n>$'),
        ('^big<adj>/big<adj>$ ^thing3<n><nt>/Nn<n><nt>$',
         '^big<adj><ADJ_AGR>$ ^Nn<n>$'),
        ('^big<adj>/big<adj>$ ^thing1<n><m><PL>/Nm<n><m><PL>$',
         '^big<adj><ADJ_AGR_PL>$ ^Nm<n><PL>$'),
        ('^big<adj>/big<adj>$ ^thing2<n><f><PL>/Nf<n><f><PL>$',
         '^big<adj><ADJ_AGR_PL>$ ^Nf<n><PL>$'),
        ('^big<adj>/big<adj>$ ^thing3<n><nt><PL>/Nn<n><nt><PL>$',
         '^big<adj><ADJ_AGR_PL>$ ^Nn<n><PL>$'),

        ('^big<adj>/big<adj>$ ^thing1<n><m><ACC>/Nm<n><m><ACC>$',
         '^big<adj><ADJ_AGR_M_ACC>$ ^Nm<n><ACC_SG>$'),
        ('^big<adj>/big<adj>$ ^thing2<n><f>/Nf<n><f><ACC>$',
         '^big<adj><ADJ_AGR_F_ACC>$ ^Nf<n><ACC_SG>$'),
        ('^big<adj>/big<adj>$ ^thing3<n><nt><ACC>/Nn<n><nt><ACC>$',
         '^big<adj><ADJ_AGR_N_ACC>$ ^Nn<n><ACC_SG>$'),
        ('^big<adj>/big<adj>$ ^thing1<n><m><ACC_PL>/Nm<n><m><ACC_PL>$',
         '^big<adj><ADJ_AGR_PL>$ ^Nm<n><PL>$'),
        ('^big<adj>/big<adj>$ ^thing2<n><f><ACC_PL>/Nf<n><f><ACC_PL>$',
         '^big<adj><ADJ_AGR_PL>$ ^Nf<n><PL>$'),
        ('^big<adj>/big<adj>$ ^thing3<n><nt><ACC_PL>/Nn<n><nt><ACC_PL>$',
         '^big<adj><ADJ_AGR_PL>$ ^Nn<n><PL>$'),
    ]

def Rule2Index(t1xFile: str):
    from xml.etree import ElementTree as ET
    root = ET.parse(t1xFile).getroot()
    dct = {}
    for i, rule in enumerate(root.iter('rule')):
        dct[rule.get('comment')] = i
    return dct

class InsertBeforeOldRules(GermanEnglishDoubleDefault):
    TransferFile = 'OldRules.t1x'

    def runTest(self):
        super().runTest()
        rules = Rule2Index(self.t1xFile)
        self.assertIn('def n simple (123)', rules)
        self.assertLess(rules['def n simple'], rules['def n simple (123)'])

class DeleteOldRules(GermanEnglishDoubleDefault):
    RuleFile = 'GermanEnglishDoubleDefaultOverwrite.xml'
    TransferFile = 'OldRules.t1x'

    def runTest(self):
        super().runTest()
        rules = Rule2Index(self.t1xFile)
        self.assertNotIn('def n simple (123)', rules)

if __name__ == '__main__':
    unittest.main()
