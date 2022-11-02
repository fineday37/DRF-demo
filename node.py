import pprint

lines = [(1, 1, '父1节点'), (2, 1, '1-2'), (3, 1, '1-3'), (4, 3, '1-3-4'), (5, 3, '1-3-5'), (6, 3, '1-3-6'),
         (7, 7, '父7节点'), (8, 7, '7-8'), (9, 7, '7-9'), (10, 11, '10-11')]  # (id, prarentId, name)

nodes = {}
data_temp = []
for line in lines:
    id, parentId, name = line
    # nodes[]保存需要的字典格式
    nodes[id] = {'children': [], 'id': id, "parentId": parentId, "name": name, 'orLeafnode': '1'}  # orLeafnode 是叶子节点
    # data_temp 保存id,parentId
    data_temp.append({'id': id, "parentId": parentId})
data = []
for i in data_temp:
    id = i['id']
    parent_id = i['parentId']
    node = nodes[id]
    if id == parent_id:
        node['orLeafnode'] = '0'
        data.append(node)
    else:
        parent = nodes.get(parent_id)
        if parent:
            parent['orLeafnode'] = '0'
            parent['children'].append(node)
        else:
            node['orLeafnode'] = '0'
            data.append(node)
pprint.pprint(data)


import redis

r = redis.Redis(host='43.140.197.232', port=6379)
r.set('python', 'children')
print(r.get('python'))

