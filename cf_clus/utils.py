def clus_tree_to_dot(node, node_index):
    text = ""
    node['dot_id'] = node_index
    if 'children' in node:
        text += "N" + str(node_index) + ' [label="' + node['test_string'] + '"]\n'
        node_index += 1
        for child in node['children']:
            child_text, node_index = clus_tree_to_dot(child, node_index)
            text += child_text
            text += "N" + str(node['dot_id']) + "->N" + str(child['dot_id']) + '[label="' + child[
                'branch_label'] + '"]' + "\n"
    else:
        return "N" + str(node_index) + ' [label="' + node[
            'target_stat'].replace(',', ',\\n') + '" shape=box style=filled ]\n', node_index + 1
    return text, node_index


def clus_tree_to_node_edge(node, node_index):
    nodes = []
    edges = []
    node['dot_id'] = node_index
    if 'children' in node:
        nodes.append({'id': node['dot_id'], 'label': node['test_string'], 'shape': 'ellipse',
                      'target_stat': node['target_stat'].replace(',', ',\\n'),
                      'title': node['target_stat'].replace(',', ',<br>'),
                      'min': node['summary']['min'],
                      'max': node['summary']['max'],
                      'stddev': node['summary']['stddev'],
                      'avg': node['summary']['avg']})
        node_index += 1
        for child in node['children']:
            child_nodes, child_edges, node_index = clus_tree_to_node_edge(child, node_index)
            nodes += child_nodes
            edges += child_edges
            edges.append({'from': node['dot_id'], 'to': child['dot_id'], 'label': child['branch_label']})
    else:
        nodes.append({'id': node_index, 'label': node['target_stat'].replace(',', ',\\n'), 'shape': 'box',
                      'target_stat': node['target_stat'], 'title': node['target_stat'].replace(',', ',<br>'),
                      'min': node['summary']['min'],
                      'max': node['summary']['max'],
                      'stddev': node['summary']['stddev'],
                      'avg': node['summary']['avg']})
        return nodes, edges, node_index + 1
    return nodes, edges, node_index


def perform_test(test_string, instance, attributes):
    if '(' in test_string:
        test_string = test_string.split(' (')[0]
    if ' > ' in test_string:
        name_value = test_string.split(' > ')
        name = name_value[0]
        value = float(name_value[1])
        i = 0
        for a in attributes:
            if a[0] == name:
                return instance[i] > value
            i += 1
    if ' = ' in test_string:
        name_value = test_string.split(' = ')
        name = name_value[0]
        value = name_value[1]
        i = 0
        for a in attributes:
            if a[0] == name:
                return instance[i] == value
            i += 1
    if " <= " in test_string:
        name_value = test_string.split(' <= ')
        name = name_value[0]
        value = name_value[1]
        i = 0
        for a in attributes:
            if a[0] == name:
                return instance[i] <= value
            i += 1
    if " in " in test_string:
        name_value = test_string.split(' in ')
        name = name_value[0]
        value = name_value[1]
        value = value.replace("{", "")
        value = value.replace("}", "")
        values = value.split(",")
        values = [x.strip() for x in values]
        i = 0
        for a in attributes:
            if a[0] == name:
                return instance[i] in values
            i += 1
    return None


def get_instance_nodes(node, instance, attributes):
    node_ids = []
    node_ids.append(node['dot_id'])
    if 'children' in node:
        test_result = perform_test(node['test_string'], instance, attributes)
        for child in node['children']:
            if test_result == True and child['branch_label'] == 'Yes':
                node_ids = node_ids + get_instance_nodes(child, instance, attributes)
            if test_result == False and child['branch_label'] == 'No':
                node_ids = node_ids + get_instance_nodes(child, instance, attributes)
    return node_ids
