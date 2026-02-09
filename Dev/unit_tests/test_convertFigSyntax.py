import unittest
import sys
import os

# Add the path to the lib directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../lib')))
sys.path.append('C:\\Program Files\\SIL\\FieldWorks 9\\')
sys.path.append('C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\')

# Import and initialize pythonnet
import clr
clr.AddReference("System")
clr.AddReference("SIL.LCModel")
clr.AddReference("SIL.LCModel.Core")

from ChapterSelection import convertFigSyntax

class TestConvertFigSyntax(unittest.TestCase):

    def test_convert_fig_new_format(self):
        input_str = (
            '\\p Ngaxusunga \\fig Xailongga li suxungunoa|alt="John writing on Patmos" '
            'src="PD-272bw.tif" size="span" loc="Revelation 1:1" copy="Art" ref="1:1,3"\\fig*'
        )
        expected_output = (
            '\\p Ngaxusunga \\fig Xailongga li suxungunoa|alt="John writing on Patmos" '
            'src="PD-272bw.tif" size="span" loc="Revelation 1:1" copy="Art" ref="1:1,3"\\fig*'
        )
        self.assertEqual(convertFigSyntax(input_str), expected_output)

    def test_convert_fig_old_format(self):
        input_str = (
            '\\fig TenCommandmentsPicture|tablets.jpg|large|top|© 2020 The Company|The Ten Commandments|20:1\\fig*'
        )
        expected_output = (
            '\\fig The Ten Commandments|alt="TenCommandmentsPicture" src="tablets.jpg" '
            'size="large" loc="top" copy="© 2020 The Company" ref="20:1"\\fig*'
        )
        self.assertEqual(convertFigSyntax(input_str), expected_output)

    def test_convert_fig_quails(self):
        input_str = (
            '\\v 13 Tsay tardimi atska codornizkuna Israel runakunapa campamentunman ratapäkurqan. Patsa '
            'wararkuptinnami campamentu nawpankunapapis yoraqayparaq shulyashqa warämurqan.\\x + \\xo 16.12-13 '
            '\\xt Núm. 11.31-32.\\x*\\fig Quails on the ground|HK00065B.TIF|col|Exodus 16.13|HK|Codornizkuna|16.13\\fig*'
        )
        expected_output = (
            '\\v 13 Tsay tardimi atska codornizkuna Israel runakunapa campamentunman ratapäkurqan. Patsa '
            'wararkuptinnami campamentu nawpankunapapis yoraqayparaq shulyashqa warämurqan.\\x + \\xo 16.12-13 '
            '\\xt Núm. 11.31-32.\\x*\\fig Codornizkuna|alt="Quails on the ground" src="HK00065B.TIF" '
            'size="col" loc="Exodus 16.13" copy="HK" ref="16.13"\\fig*'
        )
        self.assertEqual(convertFigSyntax(input_str), expected_output)

    def test_convert_fig_candelestick(self):
        input_str = (
            '\\v 36 Waytankunapis y rikrankunapis tsay piëzala kanqa. Lapanpis qori pürulapita martilluwan takaylapa '
            'rurashqa kanqa.\\fig Candelestick of Tabernacle|lb00277B.TIF|col|Exo. 25.31-39|HK|Candelabru|25.31\\fig*'
        )
        expected_output = (
            '\\v 36 Waytankunapis y rikrankunapis tsay piëzala kanqa. Lapanpis qori pürulapita martilluwan takaylapa '
            'rurashqa kanqa.\\fig Candelabru|alt="Candelestick of Tabernacle" src="lb00277B.TIF" size="col" '
            'loc="Exo. 25.31-39" copy="HK" ref="25.31"\\fig*'
        )
        self.assertEqual(convertFigSyntax(input_str), expected_output)

    def test_convert_fig_tabernacle(self):
        input_str = (
            '\\v 2 Tsay chunka bayëtata ruratsinki tsay tamäñulata. Largunmi kanqa chunka ishkay metru pulan '
            '(12.5). Anchunnami kanqa ishkay metru.\\fig Tabernacle in wilderness|LB00259B.TIF|span||LB|Sagrädu '
            'Toldu|26.2\\fig*'
        )
        expected_output = (
            '\\v 2 Tsay chunka bayëtata ruratsinki tsay tamäñulata. Largunmi kanqa chunka ishkay metru pulan '
            '(12.5). Anchunnami kanqa ishkay metru.\\fig Sagrädu Toldu|alt="Tabernacle in wilderness" '
            'src="LB00259B.TIF" size="span" loc="" copy="LB" ref="26.2"\\fig*'
        )
        self.assertEqual(convertFigSyntax(input_str), expected_output)

    def test_convert_fig_breastplate(self):
        input_str = (
            '\\v 15 <<Pëchunman churakunan pechëra kanqa imata yarpashqätapis cüra musyananpaq.\\f + \\fr 28.15 \\ft '
            'Pechëra rurinchömi Urim y Tumim nishqan rumikuna karqan. Tsay rumikunawanmi cüra suertita rikaq Tayta Dios '
            'imata munashqanta musyananpaq. Tsaypita masta musyanaykipaq liyinki \\xt Éxo. 28.30.\\xt*\\f* Tsaytapis '
            'ruratsinki \\w efodta|efod\\w* ruratsishqaykinöla. Tsaymi kanqa qori hïlupita, azul, granäti y puka milwa '
            'hïlukunapita y llanula putskashqa lïnu hïlupita.\\fig Breastplate and turban of High Priest|HK00261B.TIF|'
            'col|Exo. 28.15-29|HK|Mandaq cürapa görran y pechëran|28.15\\fig*'
        )
        expected_output = (
            '\\v 15 <<Pëchunman churakunan pechëra kanqa imata yarpashqätapis cüra musyananpaq.\\f + \\fr 28.15 \\ft '
            'Pechëra rurinchömi Urim y Tumim nishqan rumikuna karqan. Tsay rumikunawanmi cüra suertita rikaq Tayta Dios '
            'imata munashqanta musyananpaq. Tsaypita masta musyanaykipaq liyinki \\xt Éxo. 28.30.\\xt*\\f* Tsaytapis '
            'ruratsinki \\w efodta|efod\\w* ruratsishqaykinöla. Tsaymi kanqa qori hïlupita, azul, granäti y puka milwa '
            'hïlukunapita y llanula putskashqa lïnu hïlupita.\\fig Mandaq cürapa görran y pechëran|'
            'alt="Breastplate and turban of High Priest" src="HK00261B.TIF" size="col" loc="Exo. 28.15-29" '
            'copy="HK" ref="28.15"\\fig*'
        )
        self.assertEqual(convertFigSyntax(input_str), expected_output)

    def test_convert_fig_priest_censer(self):
        input_str = (
            '\\v 43 Tsay calzoncïllutaqa Aarón y tsurinkuna jatikunqa Tinkunantsi Tolduman yaykunanpaq. Tsaynin jatishqami '
            'Lugar Santucho kaq \\w altarchöpis|altar\\w* sirvimanqa. Calzoncïlluynaq yaykurqa jutsayuq kar wanunqapaqmi. '
            'Tsay nishqäkunaqa imayyaqpis leymi kanqa Aarónpaq, tsurinkunapaq y paypita miraqkunapaqpis.\\fig Priest with '
            'censer|HK00267B.TIF|col|Exodus 28||Mandaq cüra|28.43\\fig*'
        )
        expected_output = (
            '\\v 43 Tsay calzoncïllutaqa Aarón y tsurinkuna jatikunqa Tinkunantsi Tolduman yaykunanpaq. Tsaynin jatishqami '
            'Lugar Santucho kaq \\w altarchöpis|altar\\w* sirvimanqa. Calzoncïlluynaq yaykurqa jutsayuq kar wanunqapaqmi. '
            'Tsay nishqäkunaqa imayyaqpis leymi kanqa Aarónpaq, tsurinkunapaq y paypita miraqkunapaqpis.\\fig Mandaq cüra|'
            'alt="Priest with censer" src="HK00267B.TIF" size="col" loc="Exodus 28" copy="" ref="28.43"\\fig*'
        )
        self.assertEqual(convertFigSyntax(input_str), expected_output)

    def test_convert_fig_incense_altar(self):
        input_str = (
            '\\v 26 Tsay altarta jananpa, lädunkunapa y waqrankunatapis qori püruwanmi enchaparqan. Tsaynöpis intëru kunpa '
            'qoripita rebëtinta rurarkur jiruruq churaparqan.\\fig Incense altar and priest|HK00260B.TIF|col|'
            'EXO 37.25-29||Inciensuwan qoshtatsikuna altar|37.26\\fig*'
        )
        expected_output = (
            '\\v 26 Tsay altarta jananpa, lädunkunapa y waqrankunatapis qori püruwanmi enchaparqan. Tsaynöpis intëru kunpa '
            'qoripita rebëtinta rurarkur jiruruq churaparqan.\\fig Inciensuwan qoshtatsikuna altar|alt="Incense altar and '
            'priest" src="HK00260B.TIF" size="col" loc="EXO 37.25-29" copy="" ref="37.26"\\fig*'
        )
        self.assertEqual(convertFigSyntax(input_str), expected_output)

    def test_convert_fig_bronze_altar(self):
        input_str = (
            '\\v 3 Tsaynölami altarpaq uchpa shuntakunata, tenäzakunata, trinchikunata, tazonkunata, kanalakunata y lapan '
            'manëjukunatapis broncipita rurarqan.\\fig Bronze altar|HK00256B.TIF|span|EXO. 38.1-7|HK|Bronciwan '
            'enchapashqan altar|38.1-7\\fig*'
        )
        expected_output = (
            '\\v 3 Tsaynölami altarpaq uchpa shuntakunata, tenäzakunata, trinchikunata, tazonkunata, kanalakunata y lapan '
            'manëjukunatapis broncipita rurarqan.\\fig Bronciwan enchapashqan altar|alt="Bronze altar" '
            'src="HK00256B.TIF" size="span" loc="EXO. 38.1-7" copy="HK" ref="38.1-7"\\fig*'
        )
        self.assertEqual(convertFigSyntax(input_str), expected_output)

    def test_convert_fig_multiple_consecutive(self):
        input_str = (
            '\\fig Figure One|fig01.jpg|col|Exodus 1|pub1|Caption One|1.0\\fig* '
            '\\fig Figure Two|fig02.jpg|col|Exodus 2|pub1|Caption Two|2.0\\fig* '
            '\\fig Figure Three|fig03.jpg|col|Exodus 3|pub2|Caption Three|3.0\\fig* '
            '\\fig Figure Four|fig04.jpg|span|Exodus 4|pub1|Caption Four|4.0\\fig* '
            '\\fig Figure Five|fig05.jpg|col|Exodus 5||Caption Five|5.0\\fig* '
            '\\fig Figure Six|fig06.jpg|col|Exodus 6|pub2|Caption Six|6.0\\fig* '
            '\\fig Figure Seven|fig07.jpg|span|Exodus 7|pub1|Caption Seven|7.0\\fig*'
        )
        expected_output = (
            '\\fig Caption One|alt="Figure One" src="fig01.jpg" size="col" loc="Exodus 1" copy="pub1" ref="1.0"\\fig* '
            '\\fig Caption Two|alt="Figure Two" src="fig02.jpg" size="col" loc="Exodus 2" copy="pub1" ref="2.0"\\fig* '
            '\\fig Caption Three|alt="Figure Three" src="fig03.jpg" size="col" loc="Exodus 3" copy="pub2" ref="3.0"\\fig* '
            '\\fig Caption Four|alt="Figure Four" src="fig04.jpg" size="span" loc="Exodus 4" copy="pub1" ref="4.0"\\fig* '
            '\\fig Caption Five|alt="Figure Five" src="fig05.jpg" size="col" loc="Exodus 5" copy="" ref="5.0"\\fig* '
            '\\fig Caption Six|alt="Figure Six" src="fig06.jpg" size="col" loc="Exodus 6" copy="pub2" ref="6.0"\\fig* '
            '\\fig Caption Seven|alt="Figure Seven" src="fig07.jpg" size="span" loc="Exodus 7" copy="pub1" ref="7.0"\\fig*'
        )
        self.assertEqual(convertFigSyntax(input_str), expected_output)

    def test_convert_fig_orig_multiple_consecutive(self):
        input_str = (
            '\\fig Xailongga li suxungunoa|alt="John writing on Patmos" src="PD-272bw.tif" size="span" '
            'loc="Revelation 1:1" copy="Art" ref="1:1,3"\\fig* '
            '\\fig Xailongga li suxungunoa|alt="John writing on Patmos" src="PD-272bw.tif" size="span" '
            'loc="Revelation 1:1" copy="Art" ref="1:1,3"\\fig* '
            '\\fig Xailongga li suxungunoa|alt="John writing on Patmos" src="PD-272bw.tif" size="span" '
            'loc="Revelation 1:1" copy="Art" ref="1:1,3"\\fig* '
            '\\fig Xailongga li suxungunoa|alt="John writing on Patmos" src="PD-272bw.tif" size="span" '
            'loc="Revelation 1:1" copy="Art" ref="1:1,3"\\fig* '
            '\\fig Xailongga li suxungunoa|alt="John writing on Patmos" src="PD-272bw.tif" size="span" '
            'loc="Revelation 1:1" copy="Art" ref="1:1,3"\\fig* '
            '\\fig Xailongga li suxungunoa|alt="John writing on Patmos" src="PD-272bw.tif" size="span" '
            'loc="Revelation 1:1" copy="Art" ref="1:1,3"\\fig* '
            '\\fig Xailongga li suxungunoa|alt="John writing on Patmos" src="PD-272bw.tif" size="span" '
            'loc="Revelation 1:1" copy="Art" ref="1:1,3"\\fig*'
        )
        expected_output = (
            '\\fig Xailongga li suxungunoa|alt="John writing on Patmos" src="PD-272bw.tif" size="span" '
            'loc="Revelation 1:1" copy="Art" ref="1:1,3"\\fig* '
            '\\fig Xailongga li suxungunoa|alt="John writing on Patmos" src="PD-272bw.tif" size="span" '
            'loc="Revelation 1:1" copy="Art" ref="1:1,3"\\fig* '
            '\\fig Xailongga li suxungunoa|alt="John writing on Patmos" src="PD-272bw.tif" size="span" '
            'loc="Revelation 1:1" copy="Art" ref="1:1,3"\\fig* '
            '\\fig Xailongga li suxungunoa|alt="John writing on Patmos" src="PD-272bw.tif" size="span" '
            'loc="Revelation 1:1" copy="Art" ref="1:1,3"\\fig* '
            '\\fig Xailongga li suxungunoa|alt="John writing on Patmos" src="PD-272bw.tif" size="span" '
            'loc="Revelation 1:1" copy="Art" ref="1:1,3"\\fig* '
            '\\fig Xailongga li suxungunoa|alt="John writing on Patmos" src="PD-272bw.tif" size="span" '
            'loc="Revelation 1:1" copy="Art" ref="1:1,3"\\fig* '
            '\\fig Xailongga li suxungunoa|alt="John writing on Patmos" src="PD-272bw.tif" size="span" '
            'loc="Revelation 1:1" copy="Art" ref="1:1,3"\\fig*'
        )
        self.assertEqual(convertFigSyntax(input_str), expected_output)

if __name__ == "__main__":
    unittest.main()