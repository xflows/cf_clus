from subprocess import check_output, CalledProcessError
from tempfile import NamedTemporaryFile
import os
import ConfigParser


def clus(input_dict):
    # First we write the ARFF file and the settings file into temporary files.
    temporary_arff = NamedTemporaryFile(suffix='.arff', delete=False)
    temporary_arff.write(input_dict['arff'])
    temporary_arff.close()
    temporary_settings = NamedTemporaryFile(suffix='.s', delete=False)
    settings = input_dict['settings']
    if settings is None:
        settings = ''
    temporary_settings.write(settings)
    temporary_settings.close()

    # We need to change the filenames in the settings.
    settings = ConfigParser.RawConfigParser()
    settings.optionxform = str
    settings.read(temporary_settings.name)
    if not settings.has_section('Data'):
        settings.add_section('Data')
    settings.set('Data', 'File', temporary_arff.name)
    temporary_settings = open(temporary_settings.name, mode='wb')
    settings.write(temporary_settings)
    temporary_settings.close()

    # Execute CLUS.

    clus_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'bin', 'Clus.jar')
    try:
        output = check_output(
            ["java", "-jar", clus_path, temporary_settings.name])
    except CalledProcessError, e:
        raise Exception("An error has occured while trying to execute CLUS. Output:" + str(e.output) + " Cmd:" + str(
            e.cmd) + " return code: " + str(e.returncode))
    try:
        output_file = open(temporary_settings.name.replace(".s", ".out"), 'rb')
        output = output_file.read()
        os.unlink(output_file.name)
    except:
        pass

    # We remove all temporary files.
    os.unlink(temporary_arff.name)
    os.unlink(temporary_settings.name)
    return {'output': output}
