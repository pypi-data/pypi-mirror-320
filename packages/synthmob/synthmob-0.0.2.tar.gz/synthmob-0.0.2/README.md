
# SynthMob: A Framework for Generating Synthetic High Frequency Mobility Data

SynthMob is a framework designed to help the generation of synthetic mobility data with realistic distributions by combining publicly available geospatial data from multiple sources. The framework integrates population and building data, points of interest (POIs), and road network data to compute synthetic origin-destination pairs and simulate movement patterns.

No deep learning algorithm is involved, but it is highly customizable and origin and destination can be a direct expert user input derived from them.

---

## Features

The expected usage is a pipeline shown in the example notebook.
After setting the city, the CRS projection and the timezone:

- **Population and Building Height Data Integration**  
  - Fetches population and building height rasters from [Google Earth Engine](https://earthengine.google.com/).
  - Population data is retreived from [WorldPop](https://developers.google.com/earth-engine/datasets/catalog/WorldPop_GP_100m_pop_age_sex)
  - Building height is retrieved from [GHSL](https://developers.google.com/earth-engine/datasets/catalog/JRC_GHSL_P2023A_GHS_BUILT_H)
  - Assigns inhabitants from raster pixels to buildings using building volume as a disaggregating factor.

- **Buildings, POIs and Road Network Extraction**  
  - Retrieves building footprints, POIs, and road network data from [Overture Maps Foundation](https://overturemaps.org/).  
  - Builds a proximity graph for POIs based on k-nearest neighbors (kNN) above a defined distance threshold (anything below is fully connected).  

- **Centrality and Importance Computation**  
  - Computes the **betweenness centrality** of POIs on the proximity graph.  
  - Determines POI importance using centrality, area, and category frequency.  

- **Origin-Destination Mapping**  
  - Connects computed origins (home locations) and destinations (important POIs) using paths on the road network.  

- **Synthetic Mobility Data Generation**  
  - Generates realistic synthetic pings:
    - Power-law distributions for speed, spatial distance, temporal delta, number of pings per user.  
  - Highly customizable and parametric:
    - Parametric control of movement peaks during morning and evening rush hours.
    - Possibility of setting max pings per user to increase density or generate seasonality.

---

## Installation

1. **Install from registry**  
   ```bash
   pip install synthmob
   ```

2. **Set Up Google Earth Engine**  
   Authenticate on Google Earth Engine and create a project name (required by Google Earth Engine quota policy)

3. **Run!**

## Future Developments

 - A simpler Colab notebook and a Dockerfile will be available soon.
 - There may be some updates on POI importance computation and graph compression.
 - I will make seasonality a parameter and compress the pipeline further.
 - I will start generating some large scale synthetic dataset for areas I am interested in (in case I will share them on huggingface)


## Contributing

I welcome contributions to SynthMob! Feel free to open issues or submit pull requests to improve the framework.

---

## License

SynthMob is licensed under the [MIT License](LICENSE).

---

## Acknowledgments

- [Google Earth Engine](https://earthengine.google.com/)  
- [Overture Maps Foundation](https://overturemaps.org/)
- Contributors to open-source geospatial libraries.

---

## Contact

If you have any questions or need further assistance, feel free to open an issue on GitHub or contact me at lwdovico@protonmail.com

Happy Mapping!