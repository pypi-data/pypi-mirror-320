import sys
import subprocess
import traceback
import tempfile
import numpy as np
import pandas as pd
import argparse 
import fiona
import geopandas as gpd
fiona_drivers = fiona.supported_drivers
import platform 

if platform.system() == 'Linux':
    from vgrid.utils.dggrid4py.interrupt import crosses_interruption, interrupt_cell, get_geom_coords
    from vgrid.utils.dggrid4py import DGGRIDv7, dggs_types

def generate_grid(dggrid_instance,dggs_type, resolution):
    dggrid_gdf = dggrid_instance.grid_cell_polygons_for_extent(dggs_type, resolution, split_dateline=True)
    geojson_path = f"dggrid_{dggs_type}_{resolution}.geojson"
    dggrid_gdf.to_file(geojson_path)
    print(f"GeoJSON saved as {geojson_path}")

def main():
    if platform.system() == 'Linux':
        parser = argparse.ArgumentParser(description='Create a debug EaseGrid based on XYZ vector tile scheme as a GeoJSON file.')
        parser.add_argument('-r', '--resolution', type=int, required=True, help='resolution')
        parser.add_argument('-t', '--dggs_type', choices=dggs_types, help="Select a DGGS type from the available options.")
        parser.add_argument('-b', '--bbox', type=float, nargs=4, help="Bounding box in the format: min_lon min_lat max_lon max_lat (default is the whole world)")
        args = parser.parse_args()        
        dggrid_instance = DGGRIDv7(executable='/usr/local/bin/dggrid', working_dir='.', capture_logs=False, silent=False, tmp_geo_out_legacy=False, debug=False)
        resolution = args.resolution  
        dggs_type = args.dggs_type
        try:
            generate_grid(dggrid_instance,dggs_type, resolution)
        except:
            print('Please ensure that an excutable DGGRID is located at /usr/local/bin/dggrid. Please install DGGRID following instructions from https://github.com/sahrk/DGGRID/blob/master/INSTALL.md'  )
    else: 
        print('dggrid only works on Linux with an excutable DGGRID at /usr/local/bin/dggrid. Please install DGGRID following instructions from https://github.com/sahrk/DGGRID/blob/master/INSTALL.md'  )
 
if __name__ == '__main__':
    main()