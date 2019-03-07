"""
parsing.py

MIT License

Copyright (c) 2018

Weill Cornell Medicine, Memorial Sloan Kettering Cancer Center, and Authors

Authors:
Yuanqing Wang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# =======
# imports
# =======
from ftplib import FTP
import xml.etree.ElementTree as ET
import pandas as pd
import os

def parse_single_entry(idx: int, ftp):
    """ Parse the single entry of emdb.

    Parameters
    ----------
    idx : int
        index of the entry

    Returns
    -------
    res : float
        resolution
    doi : str
        doi number
    pubmed : str
        pubmed address
    date : str
        date of the entry
    authors : str
        list of authors, seperated by comma
    pdb : str
        pdb entry


    """
    # initialize
    res = 0.0
    doi = ""
    pubmed = ""
    date = ""
    authors = ""
    pdb = ""

    try:
        # converting to entry string
        entry = (4 - len(str(idx))) * '0' + str(idx)
        file_name = './pub/databases/emdb/structures/EMD-%s/header/emd-%s-v30.xml' % (entry, entry)

        # prepare a tempfile
        temp_file_path = str(idx) + '_tmp.xml'
        temp_file = open(temp_file_path, 'wb')

        # download
        ftp.retrbinary('RETR ' + file_name, temp_file.write, 1024)
        temp_file.close()

        # read the xml
        xml_file = open(temp_file_path, 'r')
        tree = ET.parse(xml_file)
    except:
        return res, doi, pubmed, date, authors, pdb

    try:
        # res
        res = tree.find('./structure_determination_list/structure_determination/' +\
            'singleparticle_processing/final_reconstruction/resolution').text
    except:
        pass

    # date
    try:
        date = tree.find('./admin/current_status/date').text
    except:
        pass

    # ref
    try:
        external_references = tree.findall('./crossreferences/citation_list/' +\
            'primary_citation/journal_citation/external_references')


        for child in external_references:
            if child.attrib['type'] == 'PUBMED':
                pubmed = child.text
            elif child.attrib['type'] == 'DOI':
                doi = child.text
    except:
        pass

    try:
        authors = tree.findall('./crossreferences/citation_list/' +\
            'primary_citation/journal_citation/author')

        authors = ", ".join([child.text for child in authors])

    except:
        pass

    try:
        pdbs = tree.findall('./crossreferences/pdb_list/' +\
            'pdb_reference/pdb_id')
        pdb = ",".join([child.text for child in pdbs])
    except:
        pass

    try:
        xml_file.close()
        os.remove(temp_file_path)
    except:
        pass
    return res, doi, pubmed, date, authors, pdb

def parse_all():
    """ Parse the whole database.
    """
    ftp = FTP('ftp.ebi.ac.uk')
    ftp.login()

    df = pd.DataFrame(columns = ['index', 'doi', 'pubmed', 'date', 'authors',
        'pdb'])

    for idx in range(1, 9784):
        res, doi, pubmed, date, authors, pdb = parse_single_entry(idx, ftp)
        df[idx] = [idx, res, doi, pubmed, date, authors, pdb]
        print(idx, res, doi, pubmed, date, authors, pdb)
    df.to_csv('emdb_summary.csv', sep='\t')

if __name__ == '__main__':
    parse_all()
