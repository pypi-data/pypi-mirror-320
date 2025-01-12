from Bio import AlignIO
import numpy as np 
from pycofitness.resmapping.resmapping import residue_mapping
import logging 

logger = logging.getLogger(__name__)

def get_alignment_from_fasta_file(file_name):
    """Read sequences from FASTA file using Bio.AlignIO.read()
    Parameters
    ----------
        file_name : str
            Path to FASTA formatted file.
    Returns
    -------
        alignment : list
            A list of biomolecular sequence strings.
    """
    alignment = []
    try:
        record_iterator = AlignIO.read(file_name, 'fasta')
        #biopython just reads the records if there are tags (>some key).
        #It doesn't know if the file is really a biological sequence or not
    except Exception as expt:
        error_msg='\n\tError occured while reading from fasta file: {}.' +\
            '\n\tError type:{}\n\tArguments:{!r}'
        logger.error(error_msg.format(file_name, type(expt).__name__, expt.args))
        raise
    else:
        if any(True for _ in record_iterator):
            for record in record_iterator:
                seq = record.seq.strip()
                if seq: alignment.append(seq.upper())
            if not alignment:
                logger.error(
                    '\n\trecord_iterator returned by AlignIO.read()'
                    ' has no sequences',
                )
                raise ValueError

        else:
            logger.error(
                '\n\trecord_iterator returned by AlignIO.read() is empty',
            )
            raise ValueError
    return alignment

def alignment_letter2int(msa_file, biomolecule='protein'):
    """
    Converts sequences in a multiple sequence alignment from one letter to integer representation.
    """
    alignment  = get_alignment_from_fasta_file(msa_file)
    biomolecule=biomolecule.strip().upper()
    if biomolecule not in ['PROTEIN','RNA']:
        logger.error(
            '\n\t{} entered. Biomolecule must be either PROTEIN or RNA'.format(biomolecule))
        raise ValueError
    NUM_SITE_STATES = 21 if biomolecule == 'PROTEIN' else 5
    RES_TO_INT = residue_mapping[biomolecule]
    alignment_int_form = []
    total_num_seqs_in_msa = 0
    for seq in alignment:
        total_num_seqs_in_msa += 1
        seq_int = [RES_TO_INT.get(res.upper(), NUM_SITE_STATES - 1) for res in seq]
        alignment_int_form.append(seq_int)
    logger.info('\n\tTotal number of sequences read from file: {}'.format(total_num_seqs_in_msa))
    if not alignment_int_form:
        logger.error('\n\tNo data found in alignment in integer representation')
        raise ValueError
    return np.array(alignment_int_form, dtype=np.int32)