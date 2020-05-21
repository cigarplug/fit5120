import googlemaps
import os
import folium
import polyline
import numpy as np
import pandas as pd
from sql.db import query
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


        # extract map bounds for each route:
        route_lines["bound_ne"] = [list(x["bounds"]["northeast"].values()) for x in directions_result]
        route_lines["bound_sw"] = [list(x["bounds"]["southwest"].values()) for x in directions_result]


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


        # return routes after removing removing rows where tags are empty
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
            self.route_bounds = [route_df.at[0, "bound_sw"], route_df.at[0, "bound_ne"]]


        
        
    # function to extract top vehicles involved in crashes
    def extract_vehicles(self, x):
    
        if x is not None:
            filtered = ["Heavy Vehicle" if v == 'Heavy Vehicle (Rigid) > 4.5 Tonnes' else "Light Commercial Vehicle" if 
                    v == 'Light Commercial Vehicle (Rigid) <= 4.5 Tonnes GVM' else 
                    "Single Trailer Truck" if v == "Prime Mover - Single Trailer"
                    else v for v in x 
                    ]

            # count the number of occurence of eact vehicle type
            top_vehicles = {v: filtered.count(v) for v in set(filtered)}

            # sort, extract top 3
            top_3 = pd.DataFrame(top_vehicles.items(), columns=['vehicle', 'count']).sort_values(by="count", ascending=False).head(3)["vehicle"]

            return ("Watch out for: " + ", ".join(top_3))
        
        else:
            return ("Watch out for:")
            
    
    
    # calculate sex ratio from array
    def sex_ratio(self, x):

        d = {v: x.count(v) for v in set(x)}
        return str("female/male ratio: " + str(round(d["F"]/d["M"], 1)))

    
        
    def get_hotspots(self):
        
        # create a query class object
        db_query = query()

        crashes = db_query.get_crash_hotspots(self.polyline, min(10, ceil(self.distance/1000)))
        
        # reference: https://stackoverflow.com/questions/35491274/pandas-split-column-of-lists-into-multiple-columns
        # reference: https://stackoverflow.com/questions/4703390/how-to-extract-a-floating-number-from-a-string
        # reference: https://stackoverflow.com/questions/20829748/pandas-assigning-multiple-new-columns-simultaneously
        
        # if accidents are found on the route
        if (crashes.shape[0] != 0):
            
            # add vehicles to watch out for
            crashes["tips"] = crashes["vehicle"].apply(self.extract_vehicles)
            
            # add sex ratio
            crashes["ratio"] = crashes["sex"].apply(self.sex_ratio)
            
            crashes = crashes.assign(lon=None)
            crashes = crashes.assign(lat=None)
            
            # split centroid string into lat and lon columns
            crashes[["lon", "lat"]] = crashes["centroid"].str.findall(r'-?\d+\.\d+').to_list()
            
            # drop redundant columns to free memory
            crashes = crashes.drop('centroid', 1)
            crashes = crashes.drop('vehicle', 1)
            crashes = crashes.drop('sex', 1)
            
            return crashes
        
        else:
            return None
        
        
        
    
    def plot_folium(self):
        
        # case when map is being rendered for just the current user coordinates
        if self.dest is None:
            
            local_map = folium.Map(location=(self.origin.lat, self.origin.lon),
                                   tiles=self.tile,
                                   zoom_start=13, attr=self.attr)
            
            folium.Marker((self.origin.lat, self.origin.lon), tooltip = "Current Location",
                icon=folium.Icon(color="blue"),
                popup= folium.map.Popup(self.origin.address, show=True)).add_to(local_map)
            
            
            db_query = query()

            heat_data = db_query.get_heat_data(self.origin.lat, self.origin.lon)
            
            if heat_data.shape[0] != 0:
                heat_data = heat_data.assign(lon=None)
                heat_data = heat_data.assign(lat=None)
            
                # split centroid string into lat and lon columns
                heat_data[["lon", "lat"]] = heat_data["centroid"].str.findall(r'-?\d+\.\d+').to_list()
                
                # add vehicles to watch out for
                heat_data["tips"] = heat_data["vehicle"].apply(self.extract_vehicles)
                
                heat_data = heat_data.drop('centroid', 1)
                heat_data = heat_data.drop('vehicle', 1)
                
                folium.CircleMarker(location=[self.origin.lat, self.origin.lon],
                                radius=200,
                                fill=False, color = "blue").add_to(local_map)
                
                
                for index, row in heat_data.iterrows():
                    
                    radius = row["crash_count"]/4
                    
                    tooltip_html = (str(row["crash_count"]) + " accident events<br>" +
                                    row["tips"] )
                
                                       
                    folium.CircleMarker(location=[row["lat"], row["lon"]],
                                radius=radius,
                                tooltip=folium.map.Tooltip(tooltip_html),
                                fill=True, color = "red").add_to(local_map)
            

            return local_map._repr_html_()


         
        # case when plotting directions b/w two points
        else:
            
            
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
            folium.PolyLine(self.route_pts,
                           popup = folium.map.Popup(polyline_html,
                                                    max_width=2650, show=True)).add_to(route_map)
            
            # origon marker
            folium.Marker((self.origin.lat, self.origin.lon), tooltip="Origin", 
                icon=folium.Icon(color="blue"),
                popup=folium.map.Popup(self.origin.address, max_width=125, show=True)).add_to(route_map)
            
            # destination marker
            folium.Marker((self.dest.lat, self.dest.lon), tooltip="Destination", 
                icon=folium.Icon(color="orange"),
                popup=folium.map.Popup(self.dest.address, max_width=125, show = True)).add_to(route_map)
            
            
            # calculate crash hotspots for route
            route_hotspots = self.get_hotspots()
            
            
            # if hotspots are found in database
            # add hotspots to the map
            
            if route_hotspots is not None:
                
                for index, row in route_hotspots.iterrows():
                    
                    radius = row["crash_count"]/4
                    
                    tooltip_html = (str(row["crash_count"]) + " accident events<br>" +
                                    row["tips"] + "<br>" +
                                    row["ratio"])
                
                                       
                    folium.CircleMarker(location=[row["lat"], row["lon"]],
                                radius=radius,
                                tooltip=folium.map.Tooltip(tooltip_html),
                                fill=True, color = "red").add_to(route_map)
            
            # fit route bounds
            route_map.fit_bounds(self.route_bounds)
            

            return route_map._repr_html_()
		



	


