from osmnx.simplification import simplify_graph
import shapely
import geopandas
import igraph
import momepy

DEFAULT_SPEED =   {'footway': 30,
                    'residential': 50,
                    'service' : 25,
                    'unknown': 20,
                    'driveway': 20,
                    'tertiary': 90,
                    'parkingAisle': 20,
                    'cycleway': 20,
                    'steps': 30,
                    'primary': 200,
                    'unclassified': 25,
                    'secondary': 100,
                    'livingStreet': 20,
                    'motorway': 500,
                    'pedestrian': 20,
                    'track': 20,
                    'trunk': 400,
                    'default': 20}

class RoadProcessor():
    
    def __init__(self, roads, metric_projection):
        
        self.roads = roads
        self.metric_projection = metric_projection
        self.add_speed()
        
    def add_speed(self, speed_map = None):
        
        speed_category_map = {}
        
        if speed_map is None:
            speed_map = DEFAULT_SPEED
            
        speed_category_map.update(speed_map)
                    
        self.roads['speed'] = self.roads['road'].map(speed_category_map)\
                                                .fillna(speed_category_map.get('default', 20))
    
    def roads_fragmenter(self):
        
        roads = self.roads.to_crs(self.metric_projection)
        segment = lambda x: [shapely.geometry.LineString((x, y)) for x, y in zip(x['geometry'].coords, x['geometry'].coords[1:])]
        exploded_roads = roads.apply(segment, axis = 1).explode()

        exploded_graph = geopandas.GeoDataFrame(geometry = exploded_roads.values, crs = roads.crs)\
                                  .assign(id = exploded_roads.index)\
                                  .reset_index(drop = True)
                                  
        exploded_graph['speed'] = exploded_roads.index.map(roads['speed']).fillna(20).values
        exploded_graph['length'] = exploded_graph.length.values
        exploded_graph['travel_time'] = ((exploded_graph['length'] / 1000) / exploded_graph['speed']) * 3600
        
        return exploded_graph

    def get_primal_graph(self, gdf_graph):
        
        primal_graph = momepy.gdf_to_nx(gdf_graph, approach = 'primal')
        
        return primal_graph
    
    def simplify_graph(self, nx_graph):
        
        return simplify_graph(nx_graph.to_directed()).to_undirected()

    def make_igraph(self, nx_graph):
        
        ig_graph = igraph.Graph.from_networkx(nx_graph)
        del ig_graph.es['mm_len']
        del ig_graph.es['_nx_multiedge_key']
        
        ig_graph.vs['geometry'] = [shapely.geometry.Point(pt) for pt in ig_graph.vs['_nx_name']]
        del ig_graph.vs['_nx_name']
        
        return ig_graph

    def get_largest_component(self, ig_graph):
        
        largest_component = sorted(ig_graph.connected_components(), key = lambda x: -len(x))[0]
        return ig_graph.subgraph(largest_component)
    
    def get_graph(self):
        
        gdf_graph = self.roads_fragmenter()
        nx_graph = self.get_primal_graph(gdf_graph)
        nx_graph = self.simplify_graph(nx_graph)
        ig_graph = self.make_igraph(nx_graph)
        ig_graph = self.get_largest_component(ig_graph)
        return ig_graph
    
def compute_paths(graph, od_pair, attr):
    
    from_node, to_nodes = od_pair
    to_nodes = tuple(to_nodes.astype(int).tolist())
    shortest_paths = graph.get_shortest_paths(from_node, to_nodes, weights=attr, output="epath")
    return {(from_node, to_node) : sp for to_node, sp in zip(to_nodes, shortest_paths)} 
