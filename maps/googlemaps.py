import googlemaps
import os
import folium
import polyline
import numpy as np
import pandas as pd
from sql.db import query
from shapely.geometry import Polygon
from math import ceil
import time



class Place():
    def __init__(self):
        self.lat = None
        self.lon = None
        self.address = "You are Here!"
        self.gmaps = googlemaps.Client(key=os.environ["gcp_key"])


    def search(self, query, qry_type):

        if qry_type == "latLon":
            self.lat = float(query["lat"])
            self.lon = float(query["lon"])
            
            try:
                self.address = query["address"]
            except KeyError:
                pass
                


        elif qry_type == "txt":
            place_search = self.gmaps.places(query)

            if place_search["status"] == "OK":
                self.lat = place_search["results"][0]["geometry"]["location"]["lat"]
                self.lon = place_search["results"][0]["geometry"]["location"]["lng"]
                self.address = place_search["results"][0]["name"]







class Directions(Place):
    def __init__(self, origin=None, dest=None):
        self.origin = origin
        self.dest = dest
        self.gmaps = googlemaps.Client(key=os.environ["gcp_key"])


    def get_routes(self):
        
        directions_result = self.gmaps.directions(
            (self.origin.lat, self.origin.lon),
            (self.dest.lat, self.dest.lon),
            mode="driving", alternatives=True)
        
        # placeholder dict for route information: path, travel time, 
        route_lines = {}

        # append the route line from google maps directions result
        route_lines["polyline"] = [each["overview_polyline"]["points"] for each in directions_result]

        # retrieve distance of each line
        route_lines["distance"] = [each["legs"][0]["distance"]["value"] for each in directions_result]

        # retrieve travel time of each route
        route_lines["travel_time"] = [each["legs"][0]["duration"]["value"] for each in directions_result]

        # create a query class object
        db_query = query()

        # calculate the number of crashes on each route
        route_lines["crashes"] = [db_query.get_route_crashes(x) for x in [each["overview_polyline"]["points"] for each in directions_result]]

        
        # create dataframe for route info
        df = pd.DataFrame(route_lines)
        
        #reference: https://stackoverflow.com/questions/47340518/list-append-in-pandas-cell
        #reference: https://stackoverflow.com/questions/12906812/error-can-only-concatenate-list-not-str-to-list
        #reference: https://stackoverflow.com/questions/42964724/pandas-filter-out-column-values-containing-empty-list
        
        #reference: https://stackoverflow.com/questions/5518435/python-fastest-way-to-create-a-list-of-n-lists
        
        # insert empty list into "tags" column as placeholder
        df["tags"] = np.empty((df.shape[0], 0)).tolist()

        # tag the routes as shortest, fastest, and safest
        df.at[df.loc[df["distance"] == df["distance"].min()].index[0], "tags"] += ["shortest"]
        df.at[df.loc[df["travel_time"] == df["travel_time"].min()].index[0], "tags"] += ["fastest"]
        df.at[df.loc[df["crashes"] == df["crashes"].min()].index[0], "tags"] += ["safest"]


        return df[df['tags'].apply(lambda x: len(x)) > 0]
        



class Map():
    
    def __init__(self, origin, dest = None, route_df = None):
        
        self.origin = origin
        self.dest = dest
        self.tile=os.environ["mapbox_tile"]
        self.attr = "MapBox"
        
        if self.dest is None:
            pass
            
        else:
            # extract values from supplied padas dataframe
            self.polyline = route_df.at[0, "polyline"]
            self.crash_count = route_df.at[0, "crashes"]
            self.travel_time = route_df.at[0, "travel_time"]
            self.distance = route_df.at[0, "distance"]

            # decode lat/lon points of each route
            self.route_pts = polyline.decode(self.polyline)

            # placeholder for storing the route and map bounds 
            self.route_bounds = []

            self.hotspots = None
    
    
    def calc_route_bounds(self):
        
        # calculate route bounds
        route_bounds = Polygon(self.route_pts).bounds

        # bounds calculated from shapely are returned in the (xmin, ymin, xmax, ymax) form
        # we create (lat, lon) tuple objects before appending it to the bounds list

        # append to route bounds placeholder
        self.route_bounds.append([route_bounds[0], route_bounds[1]])
        self.route_bounds.append([route_bounds[2], route_bounds[3]])
        
        
    def get_hotspots(self):

        # create a query class object
        db_query = query()

        crashes = db_query.get_crash_hotspots(self.polyline, limit=min(10, ceil(self.distance/1000)))

        
        # reference: https://stackoverflow.com/questions/35491274/pandas-split-column-of-lists-into-multiple-columns
        # reference: https://stackoverflow.com/questions/4703390/how-to-extract-a-floating-number-from-a-string
        # reference: https://stackoverflow.com/questions/20829748/pandas-assigning-multiple-new-columns-simultaneously
        
        # if accidents are found on the route
        if (crashes.shape[0] != 0):
            crashes = crashes.assign(lon=None)
            crashes = crashes.assign(lat=None)

            crashes[["lon", "lat"]] = crashes["centroid"].str.findall(r'-?\d+\.\d+').to_list()

            crashes = crashes.drop('centroid', 1)

            self.hotspots=crashes
        
        
        
    
    def plot_folium(self):
        
        # case when map is being rendered for just the current user coordinates
        if self.dest is None:
            
            local_map = folium.Map(location=(self.origin.lat, self.origin.lon),
                                   tiles=self.tile,
                                   zoom_start=15, attr=self.attr)
            
            folium.Marker((self.origin.lat, self.origin.lon), tooltip = "Current Location",
                          popup= folium.map.Popup(self.origin.address, show=True)).add_to(local_map)
            
            return local_map._repr_html_()
         
        # case when plotting directions b/w two points
        else:
            
            # calculate map bounds for supplied routes
            self.calc_route_bounds()
            
            # draw a map centered around mean lat/lon of origin and destination
            route_map = folium.Map(location=[np.mean([self.origin.lat, self.dest.lat]), 
                                           np.mean([self.origin.lon, self.dest.lon])], 
                                  zoom_start=1, 
                                   tiles=self.tile,
                                  attr=self.attr
                                  )


            # display text for the route
            polyline_html = ("Distance: " + 
                                str(round(self.distance/1000, 1)) +
                                " Kms<br>" + "Travel Time: " + 
                                str(time.strftime('%H:%M:%S', time.gmtime(self.travel_time)))
                               )


            # plot the route
            folium.PolyLine(self.route_pts, opacity = 1,
                           popup = folium.map.Popup(polyline_html, max_width=2650)).add_to(route_map)
            
            # origon marker
            folium.Marker((self.origin.lat, self.origin.lon), tooltip="Origin", 
                          popup=folium.map.Popup(self.origin.address, show=True)).add_to(route_map)
            
            # destination marker
            folium.Marker((self.dest.lat, self.dest.lon), tooltip="Destination", 
                          popup=folium.map.Popup(self.dest.address, show = True)).add_to(route_map)
            
            # calculate crash hotspots for route
            self.get_hotspots()
            
            # add hotspots to the map
            # if hotspots are found in database
            
            if self.hotspots is not None:
                for index, row in self.hotspots.iterrows():
    
                    folium.CircleMarker(location=[row["lat"], row["lon"]],
                                radius=row["crash_count"]/4,
                                tooltip=str(row["crash_count"]) + " accident events",
                                fill=True, color = "red").add_to(route_map)
            
            # fit route bounds
            route_map.fit_bounds(self.route_bounds)
            

            return route_map._repr_html_()
		



	


