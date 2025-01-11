import unittest, copy, os
import onkopus as op
import adagenes as ag

class MolFeatAnnotationTestCase(unittest.TestCase):

    def test_molfeat_client(self):
        #genome_version = 'hg19'
        genome_version = 'hg38'

        #data = {"chr17:7681744T>C": {}, "chr10:8115913C>T": {}}
        data = {"chr7:140753336A>T":{}}

        variant_data = op.UTAAdapterClient(genome_version=genome_version).process_data(data)
        #variant_data = op.MolecularFeaturesClient(
        #    genome_version=genome_version).process_data(variant_data)

        #print("Response ",variant_data)
        #self.assertEqual(variant_data["chr7:140753336A>T"]["molecular_features"]["aromaticity_alt"],0,"")

    def test_molfeat_export(self):
        genome_version = 'hg38'
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../../test_files/somaticMutations.l520.protein.vcf"
        outfile = __location__ + "/../../test_files/somaticMutations.l520.protein.molfeat.vcf"

        data = {"chr7:140753336A>T": {}}

        #variant_data = op.UTAAdapterClient(genome_version=genome_version).process_data(data)
        magic_obj = op.MolecularFeaturesClient(
            genome_version=genome_version)
        #op.write_file(outfile, variant_data)

        ag.process_file(infile, outfile, magic_obj=magic_obj)

        file = open(outfile)
        contents = file.read()[0:60]
        contents_expected = """n"""
        #self.assertEqual(contents, contents_expected, "")
        file.close()

