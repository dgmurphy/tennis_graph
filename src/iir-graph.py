import pandas as pd 
import numpy as np
import os.path
import sys
from lib.logging import logging
from itertools import combinations
import csv
import glob


# return persons set from a string of gkg v1 persons
def get_persons_set(persons_line):

    persons_set = set()
    l = persons_line.strip()
    person_list = l.split(";")
    
    for person in person_list:
        person = person.strip()
        if len(person) > 1:
            persons_set.add(person)

    return persons_set


def make_persons_pairs(persons_line):

    persons_set = set()
    l = persons_line.strip()
    person_list = l.split(";")
    
    for person in person_list:
        person = person.strip()
        if len(person) > 1:
            persons_set.add(person)

    pairs = []
    pset_tuples = list(combinations(persons_set, 2))
    for tup in pset_tuples:
        pair = sorted(tup)
        pairs.append(pair)

    return pairs


def names_to_ids(persons_dict, row, idx):

    persons = str(row.name).split(',')

    ids = []
    for person in persons:
        person = person.strip()
        pid = persons_dict[person][1]
        ids.append(pid)
    
    return str(ids[idx])
    


def main():

    print (os. getcwd())
    #sys.exit()

    DATA_DIR = "../data/"

    # create blank full df
    df = pd.DataFrame(columns=['PERSONS'])

    file_list = glob.glob( DATA_DIR + "IIRPersons.csv" )
 
    for f in file_list:
        
        logging.info("reading" + f)

        # read the file into temp df
        tdf = pd.read_csv(f, header=0, sep='\t', names=['PERSONS'], 
            index_col=False)

        # append temp df to full df
        df = df.append(tdf, ignore_index=True)


    logging.info("consolidated df shape: " + str(df.shape))


    # ------ create person nodes (TODO this can be made faster) --------
    persons_rows = df['PERSONS'].tolist()
    persons_dict = {}

    # assign person IDs
    pid = 0
    persons_set = set()
    for line in persons_rows:
        persons_set = get_persons_set(line)

        for person in persons_set:
            if person in persons_dict.keys():
                values = persons_dict[person]
                node_size = values[0]
                person_id = values[1]
                persons_dict[person] = [node_size + 1, person_id]

            else:
                persons_dict[person] = [1, pid]
                pid += 1


    # convert, sort and write person nodes file
    plist = []
    for key, value in persons_dict.items():   
        pl = [value[1], key, value[0]]  # id, label, nodesize
        plist.append(pl)

    node_list_df = pd.DataFrame(plist, columns=['id', 'label', 'value'])
    node_list_df = node_list_df.sort_values(by=['value'], ascending=False)
    #print(str(node_list_df.head(20)))   

    nodesfile = DATA_DIR + "PersonsNodesAll.csv"
    logging.info("writing " + nodesfile)
    node_list_df.to_csv(nodesfile, header=True, index=False, sep=",")    


    # -------------------- Build edge list ------------------------------------

    # make persons column into set
    df['PERSONS'] = df.apply(lambda row: make_persons_pairs(row.PERSONS), axis=1)

    #print(df['PERSONS'])
    #sys.exit()

    logging.info('creating pairs')
    pairs = []
    persons_list = df['PERSONS'].tolist()
    for row in persons_list:
        for pair in row:
            pair_string = str(pair[0]) + ", " + str(pair[1])
            pairs.append(pair_string)

    # make one column with all the pairs and value counts
    logging.info('building edge df')
    pdf = pd.DataFrame()
    pdf["values"] = pairs
    vc = pdf["values"].value_counts()
    edge_df = pd.DataFrame(vc)
 
    
    edgefile = DATA_DIR + "PersonsEdgeListAll.csv"
    logging.info("writing " + edgefile)
    edge_df = edge_df.sort_values(by=['values'], ascending=False)
    edge_df.to_csv(edgefile, header=False, index=True, sep=",")

    # Add node ids as columns
    edge_df['id1'] = edge_df.apply(lambda row: names_to_ids(persons_dict, row, 0), axis=1)
    edge_df['id2'] = edge_df.apply(lambda row: names_to_ids(persons_dict, row, 1), axis=1)
    #print(edge_df)

    edgeidfile = DATA_DIR + "PersonsEdgeIDsAll.csv"
    logging.info("writing " + edgeidfile)

    # write ids edge list
    edge_df = edge_df.sort_values(by=['values'], ascending=False)
    edge_df.to_csv(edgeidfile, columns=['id1', 'id2', 'values'], header=True, index=False, 
        sep=",")



    # filter edge list by link strength
    LINK_VALUE_CUTOFF = 6
    logging.info("Filtering edge list for link-strength > " + 
        str(LINK_VALUE_CUTOFF))
    
    top_edges_df = edge_df[edge_df['values'] >= LINK_VALUE_CUTOFF]
    print(top_edges_df.head(100))    

    # write the shortend edgelist
    edgefile = DATA_DIR + "PersonsEdgeListTopN.csv"
    logging.info("writing " + edgefile)
    edges_short = top_edges_df.sort_values(by=['values'], ascending=False)
    edges_short.to_csv(edgefile, header=True, index=False, sep=",",
        columns=['id1', 'id2', 'values'])       


    # keep all the nodes that appear anywhere in the top-n edge list
    keep_persons = set()
    p1_set = set(edges_short['id1'].apply(str).tolist())
    p2_set = set(edges_short['id2'].apply(str).tolist())
    pset = p1_set.union(p2_set)
    
    print(str(pset))

    # convert, sort and write shortened person nodes file
    plist = []
    for key, value in persons_dict.items():   
        if str(value[1]) in pset:
            pl = [value[1], key, value[0]]  # id, label, nodesize
            plist.append(pl)

    node_list_df = pd.DataFrame(plist, columns=['id', 'label', 'value'])
    node_list_df = node_list_df.sort_values(by=['value'], ascending=False)
    #print(str(node_list_df.head(20)))   

    nodesfile = DATA_DIR + "PersonsNodesTopN.csv"
    logging.info("writing " + nodesfile)
    node_list_df.to_csv(nodesfile, header=True, index=False, sep=",")    

if __name__ == '__main__':
    main()
    print("DONE\n")


