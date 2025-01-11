import unittest, copy
import onkopus.onkopus_clients


class UTAAdapterProteinSequenceAnnotationTestCase(unittest.TestCase):

    def test_uta_adapter_protein_sequence_client_variant(self):
        genome_version = 'hg38'
        data = {"chr7:140753336A>T": {}, "chr10:8115913C>T":{},"chr7:140753336A>G": {}}
        variant_data = onkopus.onkopus_clients.UTAAdapterClient(
            genome_version=genome_version).process_data(data)
        variant_data = onkopus.onkopus_clients.UTAAdapterProteinSequenceClient(
            genome_version=genome_version).process_data(variant_data)
        print("Response ",variant_data)
        self.assertEqual(variant_data["chr7:140753336A>T"]["UTA_Adapter_protein_sequence"]["protein_sequence"][:18],"MAALSGGGGGGAEPGQAL","")

    def test_uta_adapter_protein_sequence_client_gene(self):
        genome_version = 'hg38'
        data = {"BRAF": {}, "NRAS": {}}
        variant_data = onkopus.onkopus_clients.UTAAdapterProteinSequenceClient(
            genome_version=genome_version).process_data(data,gene_request=True)
        print("Response ",variant_data)
        self.assertListEqual(list(variant_data.keys()),["BRAF","NRAS"],"")

