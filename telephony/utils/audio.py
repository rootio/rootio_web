import sox


def get_normalized_file(input_file, db_level=0):
    """
    wrapper for pySox norm command
    :param input_file: name of the input file to process
    :param db_level: the db level to which to normalize the audio file
    :return: name of the processed file if successful, otherwise returns original input file name
    """
    try:
        transformer = sox.Transformer()
        transformer.norm(db_level)
        output_file = "{0}_{1}_{2}".format("norm", db_level, input_file)
        transformer.build(input_file, output_file)
        return output_file
    except:
        return input_file


def get_amplified_file(input_file, gain_db=0.0, limiter=True, balance=None):
    """
    Wrapper for PySox gain command
    :param input_file: name of the input file to process
    :param gain_db: The gain in db to be applied to the file
    :param limiter: Whether or not to use a limiter to prevent clipping
    :param balance: Balance options. See docs on balance parameter for pysox:gain
    :return: name of the processed file if successful, otherwise returns original input file name
    """
    try:
        transformer = sox.Transformer()
        transformer.gain(gain_db, limiter, balance)
        output_file = "{0}_{1}_{2}".format("gain", gain_db, input_file)
        transformer.build(input_file, output_file)
        return output_file
    except:
        return input_file