from maps.googlemaps import Place, Directions, Map

def map_handler(content):

	origin = Place()

	origin.search(content["origin"]["query"], content["origin"]["qry_type"])

	if content["dest"] is not None:

		dest = Place()
		
		dest.search(content["dest"]["query"], content["dest"]["qry_type"])

		my_dir = Directions(origin, dest)
		df = my_dir.get_routes()
		subdf = df.loc[df["tags"].apply(lambda x: content["tags"] in x)].reset_index()

		my_map = Map(origin, dest, subdf)
		return my_map.plot_folium()

	else:
		my_map = Map(origin)
	
	return my_map.plot_folium()

		

		