import sox
from enum import Enum

class PlayStatus(Enum):
    failed = 0
    success = 1
    no_media = 2

def get_normalized_file(input_file, db_level=0):
    """
    wrapper for pySox norm command
    :param input_file: name of the input file to process
    :param db_level: the db level to which to normalize the audio file
    :return: Boolean of whether or not the process was successful
    """
    try:
        transformer = sox.Transformer()
        transformer.norm(db_level)
        input_file_parts = input_file.split('/')
        input_file_parts[len(input_file_parts) - 1] = "{0}_{1}_{2}".format("norm", db_level, input_file_parts[len(input_file_parts) - 1])
        output_file = '/'.join(input_file_parts)
        transformer.build(input_file, output_file)
        return True, output_file
    except:
        return False, input_file


def get_amplified_file(input_file, gain_db=0.0, normalize=True, limiter=True, balance=None):
    """
    Wrapper for PySox gain command
    :param input_file: name of the input file to process
    :param gain_db: The gain in db to be applied to the file
    :param normalize: Whether or not to apply normalization
    :param limiter: Whether or not to use a limiter to prevent clipping
    :param balance: Balance options. See docs on balance parameter for pysox:gain
    :return: Boolean of whether or not the process was successful
    """
    try:
        transformer = sox.Transformer()
        transformer.gain(gain_db, normalize, limiter, balance)
        input_file_parts = input_file.split('/')
        input_file_parts[len(input_file_parts) - 1] = "{0}_{1}_{2}".format("gain", gain_db, input_file_parts[len(input_file_parts) - 1])
        output_file = '/'.join(input_file_parts)
        transformer.build(input_file, output_file)
        return True, output_file
    except Exception as e:
        print e.message
        return False, input_file