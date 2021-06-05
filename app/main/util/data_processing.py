from os import remove
import pickle
from networkx.algorithms.bipartite.basic import color
from app.main import classify_manager as cm
import networkx as nx
# import gmatch4py as gm
from numpy import linalg as LA
import numpy as np
from app.main.util.draw_graph import radial_expansion_pos, draw
import library.zss as zss
from library.zss import Node
import time
# import zss
# from zss import Node

def get_technical_skills(domain, text, modules="both"):
    """
    Use classify_manager to extract skill from text.
    Return: 
        (skills, explanation)
        skills: array.
        explanation: dictionary.
    """

    if domain not in cm.supported_domains:
        print("Request to extract the unsupported domain.")
        raise ValueError("Unsupported domain.")
    
    # prepare_text = {'keywords':"data mining, computer science"}
    prepare_text = {'keywords':""}

    prepare_text['abstract'] = text
    
    result_dict = cm.run_classifier(domain, prepare_text, modules=modules, explanation=True).get_dict()
    skills = result_dict['union']
    explanation = result_dict['explanation']

    # Convert to string
    skills = [str(s) for s in skills]

    return (skills, explanation)

def generate_edges(graph):
    edges = [] 
    # for each node in graph 
    for node in graph: 
        # for each neighbour node of a single node 
        for neighbour in graph[node]: 
            # if edge exists then append 
            edges.append((node, neighbour)) 
    return edges

def generate_skill_graph(edges):
    G2 = nx.Graph()
    G2.add_edges_from(edges)
    return G2


# def matching_score(post_text, cv_text, domain):
#     """
#     Return:
#     {
#         'score': float
#         'cv_explanation': dict
#         'post_explanation': dict
#     }
    
#     """
#     post_skills = __get_skills_by_classifier(post_text, domain)
#     cv_skills = __get_skills_by_classifier(cv_text, domain, 'syntactic')

#     (post_graph, p_root) = __generate_graph_with(domain=domain, skills=post_skills['union'])
#     (cv_graph, cv_root) = __generate_graph_with(domain=domain, skills=cv_skills['union'])

#     score = __matching(post_graph, cv_graph)

#     if not cv_skills['explanation'] or not post_skills['explanation']:
#         score = 0

#     DECIMAL_LENGTH = 4
#     return {
#         "score": np.round(score, DECIMAL_LENGTH),
#         "cv_explanation": cv_skills['explanation'],
#         "post_explanation": post_skills['explanation'],
#         "post_graph": post_graph,
#         "cv_graph": cv_graph,
        
#         "cv_skills": cv_skills,
#         "post_skills": post_skills,
#     }


def __get_skills_by_classifier(text, domain, modules = 'both'):
    return cm.run_classifier(domain, text, modules, explanation=True).get_dict()


# def __matching(post_graph, cv_graph):
#         # all edit cost are equal to 1
#         ged = gm.GraphEditDistance(1, 1, 1, 1)
#         result = ged.compare([post_graph, cv_graph], None)
#         # description how much score is and why it got matched
#         return LA.norm(ged.similarity(result))

def __generate_graph_with(domain, skills):
    (data, root_label) = cm.get_ontology(domain).generate_graph_dict(skills)
    G = nx.DiGraph()
    keys = list(data.keys())
    keys.sort()
    # Add nodes
    G.add_nodes_from([k for k in keys])
    # Add edges
    for k in data.keys():
        for v in data[k]:
            G.add_edge(k, v)
    draw(G, root_label)
    return (G, root_label)


def tree_matching_score(post_text, cv_text, domain):
    """
    Return:
    {
        'score': float
        'cv_explanation': dict
        'post_explanation': dict
    }
    
    """
    post_skills = __get_skills_by_classifier(post_text, domain)
    cv_skills = __get_skills_by_classifier(cv_text, domain, 'syntactic')

    (post_graph, post_node_count) = generate_graph_tree_with(domain=domain, skills=post_skills['union'])
    (cv_graph, cv_node_count) = generate_graph_tree_with(domain=domain, skills=cv_skills['union'])

    (score, ops) = __tree_edit_distance(cv_graph, post_graph)
    similarity_score = 1 / (1 + score)

    # if not cv_skills['explanation'] or not post_skills['explanation']:
    #     score = 0

    DECIMAL_LENGTH = 4
    return {
        "score": np.round(similarity_score, DECIMAL_LENGTH),
        "cv_explanation": cv_skills['explanation'],
        "post_explanation": post_skills['explanation'],
        "post_graph": post_graph,
        "cv_graph": cv_graph,
        
        "cv_skills": cv_skills,
        "post_skills": post_skills,
    }

def score_skills_grahp(skill_post1, grahped, domain):
    """
    Return: Score float

    """

    post_skills_1 = dict()
    post_skills_1['union']=skill_post1

    (post_graph_1, post_node_count_1) = generate_graph_tree_with(domain=domain, skills=post_skills_1['union'])

    (score, ops) = __tree_edit_distance(post_graph_1, grahped)
    similarity_score = 1 / (1 + score)


    DECIMAL_LENGTH = 4
    return np.round(similarity_score, DECIMAL_LENGTH)

def tree_matching_score_jd(skill_post1, skill_post2, domain):
    """
    Return:
    {
        'score': float
        'post1_explanation': dict
        'post2_explanation': dict
    }
    
    """

    post_skills_1 = dict()
    post_skills_1['union']=skill_post1
    post_skills_2 = dict()
    post_skills_2['union']=skill_post2

    (post_graph_1, post_node_count_1) = generate_graph_tree_with(domain=domain, skills=post_skills_1['union'])
    (post_graph_2, post_node_count_2) = generate_graph_tree_with(domain=domain, skills=post_skills_2['union'])

    (score, ops) = __tree_edit_distance(post_graph_1, post_graph_2)
    similarity_score = 1 / (1 + score)


    DECIMAL_LENGTH = 4
    return {
        "score": np.round(similarity_score, DECIMAL_LENGTH),
        # "post1_explanation": post_skills_1['explanation'],
        # "post2_explanation": post_skills_2['explanation'],
        "post1_graph": post_graph_1,
        "post2_graph": post_graph_2,
        
        "post1_skills": post_skills_1,
        "post2_skills": post_skills_2,
    }

def distance_graph_score(post_graph_1, post_graph_2):
    (score, _) = __tree_edit_distance(post_graph_1, post_graph_2)
    similarity_score = 1 / (1 + score)

    return np.round(similarity_score, 4)

def get_children(node):
    return node.children

def count_graph(g):
    s = 0
    for _ in g.iter():
        s += 1
    return s


def __tree_edit_distance(cv_graph, post_graph):
    (_, ops) = zss.simple_distance(cv_graph, post_graph, return_operations=True)
    unit_of_score = 1 / (count_graph(cv_graph) + count_graph(post_graph))

    _ops = [o for o in ops if o.type != 0 and o.type != 3]
    score = len(_ops) * unit_of_score
    return (score, ops)

def generate_graph_tree_with(domain, skills): 
    (graph_data, root) = cm.get_ontology(domain).generate_graph_dict(skills)
    # (_, _) = __generate_graph_with(domain, skills)

    graph_data = dict(graph_data)
    
    node_dict = {}
    # nodes
    for s in graph_data.keys():
        node = Node(s)
        node_dict[s] = node
    # edges
    for s in graph_data.keys():
        node = node_dict[s]
        child_labels = list(graph_data[s])
        child_labels.sort()
        for c in child_labels:
            child = node_dict[c]
            node.addkid(child)

    # if no skill match
    if not node_dict:
        node_dict['unknowed'] = Node('unknowed')
        return (node_dict['unknowed'], 1)

    return (node_dict[root], len(graph_data.keys()))