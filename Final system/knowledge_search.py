import re
import csv
from utils import *
from rnn import NER_net, predict
from py2neo import Graph
BATCH_SIZE = config.FLAGS.batch_size
unit_num = embeddings_size         # 默认词向量的大小等于RNN(每个time step) 和 CNN(列) 中神经单元的个数, 为了避免混淆model中全部用unit_num表示。
time_step = max_sequence      # 每个句子的最大长度和time_step一样,为了避免混淆model中全部用time_step表示。
DROPOUT_RATE = config.FLAGS.dropout
EPOCH = config.FLAGS.epoch
TAGS_NUM = get_class_size()
entity_path = r'E:\KG\data\entity.csv'  # E:\KG\data\entity.csv
role_path = r'E:\KG\data\roles.csv'
action = config.FLAGS.action
# 获取词的总数。
vocab_size = get_src_vocab_size()
src_unknown_id = tgt_unknown_id = vocab_size
src_padding = vocab_size + 1

src_vocab_table, tgt_vocab_table = create_vocab_tables(src_vocab_file, tgt_vocab_file, src_unknown_id,
                                                       tgt_unknown_id)
embedding = load_word2vec_embedding(vocab_size)
print(embedding)
#
# if action == 'train':
#     iterator = get_iterator(src_vocab_table, tgt_vocab_table, vocab_size, BATCH_SIZE)
# elif action == 'predict':
#     BATCH_SIZE = 1
#     DROPOUT_RATE = 1.0
#     iterator = get_predict_iterator(src_vocab_table, vocab_size, BATCH_SIZE)
# else:
#     print('Only support train and predict actions.')
#     exit(0)
#
# tag_table = tag_to_id_table()
# net = NER_net("ner", iterator, embedding, BATCH_SIZE)


def data_read():
    e = csv.reader(open(entity_path, mode='r', encoding='utf-8'))
    r = csv.reader(open(role_path, mode='r', encoding='utf-8'))
    e_name = []
    e_id = []
    r_start_id = []
    r_end_id = []
    r_type = []
    for e_index, e_line in enumerate(e):
        if e_index == 0:
            continue
        else:
            e_id_, e_name_, e_label = e_line[:]
            e_id.append(e_id_)
            e_name.append(e_name_)
    #
    for r_index, r_line in enumerate(r):
        if r_index == 0:
            continue
        else:
            id_start, id_end, _type = r_line[:]
            r_start_id.append(id_start)
            r_end_id.append(id_end)
            r_type.append(_type)
    return e_name, e_id, r_start_id, r_end_id, r_type


# e_name_w, e_id_w, r_start_id_w, r_end_id_w, r_type_w = data_read()
# print('r_type_w:', r_type_w)

def find_lcsubstr(s1, s2):
    m = [[0 for i in range(len(s2)+1)]  for j in range(len(s1)+1)]
    mmax = 0
    p = 0
    for i in range(len(s1)):
        for j in range(len(s2)):
            if s1[i] == s2[j]:
                m[i+1][j+1] = m[i][j]+1
                if m[i+1][j+1] > mmax:
                    mmax = m[i+1][j+1]
                    p = i+1
    return s1[p-mmax:p], mmax


def get_en_r(data_in, raw):

    tags = list(map(lambda x: str(x), data_in))
    index_o = tags.index(str(b'O'))
    en_res = ''
    pro_res = ''
    for index_en, cur_en in enumerate(tags[: index_o]):
        en_res += raw[index_en]

    for index_res, cur_res in enumerate(tags[index_o + 1:]):
       pro_res += raw[index_res + index_o + 1]
    print('BILSTM-CRF查询结果:', en_res, pro_res)
    return [en_res, pro_res]



def match_data(name):
    # 保存查询对象
    to_saved = open('resource/predict.txt', mode='w', encoding='utf-8')
    to_v = ' '.join(list(name.strip()))
    to_saved.write(to_v + '\n')
    to_saved.close()
    # DL 提取实体和关系
    action = config.FLAGS.action
    # 获取词的总数。
    vocab_size = get_src_vocab_size()
    src_unknown_id = tgt_unknown_id = vocab_size
    src_padding = vocab_size + 1
    src_vocab_table, tgt_vocab_table = create_vocab_tables(src_vocab_file, tgt_vocab_file, src_unknown_id,
                                                           tgt_unknown_id)
    embedding = load_word2vec_embedding(vocab_size)
    print(embedding)

    if action == 'train':
        iterator = get_iterator(src_vocab_table, tgt_vocab_table, vocab_size, BATCH_SIZE)
    elif action == 'predict':
        BATCH_SIZE = 1
        DROPOUT_RATE = 1.0
        iterator = get_predict_iterator(src_vocab_table, vocab_size, BATCH_SIZE)
    else:
        print('Only support train and predict actions.')
        exit(0)
    tag_table = tag_to_id_table()
    net = NER_net("ner", iterator, embedding, BATCH_SIZE)
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        sess.run(iterator.initializer)
        tf.tables_initializer().run()
        if action == 'train':
            train(net, iterator, sess)
        elif action == 'predict':
            print('action is prediction.')
            tags = predict(net, tag_table, sess)
        final_results = get_en_r(tags, list(name.strip()))
        final_results = ''.join(final_results)
        print('final_results:', final_results)
        # ###################################################################3
        e_name_w, e_id_w, r_start_id_w, r_end_id_w, r_type_w = data_read()
        # name = list(name.strip())
        print('To search name:', name)
        # match the name, type
        best_score = 0
        best_score_1 = 0
        best_name = ''
        best_type = ''
        for index_, cur_e_name_w in enumerate(e_name_w):
            cur_e_name_w = list(cur_e_name_w.strip())
            # lcs, score = find_lcsubstr(cur_e_name_w, ''.join(name))
            lcs, score = find_lcsubstr(cur_e_name_w, final_results)
            if best_score < score:
                best_score = score
                best_name = cur_e_name_w
        print('Best match:\t score:{} name:{}'.format(best_score, ''.join(best_name)))
        best_name = ''.join(best_name)
        for id_star, id_end, en_type in zip(r_start_id_w, r_end_id_w, r_type_w):
            compare_name = ''
            id_star_name = e_name_w[e_id_w.index(id_star)]
            id_end_name = e_name_w[e_id_w.index(id_end)]
            if id_star_name.__eq__(best_name):
                compare_name = id_end
            if id_end_name.__eq__(best_name):
                compare_name = id_star
            if compare_name.__eq__(''):
                continue
            else:
                # ######################################################
                # lcs_type, score_1 = find_lcsubstr(en_type, ''.join(name))
                lcs_type, score_1 = find_lcsubstr(en_type, final_results)
                if best_score_1 <= score_1:
                    best_score_1 = score_1
                    best_type = compare_name
        print('res:', best_name, best_type)
        if best_type.__eq__(''):
            return best_name, None, None
        else:
            # return best_name, best_type, e_name_w[e_id_w.index(best_type)]
            return best_name, final_results, e_name_w[e_id_w.index(best_type)]


graph = Graph('http://localhost:7474/db/data/')


def query(name):
    print('query graph')
    clear_name, f, ans = match_data(name)
    data = graph.run("match(p:my_entity {name:'%s'}) -[r]->(n) return p.name, r, n.name limit 50" % ''.join(clear_name))
    data = list(data)
    print('Answer:', ans)
    ans = f + '是' + ans
    return get_json_data(ans, data)


def get_json_data(ass, data):
    json_data = {'data': [], "links": [], 'res_jg': ass}
    d = []

    for i in data:
        # print(i["p.Name"], i["r.relation"], i["n.Name"], i["p.cate"], i["n.cate"])
        d.append(i['p.name']+"_")
        d.append(i['n.name']+"_")
        d = list(set(d))
    name_dict = {}
    count = 0
    for j in d:
        j_array = j.split("_")

        data_item = {}
        name_dict[j_array[0]] = count
        count += 1
        data_item['name'] = j_array[0]
        #data_item['category'] = CA_LIST[j_array[1]]
        json_data['data'].append(data_item)
    for i in data:
        string=str(i['r'])
        p = re.compile(".*?:`(.*?)`]->.*?", re.S)
        result = re.findall(p, string)
        link_item = {}
        link_item['source'] = name_dict[i['p.name']]

        link_item['target'] = name_dict[i['n.name']]
        link_item['value'] = result
        json_data['links'].append(link_item)

    return json_data


# data_read()
# match_data('冠状病毒')
