from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from geomob import random_points_in_polygon, gpd_fromlist

from .utils import WGS, get_in_parallel
import warnings

import pandas
import numpy

warnings.filterwarnings('ignore')

def fill_class(df, nan_tolerance = 0.75, feature_to_fill = 'class', approach = 'random_forest', neighbors = 5):

    if approach == 'random_forest':
        model = RandomForestClassifier(n_estimators=100, random_state = 42)
    elif approach == 'knn':
        assert neighbors is not None and neighbors > 0, 'Number of neighbors must be a defined integer with knn'
        model = KNeighborsClassifier(n_neighbors=neighbors)
    
    df = df.copy(deep = True)
    nan_class = df[feature_to_fill].isna()
    nan_ratio = nan_class.sum() / len(df)

    if nan_ratio > nan_tolerance:

        df_available = df.loc[~nan_class, ['lat', 'lng', feature_to_fill]]
        df_unavailable = df.loc[nan_class, ['lat', 'lng']]

        x_train = df_available[['lat', 'lng']].values
        y_train = df_available[feature_to_fill].values

        
        model.fit(x_train, y_train)

        prediction = model.predict(df_unavailable.values)
        df.loc[nan_class, feature_to_fill] = prediction
        
    return df

def filling_inhabitants(builds, tiles_with_height_and_pop,
                        only_residential = True,
                        min_building_height = 3,
                        max_habitable_volume = 0.6, 
                        min_buildings_ratio = 0.15, 
                        max_population_ratio = 0.95):

    if only_residential:
        buildings = builds[builds['class'] == 'residential'].copy(deep = True)
    else:
        buildings = builds.copy(deep = True)
        
    tiles_with_height_and_pop['n_buildings'] = tiles_with_height_and_pop.sjoin(buildings).groupby('index_right').size()

    buildings = buildings.sjoin(tiles_with_height_and_pop.fillna(0))
    buildings['volume'] = buildings['area'] * buildings['height'].clip(min_building_height, None)

    # from 0.4 to 0.6 of the volume is habitable
    # the following assigns an higher (towards 60% of volume) habitability to smaller buildings
    # and a lower (towards 40% of volume) habitability to bigger buildings
    normalized_volume = (buildings['volume'] - buildings['volume'].min()) / (buildings['volume'].max() - buildings['volume'].min())
    habitable_ratios = (1 - ((1-(max_habitable_volume + 0.1)) + numpy.exp(normalized_volume) * 0.1)).clip(0, max_habitable_volume)

    buildings['habitable_volume'] = buildings['volume'] * habitable_ratios

    # assign a building to its most populated and highest building tile
    buildings = buildings.reset_index()\
                        .sort_values(['index', 'height', 'pop'], ascending = False)\
                        .drop_duplicates('index', keep = 'first')\
                        .set_index('index')\
                        .sort_index()

    pop_habitability_per_tile = buildings.groupby('index_right').agg({'pop' : 'first', 'habitable_volume' : 'sum'})
    pop_habitability_per_tile['pop_density'] = pop_habitability_per_tile['pop'] / pop_habitability_per_tile['habitable_volume']

    buildings['pop_density'] = buildings['index_right'].map(pop_habitability_per_tile['pop_density'].fillna(0))
    buildings['inhabitants'] = buildings['pop_density'] * buildings['habitable_volume']
    buildings = buildings.drop('index_right', axis = 1)

    outilers = (((buildings['inhabitants'] > buildings['inhabitants'].quantile(max_population_ratio)) | \
                 (buildings['pop_density'] > buildings['pop_density'].quantile(max_population_ratio))) & \
                (buildings['n_buildings'] < buildings['n_buildings'].quantile(min_buildings_ratio)))

    outlier_buildings = buildings[outilers].drop(['pop_density', 'pop'], axis = 1)
    inlier_buildings = buildings[~outilers][['geometry', 'pop_density', 'pop']]

    new_columns = {x : 'first' for x in buildings.columns}
    new_columns.update({'pop_density' : 'mean', 'pop' : 'mean'})
    del new_columns['inhabitants']

    fixed_outliers = outlier_buildings.sjoin_nearest(inlier_buildings)\
                                      .drop('index_right', axis = 1)\
                                      .groupby('index_left')\
                                      .agg(new_columns)\
                                      .assign(inhabitants = lambda x: x['pop_density'] * x['habitable_volume'])
                                      
    corrected_buildings = pandas.concat([buildings[~outilers], fixed_outliers])\
                                .sort_index()\
                                .assign(inhabitants = lambda x: 1 + x['inhabitants'].round().astype(int))
                            
    return corrected_buildings

def point_filling_geometries(geoms, n_point_feature, concat = True):
    
    """
    WARNING: b must be provided in crs = 'EPSG:4326'
    Generate random i coordinates inside a b polygon.
    It's not optimized for this parallel task. 
    It was originally ideated for generating points in a single polygon.
    But it's good enough for my hardware and this application.
    """
    
    generate_points_by_size = lambda b, i : random_points_in_polygon(gpd_fromlist([b]), i)
    
    gn = geoms[['geometry', n_point_feature]].values
    pts = get_in_parallel(generate_points_by_size, gn)
    
    if concat:
        return pandas.concat(pts, ignore_index=True)
    return pts

class BuildingProcessor():
    
    def __init__(self, buildings, metric_projection):
        
        self.buildings = buildings
        self.metric_projection = metric_projection
        self.add_area_and_centroid()
        
    def add_area_and_centroid(self):
        
        reprojected_buildings = self.buildings['geometry'].to_crs(self.metric_projection)
        centroids = reprojected_buildings.centroid.to_crs(WGS)

        self.buildings['area'] = reprojected_buildings.area
        self.buildings['lat'] = centroids.y
        self.buildings['lng'] = centroids.x
    
    def fill_class_default(self):
        # most of problems are due to not tagged residential buildings
        buildings_filled = fill_class(self.buildings, nan_tolerance=0.75, approach='random_forest')

        return buildings_filled

    def fill_inhabitants_default(self, buildings_filled, tiles_with_height_and_pop):
        # there may be better approaches to this, I just assigned population according to the expected volume
        buildings_inhabitants = filling_inhabitants(buildings_filled, tiles_with_height_and_pop,
                                                    only_residential = True,
                                                    max_habitable_volume = 0.6, 
                                                    min_buildings_ratio = 0.15, 
                                                    max_population_ratio = 0.95)
        return buildings_inhabitants
    
    def get_default_features(self, tiles_with_height_and_pop):
        
        buildings_filled = self.fill_class_default()
        return self.fill_inhabitants_default(buildings_filled, tiles_with_height_and_pop)