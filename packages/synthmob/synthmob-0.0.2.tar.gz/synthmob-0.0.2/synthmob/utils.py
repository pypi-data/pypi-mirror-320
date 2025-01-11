from .spark import load_spark
from .raster import LargeRasterExtractor, join_raster_to_tess
import geomob

from joblib import Parallel, delayed, parallel_backend
from tqdm import tqdm
import geopandas
import shapely
import json

WGS = 'EPSG:4326'

def get_and_save_bbox(aoi_gdf, aoi_path):
    geometry = shapely.geometry.box(*aoi_gdf.union_all().bounds)

    geojson_data = {
        "type": "Feature",
        "geometry": shapely.geometry.mapping(geometry),
        "properties": {}  # Add any attributes if needed
    }
    
    with open(aoi_path, "w") as geojson_file:
        json.dump(geojson_data, geojson_file, indent=4)
        

def get_in_parallel(func, iterable, backend = 'threading'):
    with parallel_backend(backend, n_jobs=-1):
        return Parallel()(delayed(func)(*args) for args in tqdm(iterable, leave=False, position=0))
    
def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def load_resources(n_cores, aoi_path, resources_path):
    
    aoi = geomob.create_geometry(load_json(aoi_path))
    resources_paths = load_json(resources_path)
    
    spark = load_spark(n_cores = n_cores, region_name = 'us-west-2')
    
    aoi_filter = f'st_within(geometry, st_geomfromwkt("{aoi.wkt}"))'
    
    pois = spark.read.format("geoparquet").load(resources_paths['POIS'])\
                                          .filter(aoi_filter)\
                                          .select('geometry', 'categories')\
                                          .toPandas()
    pois['categories'] = pois['categories'].apply(lambda x: x[0])
    pois = geopandas.GeoDataFrame(pois, crs = 'EPSG:4326')
                                          
    roads = spark.read.format("geoparquet").load(resources_paths['ROADS'])\
                                           .filter(aoi_filter)\
                                           .select('geometry', 'road')\
                                           .toPandas()
    roads['road'] = roads['road'].apply(lambda x: eval(x).get('class'))
    roads = geopandas.GeoDataFrame(roads, crs = 'EPSG:4326')
                                           
    build = spark.read.format("geoparquet").load(resources_paths['BUILDINGS'])\
                                           .filter(aoi_filter)\
                                           .select('geometry', 'numfloors', 'class')\
                                           .toPandas()
    build = geopandas.GeoDataFrame(build, crs = 'EPSG:4326')
    
    return {'POIS': pois, 'ROADS': roads, 'BUILDINGS': build, 'AOI' : aoi}

def get_tiles(aoi, metric_projection, meters = 150):
    return geomob.sq_tessellate(geomob.gpd_fromlist([aoi]), meters, project_on_crs = metric_projection)

def load_raster_data(tiles, ee_project_name, raster_path, var, dims_name = {}, aggr_functions = ['sum', 'mean']):
    
    lat = dims_name.get('lat', 'lat')
    lon = dims_name.get('lon', 'lon')
    
    extractor = LargeRasterExtractor(ee_project_name, raster_path, var)
    extractor.bbox_define(tiles.total_bounds, chunk_meters = 10000)
    extractor.collect(lat = lat, lon = lon)
    extractor.merge_patches(lambda x: x.ffill(dim = 'time').isel(time = -1))
    return join_raster_to_tess(extractor.merged_data, tiles, aggr_functions)

def load_pop_data(tiles, ee_project_name):
    return load_raster_data(tiles, ee_project_name,
                            'WorldPop/GP/100m/pop_age_sex', 
                            'population', 
                            dims_name = {'lat' : 'lat', 'lon' : 'lon'},
                            aggr_functions = ['sum'])

def load_height_data(tiles, ee_project_name):
    return load_raster_data(tiles, ee_project_name,
                            'JRC/GHSL/P2023A/GHS_BUILT_H/2018', 
                            'built_height', 
                            dims_name = {'lat' : 'Y', 'lon' : 'X'},
                            aggr_functions = ['mean'])
    
def get_tiles_wph(ee_project_name, aoi, metric_projection):
    
    bbox_tess = get_tiles(aoi, metric_projection)
    pop_by_tile = load_pop_data(bbox_tess, ee_project_name)
    height_by_tile = load_height_data(bbox_tess, ee_project_name)

    bbox_tess['pop'] = pop_by_tile['sum']
    bbox_tess['height'] = height_by_tile['mean']
    
    return bbox_tess