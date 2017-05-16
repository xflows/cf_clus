from subprocess import check_output, CalledProcessError
from tempfile import NamedTemporaryFile
import os
import ConfigParser
import json

import subprocess


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

    # We need to enable ClowdFlows output.
    if not settings.has_section('Output'):
        settings.add_section('Output')
    settings.set('Output', 'OutputClowdFlowsJSON', 'Yes')

    temporary_settings = open(temporary_settings.name, mode='wb')
    settings.write(temporary_settings)
    temporary_settings.close()

    # Execute CLUS.

    clus_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'bin', 'Clus.jar')
    p = subprocess.Popen(["java", "-jar", clus_path, temporary_settings.name], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    if p.returncode != 0 and p.returncode is not None:
        raise Exception("There was an error when running CLUS: " + str(p.stderr.read()) + " (Error code: " + str(
            p.returncode) + ")")

    output = p.stdout.read()
    error = p.stderr.read()

    try:
        output_file = open(temporary_settings.name.replace(".s", ".out"), 'rb')
        output = output_file.read()
        os.unlink(output_file.name)
    except:
        pass

    try:
        json_file = open(temporary_settings.name.replace(".s", ".json"), 'rb')
        json_contents = json.loads(json_file.read())
        returned_settings = json_contents['settings']
        models = json_contents['models']
        os.unlink(json_file.name)

        default = {}
        original = {}
        pruned = {}

        for m in models:
            print m
            if m['name'] == 'Default':
                default = m['representation']
            if m['name'] == 'Original':
                original = m['representation']
            if m['name'] == 'Pruned':
                pruned = m['representation']
    except:
        returned_settings = None
        models = None
        default = None
        original = None
        pruned = None

    # We remove all temporary files.
    os.unlink(temporary_arff.name)
    os.unlink(temporary_settings.name)
    return {
        'output': output,
        'settings': returned_settings,
        'models': models,
        'default': default,
        'original': original,
        'pruned': pruned,
        'error:': error
    }


def clus_display_svg(input_dict):
    return {}


def clus_display_tree(input_dict):
    return {}


def clus_display_tree_and_examples(input_dict):
    return {}
