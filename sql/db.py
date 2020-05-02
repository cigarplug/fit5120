import psycopg2
import os
import pandas as pd


class query:


	def __init__(self):
		self.cnx = psycopg2.connect(user=os.environ["user"],
								password=os.environ["password"],
								host=os.environ["host"]
								)


	def get_route_crashes(self, polyline):
	    query = ("""
	    select
	        count(*) crash_count
	    from
	        node n
	    where
	        st_contains( ST_Buffer( st_linefromencodedpolyline('""" + polyline + """'),
	        0.005),
	        n.coords)

	        """)
    
	    df = pd.read_sql(query, self.cnx)
	    return(df["crash_count"][0])


	    

	def __del__(self):
		self.cnx.close()

