# ===============================================================================
# Copyright 2018 dgketchum
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================

import os

import ee


def add_doy(image):
    """ Add day-of-year image """
    mask = ee.Date(image.get('system:time_start'))
    day = ee.Image.constant(image.date().getRelative('day', 'year')).clip(image.geometry())
    i = image.addBands(day.rename('DOY')).int().updateMask(mask)
    return i


def get_world_climate(proj):
    n = list(range(1, 13))
    months = [str(x).zfill(2) for x in n]
    parameters = ['tavg', 'tmin', 'tmax', 'prec']
    combinations = [(m, p) for m in months for p in parameters]

    l = [ee.Image('WORLDCLIM/V1/MONTHLY/{}'.format(m)).select(p).resample('bilinear').reproject(crs=proj['crs'],
                                                                                                scale=30) for m, p in
         combinations]
    # not sure how to do this without initializing the image with a constant
    i = ee.Image(l)
    return i


def get_qa_bits(image, start, end, qa_mask):
    pattern = 0
    for i in range(start, end - 1):
        pattern += 2 ** i
    return image.select([0], [qa_mask]).bitwiseAnd(pattern).rightShift(start)


def mask_quality(image):
    QA = image.select('pixel_qa')
    shadow = get_qa_bits(QA, 3, 3, 'cloud_shadow')
    cloud = get_qa_bits(QA, 5, 5, 'cloud')
    cirrus_detected = get_qa_bits(QA, 9, 9, 'cirrus_detected')
    return image.updateMask(shadow.eq(0)).updateMask(cloud.eq(0).updateMask(cirrus_detected.eq(0)))


def ls57mask(img):
    sr_bands = img.select('B1', 'B2', 'B3', 'B4', 'B5', 'B7')
    mask_sat = sr_bands.neq(20000)
    img_nsat = sr_bands.updateMask(mask_sat)
    mask1 = img.select('pixel_qa').bitwiseAnd(8).eq(0)
    mask2 = img.select('pixel_qa').bitwiseAnd(32).eq(0)
    mask_p = mask1.And(mask2)
    img_masked = img_nsat.updateMask(mask_p)
    mask_sel = img_masked.select(['B1', 'B2', 'B3', 'B4', 'B5', 'B7'], ['B2', 'B3', 'B4', 'B5', 'B6', 'B7'])
    mask_mult = mask_sel.multiply(0.0001).copyProperties(img, ['system:time_start'])
    return mask_mult


def ls8mask(img):
    sr_bands = img.select('B2', 'B3', 'B4', 'B5', 'B6', 'B7')
    mask_sat = sr_bands.neq(20000)
    img_nsat = sr_bands.updateMask(mask_sat)
    mask1 = img.select('pixel_qa').bitwiseAnd(8).eq(0)
    mask2 = img.select('pixel_qa').bitwiseAnd(32).eq(0)
    mask_p = mask1.And(mask2)
    img_masked = img_nsat.updateMask(mask_p)
    mask_mult = img_masked.multiply(0.0001).copyProperties(img, ['system:time_start'])
    return mask_mult


def ndvi5():
    l = ee.ImageCollection('LANDSAT/LT05/C01/T1_SR').map(lambda x: x.select().addBands(
        x.normalizedDifference(['B4', 'B3'])))
    return l


def ndvi7():
    l = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR').map(lambda x: x.select().addBands(
        x.normalizedDifference(['B4', 'B3'])))
    return l


def ndvi8():
    l = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR').map(lambda x: x.select().addBands(
        x.normalizedDifference(['B5', 'B4'])))
    return l


def ls5_edge_removal(lsImage):
    inner_buffer = lsImage.geometry().buffer(-3000)
    buffer = lsImage.clip(inner_buffer)
    return buffer


def period_stat(collection, start, end):
    c = collection.filterDate(start, end)
    return c.reduce(
        ee.Reducer.mean().combine(reducer2=ee.Reducer.minMax(),
                                  sharedInputs=True))


if __name__ == '__main__':
    pass
# ========================= EOF ====================================================================

