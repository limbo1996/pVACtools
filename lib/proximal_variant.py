import vcf
import sys
from lib.csq_parser import CsqParser

class ProximalVariant:
    def __init__(self, proximal_variants_vcf):
        self.fh = open(proximal_variants_vcf, 'rb')
        self.proximal_variants_vcf = vcf.Reader(self.fh)
        info_fields = self.proximal_variants_vcf.infos
        if 'CSQ' not in info_fields:
            sys.exit('Proximal Variants VCF does not contain a CSQ header. Please annotate the VCF with VEP before running it.')
        if info_fields['CSQ'] is None:
            sys.exit('Failed to extract format string from info description for tag (CSQ)')
        self.csq_parser = CsqParser(info_fields['CSQ'].desc)

    def extract(self, somatic_variant, alt, transcript):
        (phased_somatic_variant, potential_proximal_variants) = self.find_phased_somatic_variant_and_potential_proximal_variants(somatic_variant, alt, transcript)

        if phased_somatic_variant is None:
            print("Warning: Main somatic variant not found in phased variants file: {}, {}".format(somatic_variant, alt))
            return

        if len(potential_proximal_variants) == 0:
            return
        #for entry in potential_proximal_variants:
            #identify variants that are in phase with the phased_somatic_variant

    def find_phased_somatic_variant_and_potential_proximal_variants(self, somatic_variant, alt, transcript):
        potential_proximal_variants = []
        phased_somatic_variant = None
        for entry in self.proximal_variants_vcf.fetch(somatic_variant.CHROM, somatic_variant.start - 100, somatic_variant.end + 100):
            if entry.start == somatic_variant.start and entry.end == somatic_variant.end and entry.ALT[0] == alt:
                phased_somatic_variant = entry
                continue

            #We assume that there is only one CSQ entry because the PICK option was used but we should double check that
            csq_entries = self.csq_parser.parse_csq_entries_for_allele(entry.INFO['CSQ'], entry.ALT[0])
            if len(csq_entries) == 0:
                print("Warning: Proximal variant is not VEP annotated and will be skipped: {}".format(entry))
                continue
            else:
                csq_entry = csq_entries[0]

            consequences = {consequence.lower() for consequence in csq_entry['Consequence'].split('&')}
            if 'missense_variant' not in consequences:
                print("Warning: Proximal variant is not a missense mutation and will be skipped: {}".format(entry))
                continue

            if csq_entry['Feature'] != transcript:
                print("Warning: Proximal variant transcript is not the same as the somatic variant transcript. Proximal variant will be skipped: {}".format(entry))
                continue

            potential_proximal_variants.append([entry, csq_entry])

        return (phased_somatic_variant, potential_proximal_variants)

