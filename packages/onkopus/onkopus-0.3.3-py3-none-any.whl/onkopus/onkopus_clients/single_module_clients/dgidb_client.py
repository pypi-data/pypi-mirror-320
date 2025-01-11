import datetime, traceback, copy
import adagenes.tools
import adagenes.tools.module_requests as req
from onkopus.conf import read_config as config
from adagenes.tools import generate_variant_dictionary
import onkopus as op


class DGIdbClient:

    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.url_pattern = config.dgidb_src
        self.srv_prefix = config.dgidb_srv_prefix
        self.extract_keys = config.dgidb_keys
        self.info_lines = config.dgidb_info_lines
        self.error_logfile = error_logfile

        self.qid_key = "q_id"
        if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
            self.qid_key = "q_id_hg19"

    def process_data(self, vcf_lines, gene_request=False):

        qid_gene_name_dc = {}
        qid_list = []
        for qid in vcf_lines.keys():
            variant_data = vcf_lines[qid]
            if ("UTA_Adapter" in variant_data) and (gene_request is False):
                if ("gene_name" in variant_data["UTA_Adapter"]) and (
                        "variant_exchange" in variant_data["UTA_Adapter"]):
                    qid_gene_name_dc[variant_data["UTA_Adapter"]["gene_name"]] = qid
                    qid_list.append(variant_data["UTA_Adapter"]["gene_name"])
            else:
                qid_list.append(qid)
        q_lists = list(op.tools.divide_list(copy.deepcopy(qid_list), chunk_size=100))

        for q_list in q_lists:
            q = ",".join(q_list)
            query = 'genes=' + q
            query = '?' + query

            try:
                json_body = req.get_connection(query, self.url_pattern, "hg38")

                for gene_name in json_body.keys():

                        if gene_request is False:
                            qid = qid_gene_name_dc[gene_name]
                        else:
                            qid = gene_name

                        try:
                            vcf_lines[qid][self.srv_prefix] = json_body[gene_name]
                        except:
                            if self.error_logfile is not None:
                                cur_dt = datetime.datetime.now()
                                date_time = cur_dt.strftime("%m/%d/%Y, %H:%M:%S")
                                print(cur_dt, ": error processing variant response: ", qid, ';', traceback.format_exc(), file=self.error_logfile+str(date_time)+'.log')
                            else:
                                print(cur_dt, ": error processing variant response: ", qid, ';', traceback.format_exc())
            except:
                print(": error processing variant response: ;", traceback.format_exc())


        return vcf_lines
