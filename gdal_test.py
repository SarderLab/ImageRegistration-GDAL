import json
import os
import subprocess

import large_image_source_gdal
import yaml

os.environ['GDAL_PAM_ENABLED'] = 'NO'

rewrite =True
number=69
images = [{
    'path':'/path/to/image_fixed.tiff',
    'fid':'/path/to/image_fixed.json',
    'gcp':'/path/to/image_fixed.gcp.tif',
    'warp':'/path/to/image_fixed.warp.tif'
},{
    'path': '/path/to/image_moving.tiff',
    'fid': '/path/to/image_moving.json',
    'gcp': '/path/to/image_moving.gcp.tif',
    'warp': '/path/to/image_moving.warp.tif'
}]


for image in images:
    anot = json.load(open(image['fid']))
    labels = {el['label']['value']: el['center']
              for el in anot['annotation']['elements']}
    image['labels'] = labels

multi = {'sources': []}
cmds = []
labels0 = images[0]['labels']
for idx, image in enumerate(images):
    source = {'path': image['path']}
    multi['sources'].append(source)
    if not idx:
        continue
    matches = []
    for key in image['labels']:
        if key in labels0:
            matches.extend(image['labels'][key])
            matches.extend(labels0[key])
    #image['gcp'] = image['path'].split('.')[0] + '.gcp.tiff'
    cmds.append(['tifftools', 'set', '--set', 'ModelTiepointTag:DOUBLE',
                 ','.join(str(val) for val in matches), image['path'],
                 image['gcp'], '--overwrite'])

    if rewrite or not os.path.exists(image['gcp']):
        subprocess.check_call(cmds[-1])
    #image['warp'] = image['path'].split('.')[0] + '.warp.tiff'
    cmds.append(['gdalwarp', '-tps', '-of', 'COG', '-CO', 'COMPRESS=JPEG',
                 '-CO', 'QUALITY=90', '-CO', 'BLOCKSIZE=1024', image['gcp'],
                 image['warp'], '-overwrite'])

    if rewrite or not os.path.exists(image['warp']):
        subprocess.check_call(cmds[-1])
    source['path'] = image['warp']
    ts = large_image_source_gdal.open(image['warp'])
    gt = ts.dataset.GetGeoTransform()
    source['position'] = {
        'x': gt[0],
        'y': gt[3],
        's11': gt[1],
        's12': gt[2],
        's21': gt[4],
        's22': gt[5],
    }
multiyaml = yaml.dump(multi)
print(multiyaml)
open('image.yaml','w').write(multiyaml)
print('done')
