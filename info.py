import gensim

path = 'resource/target.txt'
# path_source = 'resource/source.txt'
# path_target = 'resource/source_vocab.txt'
path_target = 'resource/target_vocab.txt'
data = open(path, mode='r', encoding='utf-8', errors='ignore').readlines()
saved = open(path_target, mode='w', encoding='utf-8')
data_all = []
vocab = []
for line in data:
    line = line.strip().split()
    data_all.extend(line)
    for cur in line:
        if cur not in vocab:
            vocab.append(cur)
for cur_lable in vocab:
    saved.write(cur_lable + '\n')
saved.close()
#
# model = gensim.models.Word2Vec(data_all, sg=1, size=300, window=5, min_count=2, hs=1, workers=3)
# model.save("resource/source_w2c.vec")  # binary format
# saved = open('source_w2c.vec1', mode='w', encoding='utf-8')
# words = open(path_target, mode='r', encoding='utf-8').readlines()
# model = gensim.models.Word2Vec.load("resource/source_w2c.vec")
# for cur_word in words:
#     cur_word = cur_word.strip()
#     aa = str(model[cur_word])
#     print(cur_word, aa)
# labeled_source_path = 'resource/source_all.txt'
# labeled_data_path = 'resource/source.txt'
# labeled_data_save_path = 'resource/target.txt'
# labeled_data_save = open(labeled_data_path, mode='w', encoding='utf-8')
# labeled_data_save_targrt = open(labeled_data_save_path, mode='w', encoding='utf-8')
#
# labeled_data = open(labeled_source_path, mode='r', encoding='utf-8', errors='ignore').readlines()
# for cur_ in labeled_data:
#     cur_1, cur_2 = cur_.strip().split('\t')
#     assert len(cur_1.split()) == len(cur_2.split()), cur_1
#     labeled_data_save.write(cur_1 + '\n')
#     labeled_data_save_targrt.write(cur_2 + '\n')
# labeled_data_save.close()
# labeled_data_save_targrt.close()