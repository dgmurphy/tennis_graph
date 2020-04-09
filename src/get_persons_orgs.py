import spacy
import os.path
import sys
from lib.logging import logging


def main():

    DATA_DIR = "../data/"
    IN_FILE = DATA_DIR + "tennis_resolved.txt"
    PERSONS_FILE = DATA_DIR + "Tennis_Persons.csv"

    with open(IN_FILE, 'r') as file:  
        text = file.read()

    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    sentences = list(doc.sents)
    persons_rows = []

    print("Num sentences: " + str(len(sentences)))
    processed = 0

    for s in sentences:
        persons = ""
        sdoc = nlp(str(s))
        for ent in sdoc.ents:
            if ((str(ent.label_) == "PERSON") or (str(ent.label_) == "ORG")):
                # remove the and The
                ent_str = str(ent)
                ent_str = ent_str.replace("the ", "")
                ent_str = ent_str.replace("The ", "")
                ent_str = ent_str.replace("a ", "")
                ent_str = ent_str.replace("'", "^")
                persons += (ent_str + "; ")
        
        if len(persons) > 0:
            persons = persons[:-2]  # drop last "; "
            persons_rows.append(persons)
            if (len(persons_rows) % 10) == 0:
                logging.info("persons rows: " + str(len(persons_rows)))

        processed += 1
        if (processed %100) == 0:
            print("processed: " + str(processed))
            
    with open(PERSONS_FILE, 'w') as outfile:
        for row in persons_rows:
            outfile.write(row + "\n")

    print("wrote " + PERSONS_FILE)

if __name__ == '__main__':
    main()
    print("DONE\n")