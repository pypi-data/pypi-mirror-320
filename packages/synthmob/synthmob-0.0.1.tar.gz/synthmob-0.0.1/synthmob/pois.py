import shapely
import numpy
import geopandas

import libpysal
import igraph
import warnings

from scipy.spatial import cKDTree
from .utils import WGS

warnings.filterwarnings('ignore')


def knn_with_min_distance(gdf, k, min_distance):
    """
    Compute k-nearest neighbors for a GeoDataFrame with a minimum distance threshold.
    
    Parameters:
    - gdf: GeoDataFrame with points in a `geometry` column
    - k: Number of neighbors to find
    - min_distance: Minimum distance threshold
    
    Returns:
    - neighbors_dict: Dictionary with point indices as keys and a list of (neighbor_index, distance) as values
    """
    # Extract coordinates from the GeoDataFrame
    coords = numpy.array(list(zip(gdf.geometry.x, gdf.geometry.y)))
    
    # Build KDTree for efficient neighbor search
    tree = cKDTree(coords)
    
    neighbors_dict = {}
    for i, point in enumerate(coords):
        radius = min_distance
        neighbors = []
        
        # Dynamically expand the search radius until at least k valid neighbors are found
        while len(neighbors) < k:
            radius *= 1.5  # Expand the radius
            indices = tree.query_ball_point(point, radius)
            neighbors = [
                (idx, numpy.linalg.norm(point - coords[idx]))
                for idx in indices
                if idx != i and numpy.linalg.norm(point - coords[idx]) > min_distance
            ]
        
        # Sort neighbors by distance and retain the closest k
        neighbors = sorted(neighbors, key=lambda x: x[1])[:k]
        neighbors_dict[i] = neighbors
    
    edges = []
    for i, neighbors in neighbors_dict.items():
        for j, _ in neighbors:
            edges.append((i, j))
            
    return edges

def compute_knn_edges(pois, neighbors = 10):
    
    knn_weights = libpysal.weights.KNN.from_dataframe(pois[['geometry']], k = neighbors, use_index = True)
    knn_nx = knn_weights.to_networkx()
    knn_igraph = igraph.Graph.from_networkx(knn_nx)
    
    knn_edges = numpy.array(knn_igraph.get_edgelist())
    
    return knn_igraph, knn_edges

def compute_distance_edges(pois, distance = 30):
    
    dist_weights = libpysal.weights.DistanceBand.from_dataframe(pois[['geometry']], threshold = distance, use_index = True)
    dist_nx = dist_weights.to_networkx()
    dist_igraph = igraph.Graph.from_networkx(dist_nx)
    
    dist_edges = numpy.array(dist_igraph.get_edgelist())
    
    return dist_igraph, dist_edges

def compute_proximity_graph(pois, neighbors = 10, distance = 30, knn_min_distance = True):
    pg = pois['geometry']
    
    if knn_min_distance:
        # it normalizes a bit the connectivity of the graph
        knn_edges = knn_with_min_distance(pois, k = neighbors, min_distance = distance)
    else:
        # knn may result in a less connected graph in high density areas
        _, knn_edges = compute_knn_edges(pois, neighbors = neighbors)
        
    _, dist_edges = compute_distance_edges(pois, distance = distance)
    
    edges = numpy.unique(numpy.concatenate([knn_edges, dist_edges]), axis = 0)
    
    graph = igraph.Graph(directed = False)
    graph.add_vertices(len(pois))
    graph.add_edges(edges)
    graph = graph.simplify()
    
    graph_edges = numpy.array(graph.get_edgelist())
    
    edges_geoms = geopandas.GeoDataFrame(geometry = [shapely.geometry.LineString([pg[s], pg[t]]) for s, t in graph_edges], 
                                         crs = pois.crs)
    edges_geoms['source'] = graph_edges[:, 0]
    edges_geoms['target'] = graph_edges[:, 1]
    edges_geoms['length'] = edges_geoms.length
    
    graph.es['length'] = edges_geoms['length'] + 1
    
    return graph, edges_geoms

def parametric_poi_importance(pois, 
                              centrality_eps = 0.85, # it's a balancing ratio
                              area_eps = 0.13, # it's a balancing ratio
                              category_eps = 0.02, # it's a balancing ratio
                              school_eps = 1.1, # it's an increasing log factor
                              health_eps = 1.2, # it's an increasing log factor
                              transport_eps = 1.3 # it's am increasing log factor
                              ):

    centrality_factor = (pois['centrality'] / pois['centrality'].max())
    area_factor = (pois['b_area'] / pois['b_area'].max())
    category_factor = (pois['cat_frequency'] / pois['cat_frequency'].max())

    importance = centrality_eps * centrality_factor + area_eps * area_factor + category_eps * category_factor
    logged_importance = numpy.log(importance + 1)
    max_importance = importance.max()

    school = pois['categories'].apply(lambda x: ('school' in str(x)))
    health = pois['categories'].apply(lambda x: ('health' in str(x)) or ('hospital' in str(x)))
    transport = pois['categories'].apply(lambda x: ('transport' in str(x)) or ('station' in str(x)) or ('airport' in str(x)))

    importance.loc[school] = school_eps * numpy.exp(logged_importance.loc[school]) - 1
    importance.loc[health] = health_eps * numpy.exp(logged_importance.loc[health]) - 1
    importance.loc[transport] = transport_eps * numpy.exp(logged_importance.loc[transport]) - 1

    importance /= max_importance
    importance = importance.clip(0, 1)
    
    return importance

class POIsProcessor():
    
    def __init__(self, pois, metric_projection):
        
        self.pois = pois
        self.metric_projection = metric_projection
        self.add_category_frequency()
        
    def add_category_frequency(self):
        
        pois_categories_count = self.pois['categories'].value_counts()
        self.pois['cat_frequency'] = self.pois['categories'].map(pois_categories_count)\
                                                            .fillna(pois_categories_count.min())
        self.pois['cat_frequency'] /= pois_categories_count.sum()
        
    def add_building_area(self, buildings):
        
        area_pois = self.pois.to_crs(self.metric_projection)\
                        .sjoin(buildings.to_crs(self.metric_projection), how = 'left')['area']\
                        .fillna(1)\
                        .sort_values(ascending = False)
                        
        self.pois['b_area'] = self.pois.index.map(area_pois[~area_pois.index.duplicated(keep = 'first')])

    def get_poi_centrality(self, neighbors = 4, distance = 15, knn_min_distance = True):
        
        self.poi_igraph, self.edge_geoms =  compute_proximity_graph(self.pois.to_crs(self.metric_projection), 
                                                                    neighbors = neighbors, 
                                                                    distance = distance, 
                                                                    knn_min_distance = knn_min_distance)
                                            
        self.edge_geoms = self.edge_geoms.to_crs(WGS)
        
        # it may take a while if the poi graph is dense and numerous
        self.pois['centrality'] = self.poi_igraph.betweenness(weights = 'length')
        
    def get_poi_importance(self, centrality_eps = 0.85, area_eps = 0.13, category_eps = 0.02, 
                                 school_eps = 1.1, health_eps = 1.2, transport_eps = 1.3):
        
        assert 'centrality' in self.pois.columns, 'You must compute the centrality first'
        assert 'b_area' in self.pois.columns, 'You must compute the building area first'
        
        self.pois['importance'] = parametric_poi_importance(self.pois, 
                                                            centrality_eps = centrality_eps, 
                                                            area_eps = area_eps, 
                                                            category_eps = category_eps, 
                                                            school_eps = school_eps, 
                                                            health_eps = health_eps, 
                                                            transport_eps = transport_eps)
        
