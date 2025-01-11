import ee
import geomob
import shapely
from tqdm import tqdm
from pyproj import CRS
import tempfile

import xarray
import xrspatial
import rasterio
import dask.array
from rioxarray.merge import merge_arrays

class LargeRasterExtractor():
    
    def __init__(self, ee_project_name, xee_dataset, var, date_range = None):
        
        ee.Authenticate()
        ee.Initialize(project = ee_project_name, opt_url='https://earthengine-highvolume.googleapis.com')
        
        assert (date_range is None) or (len(date_range) == 2) and \
                isinstance(date_range, tuple), "Provide a tuple (min_date, max_date) or None"
                
        self.date_range = date_range
        self.var = var
        
        asset_info = ee.data.getInfo(xee_dataset)
        
        if asset_info.get('type', 'IMAGE_COLLECTION') != 'IMAGE_COLLECTION':
            xee_dataset = [ee.Image(xee_dataset)]
            
        self.xee_dataset = ee.ImageCollection(xee_dataset)
    
        if self.date_range:
            self.xee_dataset = self.xee_dataset.filterDate(*self.date_range)
        
        self.xee_dataset = self.xee_dataset.select(self.var)
        
        self.ee_projection = self.xee_dataset.first().select(self.var).projection().getInfo()
        
        try:
            self.source_crs = self.ee_projection['crs']
        except KeyError:
            self.source_crs = self.ee_projection['wkt']
        
    def bbox_define(self, bbox, chunk_meters = 10000, project_on_crs = None):
        
        source_crs = CRS.from_string(self.source_crs)
        unit = source_crs.axis_info[0].unit_name
        
        self.bbox_shape = geomob.gpd_fromlist([shapely.geometry.box(*bbox)])
        
        if project_on_crs is None and 'm' in unit:
            project_on_crs = source_crs

        self.tessellate = geomob.sq_tessellate(self.bbox_shape, 
                                               chunk_meters, 
                                               project_on_crs=project_on_crs).bounds.values
            
    def collect(self, lat = 'lat', lon = 'lon'):
            
        scale = self.ee_projection['transform'][0]
    
        xarray_datasets = []
        
        # I avoided parallel calls to the API for simplicity
        for bound in tqdm(self.tessellate):
            aoi = ee.Geometry.Rectangle(*bound)
            
            variable_extracted = xarray.open_dataset(self.xee_dataset, 
                                                     engine='ee', 
                                                     crs=self.source_crs, 
                                                     geometry=aoi, 
                                                     chunks=None, 
                                                     scale=scale)[self.var]
            
            xarray_datasets.append(variable_extracted)
            
        self.patches = [r.rename({lon : 'x', lat : 'y'}).transpose('time', 'y', 'x') for r in xarray_datasets]

    def merge_patches(self, processing_func, crs = 'EPSG:4326'):
        
        patches_processed = list(map(processing_func, self.patches))
        
        reprojection = lambda x: x.rio.write_crs(self.source_crs).rio.reproject(geomob.UNIVERSAL_CRS)
        reprojected_patches = list(map(reprojection, patches_processed))
        
        merged_data = merge_arrays(dataarrays = reprojected_patches, 
                                   crs = geomob.UNIVERSAL_CRS, 
                                   nodata = 0)
        
        self.merged_data = merged_data.rio.reproject(crs).rio.set_spatial_dims('x', 'y')
        
def join_raster_to_tess(raster, tiles, aggr_functions = ['sum', 'mean']):
    
    with tempfile.NamedTemporaryFile(suffix='.tiff') as tmpfile:
        raster_path = tmpfile.name
        raster.rio.to_raster(raster_path)
        
        base_raster = xarray.open_dataset(raster_path)\
                            .chunk({'band' : 1, 'x': 2048, 'y': 2048})\
                            .to_dataarray()\
                            .squeeze()\
                            .rio\
                            .clip_box(*tiles.total_bounds)

    raster = rasterio.features.rasterize(
                                        [tuple(reversed(x)) for x in tiles['geometry'].items()],
                                        out_shape=base_raster.rio.shape,
                                        transform=base_raster.rio.transform(),
                                        fill=-1,
                                        all_touched=False, dtype='float64')

    fields_rasterized_xarr = base_raster.copy()
    fields_rasterized_xarr.data = dask.array.from_array(raster, chunks=base_raster.data.chunksize)

    agg_by_tile = xrspatial.zonal_stats(fields_rasterized_xarr, base_raster, stats_funcs= aggr_functions)\
                           .compute()\
                           .fillna(0)\
                           .astype(int)\
                           .set_index('zone')
    
    if -1 in agg_by_tile.index:
        agg_by_tile = agg_by_tile.drop(-1)
        
    return tiles.join(agg_by_tile)