from subprocess import check_output, CalledProcessError
from tempfile import NamedTemporaryFile
import os
import ConfigParser
import json

import subprocess
import StringIO


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

    has_prune = False
    # We check if there is prune set data.
    if input_dict.get('prune', None) is not None:
        temporary_validation = NamedTemporaryFile(suffix='.arff', delete=False)
        temporary_validation.write(input_dict['prune'])
        temporary_validation.close()
        settings.set('Data', 'PruneSet', temporary_validation.name)
        has_prune = True

    has_test = False
    # We check if there is test set data.
    if input_dict.get('test', None) is not None:
        temporary_test = NamedTemporaryFile(suffix='.arff', delete=False)
        temporary_test.write(input_dict['test'])
        temporary_test.close()
        settings.set('Data', 'TestSet', temporary_test.name)
        has_test = True

    # We need to enable ClowdFlows output.
    if not settings.has_section('Output'):
        settings.add_section('Output')
    settings.set('Output', 'OutputClowdFlowsJSON', 'Yes')

    temporary_settings = open(temporary_settings.name, mode='wb')
    settings.write(temporary_settings)
    temporary_settings.close()

    # Execute CLUS.

    args = input_dict['args'].replace(";", "").replace("|", "")

    if len(args.strip()) > 0:
        args = args.split(" ")
    else:
        args = []

    clus_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'bin', 'Clus.jar')
    p = subprocess.Popen(["java", "-jar", clus_path] + args + [temporary_settings.name,], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    if p.returncode != 0 and p.returncode is not None:
        raise Exception("There was an error when running CLUS: " + str(p.stderr.read()) + " (Error code: " + str(
            p.returncode) + ")")

    output = p.stdout.read()
    error = p.stderr.read()

    if len(error.strip()) > 0:
        if "Error: " in error:
            raise Exception(error.strip())

    try:
        output_file = open(temporary_settings.name.replace(".s", ".out"), 'rb')
        output = output_file.read()
        os.unlink(output_file.name)
    except:
        pass

    fimp = ""
    try:
        fimp_file = open(temporary_settings.name.replace(".s", ".fimp"), 'rb')
        fimp = fimp_file.read()
        os.unlink(fimp_file.name)
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
            # print m
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

    if has_prune:
        os.unlink(temporary_validation.name)
    if has_test:
        os.unlink(temporary_test.name)

    return {
        'output': output,
        'settings': returned_settings,
        'models': models,
        'default': default,
        'original': original,
        'pruned': pruned,
        'fimp': fimp,
        # 'error:': error
    }


def clus_display_svg(input_dict):
    return {}


def clus_display_tree(input_dict):
    return {}


def clus_display_tree_and_examples(input_dict):
    if type(input_dict['classifier']) == list:
        raise Exception("This widget does not work on multiple trees.")
    return {}


def clus_display_tree_and_summary(input_dict):
    return {}


def handle_setting(name, input_dict, section, settings, checkbox=False):
    if not checkbox and input_dict.get(name, None) is not None \
            and input_dict.get(name, "").strip() != "" \
            and input_dict.get(name, "") != "null":
        if not settings.has_section(section):
            settings.add_section(section)
        settings.set(section, name, input_dict[name])
    if checkbox:
        if input_dict.get(name, None) is not None \
                and input_dict.get(name, "").strip() != "" \
                and input_dict.get(name, "") != "null":
            if not settings.has_section(section):
                settings.add_section(section)
            settings.set(section, name, "Yes")
        else:
            if not settings.has_section(section):
                settings.add_section(section)
            settings.set(section, name, "No")


def clus_generate_settings(input_dict):
    settings = ConfigParser.RawConfigParser()
    settings.optionxform = str
    settings_buffer = StringIO.StringIO()

    handle_setting("RandomSeed", input_dict, "General", settings)

    handle_setting("Target", input_dict, "Attributes", settings)
    handle_setting("Clustering", input_dict, "Attributes", settings)
    handle_setting("Disable", input_dict, "Attributes", settings)
    handle_setting("Key", input_dict, "Attributes", settings)
    handle_setting("Weights", input_dict, "Attributes", settings)

    handle_setting("MinimalWeight", input_dict, "Model", settings)

    handle_setting("FTest", input_dict, "Tree", settings)
    handle_setting("SplitSampling", input_dict, "Tree", settings)
    handle_setting("Heuristic", input_dict, "Tree", settings)
    handle_setting("PruningMethod", input_dict, "Tree", settings)
    handle_setting("InductionOrder", input_dict, "Tree", settings)
    handle_setting("EntropyType", input_dict, "Tree", settings)

    handle_setting("BranchFrequency", input_dict, "Output", settings, checkbox=True)

    settings.write(settings_buffer)

    return {
        'settings': settings_buffer.getvalue()
    }
