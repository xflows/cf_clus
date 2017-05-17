from django.shortcuts import render
import os
from utils import clus_tree_to_dot, clus_tree_to_node_edge, get_instance_nodes
from random import random

from django.conf import settings
import arff


def clus_display_svg(request, input_dict, output_dict, widget):
    """Visualization displaying a decision tree"""

    import subprocess
    from mothra.settings import MEDIA_ROOT
    from workflows.helpers import ensure_dir

    img_type = 'svg'
    if input_dict['img_type'] == 'raster':
        img_type = 'png'

    dot_text = """digraph J48Tree {
    N0 [label="f8" ]
    N0->N1 [label="= +"]
    N1 [label="f99" ]
    N1->N2 [label="= +"]
    N2 [label="east (10.0/1.0)" shape=box style=filled ]
    N1->N3 [label="= -"]
    N3 [label="west (3.0/1.0)" shape=box style=filled ]
    N0->N4 [label="= -"]
    N4 [label="west (7.0)" shape=box style=filled ]
    }"""

    if type(input_dict['classifier']) == list:
        dot_text = ""
        starting_id = 0
        for cls in input_dict['classifier']:
            dot_representation, starting_id = clus_tree_to_dot(cls['representation'], starting_id)
            dot_text += dot_representation + "\n"
            # dot_text = dot_text + "digraph " + cls['name'] + " {\n" + \
            #           dot_representation + "}\n\n"
        dot_text = "digraph Tree {\n" + dot_text + "}"
    else:
        dot_text = "digraph Tree {\n" + clus_tree_to_dot(input_dict['classifier'], 0)[0] + "}"

    filename = '/'.join([str(request.user.id), 'decisionTree-clus-%d.dot' % widget.id])
    dotfile = filename
    destination_dot = '/'.join([MEDIA_ROOT, filename])
    ensure_dir(destination_dot)

    with open(destination_dot, 'w') as dot_file:
        dot_file.write(dot_text)

    # png/svg file
    filename = '/'.join([str(request.user.id),
                         'decisionTree-clus-%d.%s' % (widget.id, img_type)
                         ])
    destination_img = os.path.join(MEDIA_ROOT, filename)
    ensure_dir(destination_img)

    try:
        dot_path = settings.DOT_PATH
    except:
        dot_path = 'dot'

    subprocess.call(dot_path + " -T%s %s -o %s" % (img_type, destination_dot, destination_img), shell=True)

    return render(request,
                  'visualizations/cf_clus_display_svg_tree.html',
                  {'filename': filename,
                   'dotfile': dotfile,
                   'random': int(random() * 10000000),
                   'widget': widget,
                   'input_dict': input_dict})


def clus_display_tree(request, input_dict, output_dict, widget):
    """Visualization displaying a decision tree"""

    if type(input_dict['classifier']) == list:
        nodes, edges = [], []
        starting_id = 0
        for cls in input_dict['classifier']:
            new_nodes, new_edges, starting_id = clus_tree_to_node_edge(cls['representation'], starting_id)
            nodes += new_nodes
            edges += new_edges
    else:
        nodes, edges, index = clus_tree_to_node_edge(input_dict['classifier'], 0)

    return render(request,
                  'visualizations/cf_clus_display_tree.html',
                  {
                      'widget': widget,
                      'input_dict': input_dict,
                      'nodes': nodes,
                      'edges': edges
                  })


def clus_display_tree_and_examples(request, input_dict, output_dict, widget):
    """Visualization displaying a decision tree and the examples in the tree"""

    nodes, edges, index = clus_tree_to_node_edge(input_dict['classifier'], 0)

    data = arff.loads(input_dict['arff'])

    datanodes = []

    for instance in data['data']:
        instance_nodes = get_instance_nodes(input_dict['classifier'], instance, data['attributes'])
        datanodes.append({'data': instance, 'nodes': instance_nodes})

    return render(request,
                  'visualizations/cf_clus_display_tree_and_examples.html',
                  {
                      'widget': widget,
                      'input_dict': input_dict,
                      'nodes': nodes,
                      'edges': edges,
                      'data': data,
                      'datanodes': datanodes,
                      'random': int(random() * 10000000),
                  })


def clus_display_tree_and_summary(request, input_dict, output_dict, widget):
    """Visualization displaying a decision tree and the summary"""

    if type(input_dict['classifier']) == list:
        nodes, edges = [], []
        starting_id = 0
        attributes = input_dict['classifier'][0]['representation']['summary']['names']
        for cls in input_dict['classifier']:
            new_nodes, new_edges, starting_id = clus_tree_to_node_edge(cls['representation'], starting_id)
            nodes += new_nodes
            edges += new_edges
    else:
        nodes, edges, index = clus_tree_to_node_edge(input_dict['classifier'], 0)
        attributes = input_dict['classifier']['summary']['names']

    return render(request,
                  'visualizations/cf_clus_display_tree_and_summary.html',
                  {
                      'widget': widget,
                      'input_dict': input_dict,
                      'nodes': nodes,
                      'edges': edges,
                      'attributes': attributes,
                      'random': int(random() * 10000000),
                  })
