import pickle
import Levenshtein.StringMatcher as ls
import json
from gensim.models import Word2Vec

# http://www.semanticweb.org/vinhpham/ontologies/2021/0/general

model = Word2Vec.load('D:/KLTN/thesis/ontology/trained/w2v_model_trigram_2246403_v2_freezed')

parent_path = 'D:/KLTN/thesis/ontology/general'
cso = pickle.load(open(parent_path+'/cso.p', "rb"))
out_path = parent_path + '/combine.json'
min_similarity = 0.94
word_similarity = 0.6  # similarity of words in the model
top_amount_of_words = 10  # maximum number of words to select

cso_test = pickle.load(open('D:/automated-resume-screening-server/app/main/process_data/models/ontology/general_ontology.p', "rb"))
print(len(cso['topics_wu'].items()))

print(len(model.wv.index_to_key))
output = {}
i = 0
for wet in model.wv.index_to_key:
    # print(wet)
    i += 1
    if(i % 1000 == 0):
        print(i, len(output))

    output[wet] = []

    similar_words = []
    similar_words.append((wet, 1))  # Appending the gram with max similarity

    similarities = model.wv.most_similar(wet, topn=top_amount_of_words)
    similar_words.extend(similarities)

    for wet2, sim in similar_words:
        if sim >= word_similarity: 
            topics = {}
            topics = [key for key, _ in cso['topics_wu'].items() if key.startswith(wet2[:4])]
            for topic in topics:
                m = ls.StringMatcher(None, topic, wet2).ratio() #topic is from cso, wet is from word embedding
                if m >= min_similarity:
                    try:
                        output[wet].append({"topic":topic,"sim_t":m,"wet":wet2,"sim_w":sim})
                    except KeyError:
                        print(wet)
    # break
# now saving the cached model
with open(out_path, 'w') as outfile:
    json.dump(output, outfile, indent=4)
