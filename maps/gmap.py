import googlemaps
import os
import folium
import polyline



class Place():
	def __init__(self):
		self.lat = None
		self.lon = None
		self.address = None
		self.place_id = None
		self.gmaps = googlemaps.Client(key=os.environ["gcp_key"])


	def search(self, query, qry_type):
		if qry_type == "lat/lon":
			self.lat = query["lat"]
			self.lon = query["lon"]
			self.address = "Current Location"
			

		elif qry_type == "txt":
			place_search = self.gmaps.places(query)

			if place_search["status"] == "OK":
				self.lat = place_search["results"][0]["geometry"]["location"]["lat"]
				self.lon = place_search["results"][0]["geometry"]["location"]["lng"]
				self.address = place_search["results"][0]["formatted_address"]
				self.place_id = place_search["results"][0]["place_id"]







class Directions(Place):
	def __init__(self, origin=None, dest=None):
		self.origin = origin
		self.dest = dest
		self.gmaps = googlemaps.Client(key=os.environ["gcp_key"])
		self.routes = None		



	def get_route(self):
		directions_result = self.gmaps.directions(
			(self.origin.lat, self.origin.lon),
			(self.dest.lat, self.dest.lon),
			mode="driving",
			alternatives=True)
		
		self.routes = directions_result


	
	def plot_folium(self):
		some_map = folium.Map(location=[-37.8767985, 144.9882031], 
                              zoom_start=15, tiles='OpenStreetMap')


		for each in range(len(self.routes)):
			pts = polyline.decode(self.routes[each]["overview_polyline"]["points"])
			folium.PolyLine(pts, color = "blue", weight=5).add_to(some_map)


		return some_map._repr_html_()

		



	


