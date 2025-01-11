import numpy
import pandas
import haversine
import re
from .utils import WGS, get_in_parallel
from .roads import compute_paths

class odGenerator:
    
    def __init__(self, origins, destinations, road_nodes, sample = None):
        
        assert 'importance' in destinations.columns, 'Destinations must have an importance column'
        
        if sample:
            if type(sample) == float:
                origins = origins.sample(frac = sample)
            else:
                origins = origins.sample(sample)
        
        self.uids = origins['uid'].values
            
        self.origins = origins
        self.destinations = destinations
        
        self.road_nodes = road_nodes
        self.od_pairs = pandas.DataFrame()
        
    def map_to_nodes(self, pts, index_name = 'pts'):
        
        return pts.reset_index(names = index_name)\
                    .sjoin_nearest(self.road_nodes)\
                    .rename(columns = {'index_right' : 'nodes'})
    
    def map_origins(self, kind = 'origins'):
        
        if kind == 'origins':
            
            try:
                
                return self.od_pairs['O'].values
            
            except KeyError:
                    
                mapped_unique_nodes =  self.map_to_nodes(self.origins, 'origins')\
                                            .drop_duplicates('origins')\
                                            .set_index('origins')['nodes']
                
                return self.origins.index.map(mapped_unique_nodes)
        
        elif kind == 'destinations':
            
            assert 'D' in self.od_pairs.columns, 'You must generate the OD pairs before using the destinations'
            
            return self.od_pairs['D'].values
        
        else:
            raise ValueError("kind must be 'origins' or 'destinations'")

    def map_destinations(self, size):
        
        mapped_unique_with_importance = self.map_to_nodes(self.destinations, 'destinations')\
                                            .groupby('nodes')['importance']\
                                            .mean()\
                                            .to_frame('importance').reset_index()
                                            
        mapped_unique_with_importance['importance'] /= mapped_unique_with_importance['importance'].sum()
        
        destination_nodes = numpy.random.choice(mapped_unique_with_importance['nodes'], 
                                                size, p = mapped_unique_with_importance['importance'])
        
        return destination_nodes
            
    def generate_OD_pairs(self, kind = 'origins'):

        get_candidates = lambda c: [int(re.search(r"\d+", col).group()) for col in self.od_pairs.columns if c in col and re.search(r"\d+", col)]
        get_next_col = lambda c: f'{c}{1 + max([0] + get_candidates(c))}'
        
        origins = self.map_origins(kind = kind)
        destinations = self.map_destinations(size = len(origins))
        shuffle_idx = numpy.arange(len(origins))
        
        if kind == 'origins':
            shuffle_idx = numpy.random.permutation(len(origins))
    
        od_pairs = pandas.DataFrame()
        od_pairs['O'] = origins[shuffle_idx]
        od_pairs['D'] = destinations
        od_pairs['index'] = shuffle_idx
        od_pairs = od_pairs.set_index('index').sort_index()
        
        if self.od_pairs.empty:
            self.od_pairs = od_pairs
        else:
            self.od_pairs[get_next_col('O')] = od_pairs['O']
            self.od_pairs[get_next_col('D')] = od_pairs['D']
            
    def get_computable_OD(self, which_destination = 'all', sample = None):
        
        od_pairs = self.od_pairs
        
        if sample:
            if type(sample) == float:
                od_pairs = od_pairs.sample(frac = sample)
            else:
                od_pairs = od_pairs.sample(sample)
        
        if which_destination == 'all':
            ODs = []
            
            for d_col in od_pairs.columns:
                if 'D' in d_col:
                    o_col = d_col.replace('D', 'O')
                    ODs.append(od_pairs[[o_col, d_col]].rename(columns = {o_col : 'O', d_col : 'D'}))
                
            od_concat = pandas.concat(ODs)
        else:
            d_col = which_destination
            o_col = which_destination.replace('D', 'O')
            od_concat = od_pairs[[o_col, d_col]].rename(columns = {o_col : 'O', d_col : 'D'})    
        
        od_clean = od_concat.loc[od_concat['O'] != od_concat['D'], ['O', 'D']].values
        od_reduced = pandas.DataFrame(sorted({frozenset((o, d)) for o, d in od_clean}), 
                                      columns = ['O', 'D'])
            
        return od_reduced.reset_index()\
                         .groupby(['O'])\
                         .agg({'D' : 'unique'})\
                         .reset_index()[['O', 'D']].values

    def get_trips_with_size(self, which_destination = 'all', compute_space = False, sample = None):
        
        od_pairs = self.od_pairs
        
        if sample:
            if type(sample) == float:
                od_pairs = od_pairs.sample(frac = sample)
            else:
                od_pairs = od_pairs.sample(sample)
            
        if which_destination == 'all':
            ODs = []
            
            for d_col in od_pairs.columns:
                if 'D' in d_col:
                    o_col = d_col.replace('D', 'O')
                    ODs.append(od_pairs[[o_col, d_col]].rename(columns = {o_col : 'O', d_col : 'D'}))
                
            od_concat = pandas.concat(ODs)
        else:
            d_col = which_destination
            o_col = which_destination.replace('D', 'O')
            od_concat = od_pairs[[o_col, d_col]].rename(columns = {o_col : 'O', d_col : 'D'})    
            
        nodes_dict = self.road_nodes.to_crs(WGS)['geometry'].to_dict()
        trips = od_concat.groupby(['O', 'D']).size().to_frame('flows')
        
        trips['origin'] = trips.reset_index()['O'].map(nodes_dict).values
        trips['destination'] = trips.reset_index()['D'].map(nodes_dict).values

        trips['olat'] = trips['origin'].apply(lambda x: x.y)
        trips['olng'] = trips['origin'].apply(lambda x: x.x)
        trips['dlat'] = trips['destination'].apply(lambda x: x.y)
        trips['dlng'] = trips['destination'].apply(lambda x: x.x)
        trips = trips.drop(['origin', 'destination'], axis = 1)
        
        if compute_space:
            trips['delta_space'] = trips.apply(lambda x: haversine.haversine((x['olat'], x['olng']), 
                                                                             (x['dlat'], x['dlng'])), axis = 1)
        return trips
    
    def get_paths(self, G, computational_OD):

        drop_consecutive_duplicates = lambda lst: ([x for i, x in enumerate(lst) if i == 0 or lst[i-1] != x])
        
        enlist = lambda lst : [x if type(x) == list else [x] for x in lst]
        ravel_list = lambda lst: [el for x in lst for el in x]
        clean_list = lambda lst : ravel_list(enlist(lst))
        
        iterable_params =  [(G, od_pair, 'travel_time') for od_pair in computational_OD]
        computed_paths = get_in_parallel(compute_paths, iterable_params, 'threading')
        
        paths = {}

        for batch in computed_paths:
            for (o, d), sps in batch.items():
                road_ids = clean_list(drop_consecutive_duplicates(G.es[sps]['id']))
                
                paths[(o, d)] = road_ids
                paths[(d, o)] = road_ids[::-1]
                
        return paths
    
    def assign_paths_to_OD(self, od_pair, paths):
        od_edged = od_pair[od_pair['O'] != od_pair['D']]
        od_edged['edge'] = od_edged.apply(lambda x: paths[(x['O'], x['D'])], axis = 1)
        
        return od_edged
