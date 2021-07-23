import pickle
from owlready2 import IRIS, get_ontology
import csv as co
import re

# get_ontology('data.owl').load()


class Ontology:
    def __init__(self, intput, output):
        """ Initialising the ontology class
        """
        self.topics = dict()
        self.topics_wu = dict()
        self.broaders = dict()
        self.narrowers = dict()
        self.same_as = dict()
        self.primary_labels = dict()
        self.primary_labels_wu = dict()
        self.topic_stems = dict()
        self.input = intput
        self.output = output
        self.ontology_attr = ('topics', 'topics_wu', 'broaders', 'narrowers',
                              'same_as', 'primary_labels', 'primary_labels_wu', 'topic_stems')
        self.load_cso_from_csv()

    def __repr__(self):
        return "Ontology: {}".format(self.from_single_items_to_cso())

    def load_cso_from_csv(self):
        """Function that loads the CSO from the file in a dictionary.
           In particular, it load all the relationships organised in boxes:
               - topics, the list of topics
               - broaders, the list of broader topics for a given topic
               - narrowers, the list of narrower topics for a given topic
               - same_as, all the siblings for a given topic
               - primary_labels, all the primary labels of topics, if they belong to clusters
               - topics_wu, topic with underscores
               - primary_labels_wu, primary labels with underscores
               - topic_stems, groups together topics that start with the same 4 letters
        """

        with open(self.input, "r") as ontoFile:
            ontology = co.reader(ontoFile, delimiter=',')

            for triple in ontology:
                # relation is subClassOf
                if triple[1] == "http://www.w3.org/2000/01/rdf-schema#subClassOf":
                    child = triple[0].split('#')[1].lower().replace("_", " ")
                    parent = triple[2].split('#')[1].lower().replace("_", " ")

                    # load broader topic
                    if child in self.broaders:
                        if parent not in self.broaders[child]:
                            self.broaders[child].append(parent)
                    else:
                        self.broaders[child] = [parent]

                    # load narrower topic
                    if parent in self.narrowers:
                        if child not in self.narrowers[parent]:
                            self.narrowers[parent].append(child)
                    else:
                        self.narrowers[parent] = [child]

                if triple[1] == "http://www.w3.org/2000/01/rdf-schema#label":
                    alter_labels = triple[2:]   
                    primary_label= '' 
                    if not triple[0].startswith("https://cso.kmi.open.ac.uk/topics/"):
                        primary_label = triple[0].split('#')[1].lower().replace("_", " ")
                    else:
                        primary_label = triple[0].split("/")[-1].lower().replace("_", " ")
                    for label in alter_labels:
                        label = label.lower()
                        label_wu = label.replace(" ", "_")

                        if label not in self.primary_labels:
                            self.primary_labels[label] = primary_label
                        if label_wu not in self.primary_labels:
                            self.primary_labels_wu[label_wu] = primary_label.replace(
                                " ", "_")

                if triple[1] == 'http://cso.kmi.open.ac.uk/schema/cso#superTopicOf':
                    parent = triple[0].split('/')[-1].lower().replace("_", " ")
                    child = triple[2].split('/')[-1].lower().replace("_", " ")

                    # load broader topic
                    if child in self.broaders:
                        if parent not in self.broaders[child]:
                            self.broaders[child].append(parent)
                    else:
                        self.broaders[child] = [parent]

                    # load narrower topic
                    if parent in self.narrowers:
                        if child not in self.narrowers[parent]:
                            self.narrowers[parent].append(child)
                    else:
                        self.narrowers[parent] = [child]

                if triple[1] == 'http://cso.kmi.open.ac.uk/schema/cso#relatedEquivalent':
                    primary_label = triple[0].split(
                        '/')[-1].lower().replace("_", " ")
                    alter_labels = triple[2].split(
                        '/')[-1].lower().replace("_", " ")
                    label_wu = alter_labels.replace(" ", "_")

                    if alter_labels not in self.primary_labels:
                        self.primary_labels[alter_labels] = primary_label
                    if label_wu not in self.primary_labels:
                        self.primary_labels_wu[label_wu] = primary_label.replace(
                            " ", "_")

                # set topic
                if triple[0].startswith("http://www.semanticweb.org/"):
                    topic = triple[0].split('#')[1].lower().replace("_", " ")
                    topic_wu = re.sub(r" ", "_", topic)
                    if topic not in self.topics:
                        self.topics[topic] = True
                    if topic_wu not in self.topics_wu:
                        self.topics_wu[topic_wu] = True
                if triple[0].startswith("https://cso.kmi.open.ac.uk"):
                    topic = triple[0].split('/')[-1].lower().replace("_", " ")
                    topic_wu = re.sub(r" ", "_", topic)
                    if topic not in self.topics:
                        self.topics[topic] = True
                    if topic_wu not in self.topics_wu:
                        self.topics_wu[topic_wu] = True

            for topic in self.topics.keys():
                if topic[:4] not in self.topic_stems:
                    self.topic_stems[topic[:4]] = list()
                self.topic_stems[topic[:4]].append(topic)

            with open(self.output, 'wb') as cso_file:
                print("Creating ontology pickle file from a copy of the CSO Ontology found in", self.output)
                pickle.dump(self.from_single_items_to_cso(), cso_file)

    def from_single_items_to_cso(self):
        """ Function that returns a single dictionary containing all relevant values for the ontology.
        """
        return {attr: getattr(self, attr) for attr in self.ontology_attr}

# url = 'https://cso.kmi.open.ac.uk/topics/pifa'
# print(url.split("/")[-1])

data = Ontology(intput='D:/KLTN/thesis/ontology/general/general-ontology.csv',
                output='D:/KLTN/thesis/ontology/general/general-ontology.p')
