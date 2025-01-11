import pandas
import numpy
import string
import geopandas
from tqdm import tqdm

from .utils import WGS
from .building import point_filling_geometries
from collections import Counter

tqdm.pandas()

def generate_uid(length=40, include_uppercase=False, include_lowercase=True, 
                 include_digits=True, include_special=False):
    
    # Define character sets
    uppercase = string.ascii_uppercase if include_uppercase else ''
    lowercase = string.ascii_lowercase if include_lowercase else ''
    digits = string.digits if include_digits else ''
    special = '!@#$%^&*()_+-=[]{}|;:,.<>?' if include_special else ''
    
    # Combine all allowed characters
    all_chars = uppercase + lowercase + digits + special
    
    if not all_chars:
        raise ValueError("At least one character set must be included")
    
    all_chars = numpy.array(list(all_chars))
    
    get_chars = lambda all_chars, length : list(all_chars[numpy.random.choice(numpy.arange(len(all_chars)), length)])
    # Generate the UID
    length_schema = length // 8
    
    uid = '-'.join([''.join(get_chars(all_chars, length_schema)) for _ in range(length_schema)])
    
    return uid

def generate_uids(n_uids, name_length = 40):
    
    return numpy.array([generate_uid(name_length) for _ in range(n_uids)])

def generate_uid_distribution(uids, peak_alpha, pings_density, max_pings_per_user):
    
    user_dist = numpy.random.pareto(peak_alpha, len(uids)) + 1
    uid_increasing_factor = numpy.random.pareto(peak_alpha, len(uids)) ** pings_density * max_pings_per_user
    
    user_dist = (user_dist - user_dist.min()) / (user_dist.max() - user_dist.min()) * uid_increasing_factor
    user_dist = numpy.clip(user_dist.astype(int), 1, max_pings_per_user)
    
    overflow = user_dist == max_pings_per_user
    correct = user_dist < max_pings_per_user
    user_dist[overflow] = numpy.random.choice(user_dist[correct], len(user_dist[overflow]))
    return user_dist

def generate_timestamps(n_pings, morning_peak = 8, evening_peak = 17, hour_range = (0, 24)):

    ratio_day = 0.50
    hours = numpy.concatenate([numpy.random.normal(morning_peak, 3, int(n_pings * ratio_day) + 1), 
                               numpy.random.normal(evening_peak, 4, int(n_pings * (1 - ratio_day)) + 1)])

    while hours.min() < 0 or hours.max() > 24:
        hours[hours < 0] = hours[hours < 0] + 24
        hours[hours > 24] = hours[hours > 24] - 24
        
    numpy.random.shuffle(hours)
    
    if hour_range[0] <= hour_range[1]:
        # Normal case: range does not cross midnight
        valid_hours = hours[(hours >= hour_range[0]) & (hours < hour_range[1])]
    else:
        # Case where the range crosses midnight
        valid_hours = hours[(hours >= hour_range[0]) | (hours < hour_range[1])]
    
    return numpy.random.choice(valid_hours, n_pings, replace=True)

def generate_time_distribution(total_pings, peak_alpha, pings_density, max_days):
    
    max_hd = 24 * max_days # results in hours
    
    hour_dist = numpy.random.pareto(peak_alpha, total_pings) + 1
    hour_increase_factor = numpy.random.pareto(peak_alpha, total_pings) ** pings_density * max_hd
    
    hour_dist = (hour_dist - hour_dist.min()) / (hour_dist.max() - hour_dist.min()) * hour_increase_factor
    hour_dist = numpy.clip(hour_dist, 0, max_hd)
    
    overflow = hour_dist == max_hd
    correct = hour_dist < max_hd
    hour_dist[overflow] = numpy.random.choice(hour_dist[correct], len(hour_dist[overflow]))
    
    return hour_dist

def generate_space_distribution(total_pings, peak_alpha, pings_density, max_km):
    
    max_meters = 1000 * max_km # processing in meters
    
    space_dist = numpy.random.pareto(peak_alpha, total_pings) + 1
    space_increase_factor = numpy.random.pareto(peak_alpha, total_pings) ** pings_density  * max_meters
    
    space_dist = (space_dist - space_dist.min()) / (space_dist.max() - space_dist.min()) * space_increase_factor
    space_dist = numpy.clip(space_dist, 1, max_meters)
    
    overflow = space_dist == max_meters
    correct = space_dist < max_meters
    
    space_dist[overflow] = numpy.random.choice(space_dist[correct], len(space_dist[overflow]), replace = False)
    
    lower_sixty = space_dist < numpy.quantile(space_dist, 0.75)
    
    space_dist[lower_sixty] = numpy.random.normal(numpy.quantile(space_dist[~lower_sixty], 0.1), 
                                                  space_dist.std() * 3,
                                                  len(space_dist[lower_sixty]))
    
    space_dist = numpy.clip(space_dist, 0, max_meters)
    
    return space_dist / 1000

def correlate_space_with_time(space, time):
    
    # Convert to numpy arrays
    arr1 = numpy.array(space)
    arr2 = numpy.array(time)
    
    n = len(space)
    positions = numpy.arange(n)
    noise_amount = numpy.random.normal(0, 0.9999 * n/4, n)
    new_positions = positions + noise_amount
    
    # Sort and apply
    idx1 = numpy.argsort(arr1)
    idx2 = numpy.argsort(arr2)[numpy.argsort(new_positions)]
    
    # Return reordered lists
    return arr1[idx1], arr2[idx2]

def generate_pings_meta(uids, max_pings_per_user = 5000, 
                              peak_alpha = 2, 
                              pings_density = 2, 
                              max_km = 10, 
                              max_days = 30, 
                              hour_range = (0, 24)):
    
    user_dist = generate_uid_distribution(uids, peak_alpha, pings_density, max_pings_per_user)
    total_pings = user_dist.sum()

    hour_dist = generate_time_distribution(total_pings, peak_alpha, pings_density, max_days)
    space_dist = generate_space_distribution(total_pings, peak_alpha, pings_density, max_km)
    space_dist[space_dist == space_dist.min()] = 0
    
    sd, td = correlate_space_with_time(space_dist, hour_dist)
    
    distribution = pandas.DataFrame([sd, td], index = ['space_delta', 'time_delta']).T
    distribution.index = numpy.random.choice(numpy.arange(len(distribution)), len(distribution), replace = False)
    distribution = distribution.sort_index()
    distribution['speed'] = distribution['space_delta'] / distribution['time_delta']
    
    distribution['uid'] = uids[numpy.random.choice(numpy.arange(len(uids)), total_pings, p = user_dist / total_pings)]
    distribution['timestamp'] = generate_timestamps(total_pings, hour_range = hour_range)
    
    return distribution[distribution['speed'] < 200]
    
def sort_points_along_line_gdf(gdf):
    
    # Extract coordinates
    coords = numpy.array([(point.x, point.y) for point in gdf.geometry])

    # Fit a line through the points using principal component analysis (PCA)
    mean = coords.mean(axis=0)
    centered_coords = coords - mean
    _, _, vh = numpy.linalg.svd(centered_coords, full_matrices=False)
    line_direction = vh[0]  # Direction of maximum variance

    # Project points onto the line
    projections = centered_coords @ line_direction

    # Sort by projections
    gdf['projection'] = projections
    gdf_sorted = gdf.sort_values('projection').drop(columns='projection')
    
    return gdf_sorted

def adjust_geodataframes_content(gdf_list):
    
    if len(gdf_list) < 2:
        return gdf_list

    # Check if first two GDFs share UID/trip_id before comparing
    if gdf_list[0]['uid'].iloc[0] == gdf_list[1]['uid'].iloc[0] and \
       gdf_list[0]['trip_id'].iloc[0] == gdf_list[1]['trip_id'].iloc[0]:
        first_point_first = gdf_list[0].geometry.iloc[0]
        last_point_first = gdf_list[0].geometry.iloc[-1]
        first_point_second = gdf_list[1].geometry.iloc[0]
        
        dist_first_to_first = first_point_first.distance(first_point_second)
        dist_last_to_first = last_point_first.distance(first_point_second)
        
        if dist_last_to_first < dist_first_to_first:
            gdf_list[0] = gdf_list[0].iloc[::-1]

    # Adjust remaining GeoDataFrames
    for i in tqdm(range(len(gdf_list) - 1), total = len(gdf_list) - 1):
        # Only compare if UIDs and trip_ids match
        if gdf_list[i]['uid'].iloc[0] == gdf_list[i + 1]['uid'].iloc[0] and \
           gdf_list[i]['trip_id'].iloc[0] == gdf_list[i + 1]['trip_id'].iloc[0]:
            last_point_current = gdf_list[i].geometry.iloc[-1]
            first_point_next = gdf_list[i + 1].geometry.iloc[0]
            last_point_next = gdf_list[i + 1].geometry.iloc[-1]
            
            dist_to_start = last_point_current.distance(first_point_next)
            dist_to_end = last_point_current.distance(last_point_next)
            
            if dist_to_end < dist_to_start:
                gdf_list[i + 1] = gdf_list[i + 1].iloc[::-1]
    
    return gdf_list

def make_noisy(raw_pings, metric_projection, strength = 100):
    
    pings = raw_pings.to_crs(metric_projection)
    renoise_lat = numpy.random.choice([-1, 1], len(pings)) * strength * numpy.random.pareto(15, len(pings))
    renoise_lng = numpy.random.choice([-1, 1], len(pings)) * strength * numpy.random.pareto(15, len(pings))
    pings['lat'] = pings['geometry'].apply(lambda x: x.y) + renoise_lat
    pings['lng'] = pings['geometry'].apply(lambda x: x.x) + renoise_lng
    pings['geometry'] = geopandas.points_from_xy(pings['lng'], pings['lat'])
    pings = pings.drop(['lat', 'lng'], axis = 1).to_crs(WGS)
    
    return pings

def get_delta_seconds_from_tz(tz):
    midnight_utc = pandas.Timestamp.now().replace(hour = 0, minute = 0, second = 0, microsecond = 0)
    midnight_tz = midnight_utc.tz_localize(tz)
    return midnight_utc.timestamp() - midnight_tz.timestamp()

def get_midnight():
    # today's midnight UTC
    return pandas.Timestamp.now().replace(hour = 0, minute = 0, second = 0, microsecond = 0).timestamp()

def get_random_time(max_days, hour_range, n_timestamps, base_day = None, morning_peak = 8, evening_peak = 17):
    
    if base_day is None:
        
        base_day = get_midnight()
        
    equal_distribution_of_days = numpy.random.uniform(0, max_days, 1).astype(int) * 24 * 60 * 60
    
    timestamps = (generate_timestamps(n_timestamps, 
                                      morning_peak = morning_peak, 
                                      evening_peak = evening_peak, 
                                      hour_range = hour_range) * 3600).astype(int)
    
    return base_day + equal_distribution_of_days + timestamps

class SynthGPS():
    
    def __init__(self, roads, 
                       meter_road_buffer, 
                       metric_projection, 
                       max_pings_per_user = 100):
        
        self.meter_road_buffer = meter_road_buffer
        self.metric_projection = metric_projection
        self.max_pings_per_user = max_pings_per_user
        
        self.length_dist = numpy.array(roads['geometry'].to_crs(self.metric_projection).length)
        
        rv_buffered = roads.assign(geometry = lambda x: x.to_crs(self.metric_projection)\
                                                         .buffer(self.meter_road_buffer)\
                                                         .to_crs(WGS)).fillna(0)

        rv_buffered['max_pings_per_user'] = self.max_pings_per_user

        self.road_pts = point_filling_geometries(rv_buffered, n_point_feature = 'max_pings_per_user', concat = False)
    
    def set_time(self, max_days, hour_range, timezone, base_day = None):
        
        self.max_days = max_days
        self.hour_range = hour_range
        self.timezone = 'UTC' if timezone is None else timezone
        self.base_day = get_midnight() if base_day is None else base_day
                            
    def compute_uid_metadata(self, uids):
            
        uids_metadata = generate_pings_meta(uids, 
                                            max_days = self.max_days, 
                                            max_pings_per_user = self.max_pings_per_user, 
                                            hour_range = self.hour_range)
        
        uids_metadata['day'] = numpy.random.uniform(0, self.max_days, len(uids_metadata)).astype(int)
        
        uids_metadata['timestamp'] = (self.base_day + \
                                      uids_metadata['day'] * 24 * 60 * 60 + \
                                      uids_metadata['timestamp'] * 3600).astype(int)
        
        uids_metadata = uids_metadata.sort_values('timestamp').reset_index(drop = True).drop('day', axis = 1)
        
        return uids_metadata
    
    def get_segment_points(self, num_pts, geom):
        
        return sort_points_along_line_gdf(self.road_pts[geom].sample(num_pts, replace = True))
            
    def get_timestamp_per_uid(self, group_uid_df):
        
        len_uid_df = len(group_uid_df)
        
        starting_timestamp = get_random_time(self.max_days, self.hour_range, 10000, base_day=self.base_day)[:1]
        
        time_distribution = generate_time_distribution(total_pings = len_uid_df + 1, 
                                                       peak_alpha = 2,
                                                       pings_density = 2, 
                                                       max_days = 1) * 60 * 60 # in seconds
        
        sorted_seconds_of_movements = numpy.sort(time_distribution)[:len_uid_df].astype(int)
        
        return starting_timestamp + sorted_seconds_of_movements
        
    def generate_moving_pings(self, trips, noise_strength = 100, filter_speed = 200, get_metrics = False):
        
        uids_metadata = self.compute_uid_metadata(trips['uid'].unique())
        total_pings = uids_metadata.groupby('uid').size()

        trips_hw = trips.set_index('uid').join(total_pings.to_frame('total_pings'))
        trips_hw['edge'] = trips_hw['edge'].apply(lambda x: x if x else None)
        trips_hw = trips_hw.dropna()
        
        trips_hw['total_pings'] = trips_hw['total_pings'].astype(int)
        trips_hw['length_to_trip'] = trips_hw['edge'].apply(lambda x:  numpy.random.pareto(2, len(x)) * self.length_dist[x])\
                                                     .apply(lambda x:  x / x.sum())

        get_point_indexes = lambda x: Counter(sorted(numpy.random.choice(numpy.arange(len(x['length_to_trip'])), 
                                                                        x['total_pings'], 
                                                                        p = x['length_to_trip'],
                                                                        replace = True)))

        extract_geom_count = lambda x: list(zip(x['chosen_index'].values(), 
                                                [x['edge'][i] for i in x['chosen_index']]))
        
        trips_hw['chosen_index'] = trips_hw.apply(get_point_indexes, axis = 1)
        trips_hw['count_geom'] = trips_hw.apply(extract_geom_count, axis = 1)
        
        trips_hw = trips_hw.reset_index()\
                           .reset_index(names = 'trip_id')[['trip_id', 'uid', 'count_geom']]\
                           .explode('count_geom')

        compute_segment_with_id = lambda i, num_pts, geom: self.get_segment_points(num_pts, geom)\
                                                               .assign(trip_id = trips_hw['trip_id'].iloc[i],
                                                                       uid = trips_hw['uid'].iloc[i])

        pings_list = [compute_segment_with_id(i, num_pts, geom) \
                      for i, (num_pts, geom) in tqdm(enumerate(trips_hw['count_geom'].values), 
                                                     total = len(trips_hw), position = 0, leave = False)]

        check_correct_order = adjust_geodataframes_content(pings_list) 

        generated_pings = pandas.concat(check_correct_order, ignore_index = True)\
                                .reset_index(names = 'sequence')\
                                .sort_values(['uid', 'sequence'])\
                                .reset_index(drop = True)
                                
        gen_df = geopandas.GeoDataFrame(uids_metadata[uids_metadata['uid'].isin(generated_pings['uid'].unique())]\
                          .sort_values(['uid', 'timestamp'])\
                          .reset_index(drop = True)\
                          .assign(geometry = generated_pings['geometry']))

        gen_df = make_noisy(gen_df, self.metric_projection, noise_strength)
        
        gen_df['timestamp'] = gen_df.groupby('uid').apply(self.get_timestamp_per_uid, include_groups=False)\
                                                   .explode().reset_index(drop = True)
        
        if get_metrics:
            
            get_time_delta = lambda df: (df['timestamp'] - df['timestamp'].shift()) / 60 / 60
            get_space_delta = lambda df: df['geometry'].distance(df['geometry'].shift()) / 1000           
            
            gen_df['time_delta'] = gen_df.groupby('uid')\
                                        .apply(get_time_delta, include_groups=False)\
                                        .reset_index(level = 0)['timestamp']
                                        
            gen_df['space_delta'] = gen_df.to_crs(self.metric_projection)\
                                        .groupby('uid')\
                                        .apply(get_space_delta, include_groups = False)\
                                        .reset_index(level = 0)[0]
                                        
            gen_df['speed'] = gen_df['space_delta'] / gen_df['time_delta']
            gen_df = gen_df[gen_df['speed'] < filter_speed].reset_index(drop = True)
            
            gen_df['timestamp'] = gen_df['timestamp'].astype(int) + get_delta_seconds_from_tz(self.timezone)
        
        return gen_df

    def generate_raw_static_assets(self, trips, road_nodes, homes_df, build_df, poi_df):
        
        workplaces = sorted(set(trips['D'].values))

        bv_nodes = road_nodes.sjoin_nearest(build_df.to_crs(road_nodes.crs))['index_right']\
                            .groupby(level = 0)\
                            .apply(list)\
                            .to_dict()

        pv_nodes = road_nodes.sjoin_nearest(poi_df.to_crs(road_nodes.crs))['index_right']\
                            .groupby(level = 0)\
                            .apply(list)\
                            .to_dict()

        map_node_to_building = lambda x: build_df.loc[bv_nodes[x], 'geometry'].values.tolist()
        
        working_buildings = pandas.DataFrame([(d, map_node_to_building(d)) for d in workplaces],
                                            columns = ['D', 'geometry'])\
                                .assign(n = 25)\
                                .explode('geometry')

        work_map = pandas.DataFrame(zip(working_buildings['D'], 
                                    point_filling_geometries(working_buildings, n_point_feature = 'n', concat = False)),
                                columns = ['D', 'geometry'])\
                    .groupby('D')['geometry']\
                    .apply(list)\
                    .apply(pandas.concat)\
                    .to_dict()
                    
        home_pts = trips['uid'].map(homes_df.set_index('uid')['geometry']).values.tolist()

        assign_work = lambda x: work_map[x].sample(1)['geometry'].values[0]
        work_pts = trips['D'].progress_apply(assign_work).values.tolist()

        assign_poi = lambda x: poi_df.loc[pv_nodes[x], 'geometry'].sample(1, weights = poi_df['importance']).values[0]
        pois_pts = trips['D'].progress_apply(assign_poi).values.tolist()

        homes = pandas.DataFrame(zip(trips.index, trips['uid'], home_pts), columns = ['index', 'uid', 'geometry'])
        works = pandas.DataFrame(zip(trips.index, trips['uid'], work_pts), columns = ['index', 'uid', 'geometry'])
        pois = pandas.DataFrame(zip(trips.index, trips['uid'], pois_pts), columns = ['index', 'uid', 'geometry'])
        
        return homes, works, pois
    
    def generate_static_pings(self, uid_to_exclude, 
                              homes, works, pois, 
                              homes_ratio = 0.30, workplaces_ratio = 0.30, pois_ratio = 0.30, 
                              home_hour_range = (22, 4), work_hour_range = (9, 17), poi_hour_range = (9, 17),
                              noise_strength = 100):
        
        non_appearing_homes = geopandas.GeoDataFrame(homes[~homes['uid'].isin(uid_to_exclude)], crs = WGS)
        non_appearing_works = geopandas.GeoDataFrame(works[~works['uid'].isin(uid_to_exclude)], crs = WGS)
        non_appearing_pois = geopandas.GeoDataFrame(pois[~pois['uid'].isin(uid_to_exclude)], crs = WGS)
        
        homes_df = non_appearing_homes.sample(frac = homes_ratio, replace = True)
        works_df = non_appearing_works.sample(frac = workplaces_ratio, replace = True)
        pois_df = non_appearing_pois.sample(frac = pois_ratio, replace = True)
        
        home_synthetic_night = make_noisy(homes_df, metric_projection = self.metric_projection, strength = noise_strength)
        work_synthetic_afternoon = make_noisy(works_df, metric_projection = self.metric_projection, strength = noise_strength)
        pois_synthetic_afternoon = make_noisy(pois_df, metric_projection = self.metric_projection, strength = noise_strength)
        
        home_synthetic_night['timestamp'] = get_random_time(self.max_days, home_hour_range, len(home_synthetic_night), 
                                                            base_day=self.base_day,
                                                            morning_peak=home_hour_range[0], evening_peak=home_hour_range[1])
        work_synthetic_afternoon['timestamp'] = get_random_time(self.max_days, work_hour_range, len(work_synthetic_afternoon),
                                                                base_day=self.base_day,
                                                                morning_peak=work_hour_range[0], evening_peak=work_hour_range[1])
        pois_synthetic_afternoon['timestamp'] = get_random_time(self.max_days, poi_hour_range, len(pois_synthetic_afternoon),
                                                                base_day=self.base_day,
                                                                morning_peak=poi_hour_range[0], evening_peak=poi_hour_range[1])
        
        home_synthetic_night['timestamp'] = home_synthetic_night['timestamp'].astype(int) + get_delta_seconds_from_tz(self.timezone)
        work_synthetic_afternoon['timestamp'] = work_synthetic_afternoon['timestamp'].astype(int) + get_delta_seconds_from_tz(self.timezone)
        pois_synthetic_afternoon['timestamp'] = pois_synthetic_afternoon['timestamp'].astype(int) + get_delta_seconds_from_tz(self.timezone)
        
        return home_synthetic_night, work_synthetic_afternoon, pois_synthetic_afternoon