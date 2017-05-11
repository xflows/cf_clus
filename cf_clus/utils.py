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
            'target_stat'] + '" shape=box style=filled ]\n', node_index + 1
    return text, node_index


def clus_tree_to_node_edge(node, node_index):
    nodes = []
    edges = []
    node['dot_id'] = node_index
    if 'children' in node:
        nodes.append({'id': node['dot_id'], 'label': node['test_string'], 'shape': 'ellipse'})
        node_index += 1
        for child in node['children']:
            child_nodes, child_edges, node_index = clus_tree_to_node_edge(child, node_index)
            nodes += child_nodes
            edges += child_edges
            edges.append({'from': node['dot_id'], 'to': child['dot_id'], 'label': child['branch_label']})
    else:
        nodes.append({'id': node_index, 'label': node['target_stat'], 'shape': 'box'})
        return nodes, edges, node_index + 1
    return nodes, edges, node_index
