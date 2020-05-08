

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

        # R1
        'u-bc179': 'UKESM1 Historical run (2250)',
        'u-be509': 'UKESM1 SSP1 2.6 R1 (2250)',
        'u-be537': 'UKESM1 SSP2 4.5 R1 (2250)',
        'u-be647': 'UKESM1 SSP3 7.0 R1 (2250)',
        'u-be653': 'UKESM1 SSP5 8.5 R1 (2250)',
        'u-bh409': 'UKESM1 SSP1 1.9 R1 (2250)',
        'u-bh454': 'UKESM1 SSP4 3.4 R1 (2250)',
        'u-bh456': 'UKESM1 SSP5 3.4-OS R1 (2250)',

        #R2
        'u-bc292': 'UKESM1 Historical run (2165)',
        'u-be606': 'UKESM1 SSP1 2.6 R2 (2165)',
        'u-be679': 'UKESM1 SSP2 4.5 R2 (2165)',
        'u-be690': 'UKESM1 SSP3 7.0 R2 (2165)',
        'u-be693': 'UKESM1 SSP5 8.5 R2 (2165)',
        'u-bh570': 'UKESM1 SSP1 1.9 R2 (2165)',
        'u-bh712': 'UKESM1 SSP4 3.4 R2 (2165)',
        'u-bh744': 'UKESM1 SSP5 3.4-OS R2 (2165)',

        #R3
        'u-bc370': 'UKESM1 Historical run (2120)',
        'u-be682': 'UKESM1 SSP1 2.6 R3 (2120)',
        'u-be683': 'UKESM1 SSP2 4.5 R2 (2120)',
        'u-be684': 'UKESM1 SSP3 7.0 R3 (2120)',
        'u-be686': 'UKESM1 SSP5 8.5 R3 (2120)',
        'u-bh716': 'UKESM1 SSP1 1.9 R3 (2120)',
        'u-bh717': 'UKESM1 SSP4 3.4 R3 (2120)',
        'u-bh718': 'UKESM1 SSP5 3.4-OS R3 (2120)',

        #R4
        'u-bb075': 'UKESM1 Historical run (1960) with new SO2 emissions height',
        'u-be335': 'UKESM1 SSP3 7.0 R4 (1960)',
        'u-be392': 'UKESM1 SSP5 8.5 R4 (1960)',
        'u-be393': 'UKESM1 SSP1 2.6 R4 (1960)',
        'u-be394': 'UKESM1 SSP2 4.5 R4 (1960)',
        'u-bh210': 'UKESM1 SSP1 1.9 R4 (1960)',
        'u-bh254': 'UKESM1 SSP4 3.4 R4 (1960)',
        'u-bh285': 'UKESM1 SSP5 3.4-OS R4 (1960)',

        #R8
        'u-bb277': 'UKESM1 Historical run (2560), with new SO2 emissions height',
        'u-be395': 'UKESM1 SSP3 7.0 R8 (2560)',
        'u-be396': 'UKESM1 SSP5 8.5 R8 (2560)',
        'u-be397': 'UKESM1 SSP1 2.6 R8 (2560)',
        'u-be398': 'UKESM1 SSP2 4.5 R8 (2560)',
        'u-bh807': 'UKESM1 SSP1 1.9 R8 (2560)',
        'u-bh808': 'UKESM1 SSP4 3.4 R8 (2560)',
        'u-bh809': 'UKESM1 SSP5 3.4-OS R8 (2560)',
            
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


all_jobs = ['u-aw310', 'u-az513', 'u-az515', 'u-az524', 'u-bb075', 'u-bb277', 'u-bc179', 'u-bc292', 'u-bc370', 'u-bc470', 'u-bd288', 'u-bd416', 'u-bd483', 'u-be335', 'u-be392', 'u-be393', 'u-be394', 'u-be395', 'u-be396', 'u-be397', 'u-be398', 'u-be509', 'u-be537', 'u-be606', 'u-be647', 'u-be653', 'u-be679', 'u-be682', 'u-be683', 'u-be684', 'u-be686', 'u-be690', 'u-be693', 'u-bf647', 'u-bf656', 'u-bf703', 'u-bh210', 'u-bh254', 'u-bh285', 'u-bh409', 'u-bh454', 'u-bh456', 'u-bh570', 'u-bh717', 'u-bh718', 'u-bh744', 'u-bh807', 'u-bh808', 'u-bh809']

def main():
    jobs = all_jobs

    fields = {'TotalIntegratedPrimaryProduction': ('regionless', 'layerless', 'metricless'), }
    units  = {'TotalIntegratedPrimaryProduction': 'Gt/yr', }
    labels = {'TotalIntegratedPrimaryProduction': 'Total Integrated Primary Production', }
    for jobID in jobs:
        for field, data_key in fields.items():
            path = get_path(jobID, field)
            data = load_shelve(path, data_key)
            save_as_csv(field, jobID, units[field], labels[field], data)

if __name__ == "__main__":
    main()
