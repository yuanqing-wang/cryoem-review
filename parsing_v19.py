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
    [res,
        res_method,
        date,
        pubmed,
        doi,
        authors,
        pdb,
        mol_weights,
        method,
        conc,
        buffer_ph,
        cryogen,
        humidity,
        temperature,
        vitrification_instrument,
        electron_source,
        electron_dose,
        imaging_mode,
        illumination_mode,
        detector,
        microscope,
        accelerating_voltage,
        symmetry,
        map_size,
        voxel_min,
        voxel_max,
        voxel_avg,
        voxel_std
        ] = ["" for dummy_idx in range(28)]

    # converting to entry string
    entry = (4 - len(str(idx))) * '0' + str(idx)
    file_name = './pub/databases/emdb/structures/EMD-%s/header/emd-%s-v19.xml' % (entry, entry)

    # prepare a tempfile
    temp_file_path = str(idx) + '_tmp.xml'
    temp_file = open(temp_file_path, 'wb')

    # download
    ftp.retrbinary('RETR ' + file_name, temp_file.write, 1024)
    temp_file.close()

    # read the xml
    xml_file = open(temp_file_path, 'r')
    tree = ET.parse(xml_file)

    try:
        # res
        res = tree.find('.processing/reconstruction/resolutionByAuthor').text
    except:
        pass

    try:
        res_method = tree.find('.processing/reconstruction/resolutionMethod').text
    except:
        pass

    # date
    try:
        date = tree.find('./deposition/depositionDate').text
    except:
        pass

    # ref
    try:
        external_references = tree.findall('.deposition/' +\
            'primaryReference/journalArticle/externalReference')

        for child in external_references:
            if child.attrib['type'] == 'pubmed':
                pubmed = child.text
            elif child.attrib['type'] == 'doi':
                doi = child.text

    except:
        pass

    try:
        authors = tree.find('.deposition/authors').text

    except:
        pass

    try:
        pdbs = tree.find('.deposition/fittedPDBEntryIdList')
        pdb = ",".join([child.text for child in pdbs])
    except:
        pass

    # marcomolecule
    try:
        mols = tree.findall('.sample/sampleComponentList/' +\
            'sampleComponent/molWtTheo')
        mol_weights = ", ".join([child.text + child.attrib['units']\
            for child in mols])

    except:
        pass

    '''
    # grid
    try:
        grid = tree.find('.//grid')
        model = grid.find('./model')
        material = grid.find('./material')
        mesh = grid.find('./mesh')
        details = grid.find('./details')

        if material != None:
            try:
                material = material.text
                material = material.lower()

                # standarize grid material
                if ('copper/rhodium' in material) or\
                    ('cu/rh' in material):
                   grid_material = 'COPPER/RHODIUM'

                elif ('copper/molybdenum' in material) or\
                    ('cu/mo' in material):
                    grid_material = 'COPPER/MOLYBDENUM'

                elif ('cu' in material) or ('copper' in material):
                    grid_material = 'COPPER'

                elif ('gold' in material) or ('au' in material):
                    grid_material = 'GOLD'

            except:
                pass

        elif (material == None) and (details != None):
            try:
                material = details.text

                # standarize grid material
                if ('copper/rhodium' in material) or\
                    ('cu/rh' in material):
                   grid_material = 'COPPER/RHODIUM'

                elif ('copper/molybdenum' in material) or\
                    ('cu/mo' in material):
                    grid_material = 'COPPER/MOLYBDENUM'

                elif ('cu' in material) or ('copper' in material):
                    grid_material = 'COPPER'

                elif ('gold' in material) or ('au' in material):
                    grid_material = 'GOLD'

            except:
                pass

        if mesh != None:
            try:
                mesh = str(mesh.text)

                # standarize
                if '200' in mesh:
                    grid_mesh = '200'
                elif '300' in mesh:
                    grid_mesh = '300'
                elif '400' in mesh:
                    grid_mesh = '400'

            except:
                pass

        elif (mesh == None) and (details != None):
            try:
                mesh = details.text
                # standarize
                if '200' in mesh:
                    grid_mesh = '200'
                elif '300' in mesh:
                    grid_mesh = '300'
                elif '400' in mesh:
                    grid_mesh = '400'
            except:
                pass

        if model != None:
            try:
                model = model.text

                if '1.2/1.3' in model:
                    grid_model = 'Quantfoil R1.2/1.3'
                elif '1/2' in model:
                    grid_model = 'Quantfoil R1/2'
                elif '2/2' in model:
                    grid_model = 'Quantfoil R2/2'
                elif '2/4' in model:
                    grid_model = 'Quantfoil R2/4'
                elif '2/1' in model:
                    grid_model = 'Quantfoil R2/1'
                elif '3/3' in model:
                    grid_model = 'Quantfoil R3/3'

            except:
                pass

        elif (model == None) and (details != None):
            try:
                model = details.text

                if '1.2/1.3' in model:
                    grid_model = 'Quantfoil R1.2/1.3'
                elif '1/2' in model:
                    grid_model = 'Quantfoil R1/2'
                elif '2/2' in model:
                    grid_model = 'Quantfoil R2/2'
                elif '2/4' in model:
                    grid_model = 'Quantfoil R2/4'
                elif '2/1' in model:
                    grid_model = 'Quantfoil R2/1'
                elif '3/3' in model:
                    grid_model = 'Quantfoil R3/3'
            except:
                pass

    except:
        pass
    '''

    # method
    try:
        method = tree.find('.processing/method').text
    except:
        pass


    # preparation
    try:
        conc = tree.find('.experiment/specimenPreparation/specimenConc').text
    except:
        pass

    try:
        buffer_ph = tree.find('experiment/specimenPreparation/buffer/ph').text
    except:
        pass

    # vitrification
    try:
        cryogen = tree.find('./experiment/vitrification/cryogenName').text
    except:
        pass

    try:
        humidity = tree.find('./experiment/vitrification/humidity').text
    except:
        pass

    try:
        temperature = tree.find('./experiment/vitrification/temperature').text
    except:
        pass

    try:
        vitrification_instrument = tree.find(
            './experiment/vitrification/instrument').text
    except:
        pass

    # imaging
    try:
        electron_source = tree.find('./experiment/imaging/electronSource').text
    except:
        pass

    try:
        electron_dose = tree.find('/experiment/imaging/electronDose').text
    except:
        pass

    try:
        imaging_mode = tree.find('/experiment/imaging/imagingMode').text
    except:
        pass

    try:
        illumination_mode = tree.find(
            '/experiment/imaging/illuminationMode').text
    except:
        pass

    try:
        detector = tree.find('/experiment/imaging/detector').text
    except:
        pass

    try:
        microscope = tree.find('/experiment/imaging/microscope').text
    except:
        pass

    try:
        accelerating_voltage = tree.find(
            '/experiment/imaging/acceleratingVoltage').text
    except:
        pass

    try:
        symmetry = tree.find('.//appliedSymmetry').text
    except:
        pass


    # map
    try:
        map_size = tree.find('./map/dimensions/numColumns').text
    except:
        pass

    try:
        voxel_min = tree.find('./map/statistics/minimum').text
        voxel_max = tree.find('./map/statistics/maximum').text
        voxel_avg = tree.find('./map/statistics/average').text
        voxel_std = tree.find('./map/statistics/std').text
    except:
        pass
    # wrap up
    try:
        xml_file.close()
    except:
        pass

    try:
        os.remove(temp_file_path)
    except:
        pass

    return [
        res,
        res_method,
        date,
        pubmed,
        doi,
        authors,
        pdb,
        mol_weights,
        method,
        conc,
        buffer_ph,
        cryogen,
        humidity,
        temperature,
        vitrification_instrument,
        electron_source,
        electron_dose,
        imaging_mode,
        illumination_mode,
        detector,
        microscope,
        accelerating_voltage,
        symmetry,
        map_size,
        voxel_min,
        voxel_max,
        voxel_avg,
        voxel_std
        ]

def parse_all():
    """ Parse the whole database.
    """
    ftp = FTP('ftp.ebi.ac.uk')
    ftp.login()

    df = pd.DataFrame()

    for idx in range(1, 9784):
            result = parse_single_entry(idx, ftp)

            df = df.append([result])

            print(idx, result)
    df.to_csv('emdb_summary.csv', sep='\t')

if __name__ == '__main__':
    parse_all()
