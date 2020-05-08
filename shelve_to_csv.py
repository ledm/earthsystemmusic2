

from shelve import open as shopen
import os
import numpy as np


def load_shelve(path, data_key):
    """
    Load the data from a shelve file.
    """
    print('Loading shelve from path:', path)
    sh = shopen(path , 'r')
    print(sh.keys())
    shelve_data = sh['modeldata'][data_key]
    sh.close()
    return shelve_data


def get_output_folder(name):
    image_fold = 'output/'+name+'/'
    try:os.makedirs(image_fold)
    except:pass
    return image_fold


def save_as_csv(field, jobID, units, label, data):
    """Convert data diuct to a csv file"""

    out_fn = get_output_folder('csv/'+field)+jobID+'_'+field+'.csv'
    if os.path.exists(out_fn):
        print('Already exists:', out_fn)
        #return

    times = np.array([t for t in sorted(data.keys())])
    data = np.array([data[t] for t in times])
    data = np.ma.masked_invalid(data)

    jobID_type = {
        'u-aw310': 'Pre-industrial Control',
        'u-bb075': 'Historical',
        'u-bh210': 'SSP1 1.9',
        'u-bh285': 'SSP5 3.4 Overshoot',
        'u-be392': 'SSP5 8.5',
        'u-az513': 'Historical',
        'u-az515': 'Historical',
        'u-az524': 'Historical',
        'u-bb075': 'Historical',
        'u-bb277': 'Historical',
        'u-bc179': 'Historical',
        'u-bc292': 'Historical',
        'u-bc370': 'Historical',
        'u-bc470': 'Historical',
        'u-bd288': 'Historical',
        'u-bd416': 'Historical',
        'u-bd483': 'Historical',
        'u-bf647': 'Historical',
        'u-bf656': 'Historical',
        'u-bf703': 'Historical',
    	}


    #print(name, field, jobID, times, data)
    units = units.replace('$', '')

    metadata = ' '.join(['# UK Earth System Model (UKESM1) data for', label, '(',field, ') in', '['+units+'].\n' ])
    metadata += '# Data prepared by Lee de Mora (ledm@pml.ac.uk) from Plymouth Marine Laboratory.\n'
    metadata += ' '.join(['# Experiment type:',jobID_type[jobID], '\n# jobID:',jobID, ''])

    header = ' '.join(['\nyear,', field, '['+units+']\n'])
    hashes = ''.join(['#' for i in range(80)])
    txt = '\n'.join([hashes, metadata,hashes,header])
    for year, dat in zip(times, data):
        txt+=str(year)+', '+str(dat)+'\n'

    print(txt)
    print('Saving ', out_fn)
    sh = open(out_fn, 'w')
    sh.write(txt)
    sh.close()


def get_path(jobID, field):
    machine = 'pml'
    if machine == 'pml':
        path = '/users/modellers/ledm/workspace/UKESM_EarthSystemSounds/shelves/'+jobID+'_'+field+'.shelve'

    return path



def main():
    jobs = ['u-aw310', ]
    fields = {'TotalIntegratedPrimaryProduction': ('regionless', 'layerless', 'metricless'), }
    units  = {'TotalIntegratedPrimaryProduction': 'Gt/yr', }
    labels = {'TotalIntegratedPrimaryProduction': 'Total Integrated Primary Production', }
    for jobID in jobs:
        for field, data_key in fields.items():
            path = get_path(jobID, field)
            data = load_shelve(path, data_key)
            save_as_csv(field, jobID, units[field], labels[field], data)
main()
