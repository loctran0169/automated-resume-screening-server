import pickle

from sqlalchemy.util.compat import b
from app.main.process_data.classifier.ontology import Ontology
import networkx as nx


class DomainOntology(Ontology):
    """ 
    A simple subclass of Ontology.
    This class helps create the specified ontology from the existent path.
    """

    def __init__(self, domain_ontology_pickle_path, domain_name):
        super().__init__(load_ontology=False)
        self.domain_ontology_pickle_path = domain_ontology_pickle_path
        self.domain_name = domain_name
        self.load_domain_ontology()

        # Custom stems_topic for also counting alternative labels
        self.topic_stems.clear()
        allkeys = set(self.topics.keys())
        for k in self.primary_labels.keys():
            allkeys.add(k)

        for topic in allkeys:
            if topic[:4] not in self.topic_stems:
                self.topic_stems[topic[:4]] = list()
            self.topic_stems[topic[:4]].append(topic)

    
    def load_domain_ontology(self):
        """ Function that loads the domain ontology from the pickle file. 
        This file has been serialised using Pickle allowing to be loaded quickly.
        """
        ontology = pickle.load(open(self.domain_ontology_pickle_path, 'rb'))
        self.from_cso_to_single_items(ontology)
        # print("{domain_name} ontology has been loaded.".format(domain_name=self.domain_name))


    def generate_graph_dict(self, words):
        g = {}
        root = None
        words = list(words)
        # Loop through words
        while len(words) > 0:
            w = words.pop()
            if w in g.keys(): 
                continue
            else:
                g[w] = set()
            # climb ontology
            bs = list(self.broaders.get(w, '.'))
            while bs[0] != '.':
                # choose broader
                b = bs[0]
                for i in bs:
                    if i in words:
                        b = i
                        break
                stop = False
                # add broader skill to graph
                if b not in g.keys(): g[b] = set()
                else: stop = True
                g[b].add(w)
                w = b
                # stop if needed
                if stop: bs[0] = '.'
                else: bs = list(self.broaders.get(w, '.'))
            # Find root
            if root is None: root = w
        return (g, root)

