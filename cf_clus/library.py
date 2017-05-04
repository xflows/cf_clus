from subprocess import check_output, CalledProcessError
from tempfile import NamedTemporaryFile
import os
import ConfigParser
import settings


def clus(input_dict):
    # First we write the ARFF file and the settings file into temporary files.
    temporary_arff = NamedTemporaryFile(suffix='.arff', delete=False)
    temporary_arff.write(input_dict['arff'])
    temporary_arff.close()
    temporary_settings = NamedTemporaryFile(suffix='.s', delete=False)
    temporary_settings.write(input_dict['settings'])
    temporary_settings.close()

    # We need to change the filenames in the settings.
    settings = ConfigParser.RawConfigParser()
    settings.optionxform = str
    settings.read(temporary_settings.name)
    settings.set('Data', 'File', temporary_arff.name)
    temporary_settings = open(temporary_settings.name, mode='wb')
    settings.write(temporary_settings)
    temporary_settings.close()

    # Execute CLUS.

    clus_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'bin', 'Clus.jar')

    # First we get the absolute path of the Clus jar.
    try:
        output = check_output(
            ["java", "-jar", clus_path, temporary_settings.name])
    except CalledProcessError, e:
        raise Exception("An error has occured while trying to execute CLUS. Output:" + str(e.output) + " Cmd:" + str(
            e.cmd) + " return code: " + str(e.returncode))

    output_file = open(temporary_settings.name.replace(".s", ".out"), 'rb')

    output = output_file.read()

    # We remove all temporary files.
    os.unlink(temporary_arff.name)
    os.unlink(temporary_settings.name)
    os.unlink(output_file.name)
    return {'output': output}
