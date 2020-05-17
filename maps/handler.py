from maps.googlemaps import Place, Directions, Map
# import re

def map_handler(content):

	origin = Place()

	origin.search(content["origin"]["query"], content["origin"]["qry_type"])

	if content["dest"] is not None:

		dest = Place()
		
		dest.search(content["dest"]["query"], content["dest"]["qry_type"])

		my_dir = Directions(origin, dest)
		df = my_dir.get_routes()
		subdf = df.loc[df["tags"].apply(lambda x: content["tags"] in x)].reset_index(drop=True)

		my_map = Map(origin, dest, subdf)

	else:
		my_map = Map(origin)
	
	html = my_map.plot_folium()

	# change padding-bottom from 60% to 0%
	# return re.sub("padding-bottom:60%", "padding-bottom:0%", html)

	return html

		

		