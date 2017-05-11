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
