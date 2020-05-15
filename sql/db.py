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
	        0.0005),
	        n.coords)

	        """)
    
	    df = pd.read_sql(query, self.cnx)
	    return(df["crash_count"][0])




	def get_crash_hotspots(self, polyline, limit = 10):
    
	    # reference: https://gis.stackexchange.com/questions/11567/spatial-clustering-with-postgis
	    # reference: https://gis.stackexchange.com/questions/269854/understanding-st-clusterwithin
	    # reference: https://stackoverflow.com/questions/35482754/postgis-clustering-with-other-aggregate
	    
	    query = ("""
	    
	        with something as (
	        select
	            t.coords,
	            ae.event_type_desc
	        from
	            (
	            select
	                n.coords,
	                n.accident_no
	            from
	                node n
	            where
	                st_contains( ST_Buffer( st_linefromencodedpolyline('""" + polyline + """'),
	                0.0005),
	                n.coords) ) t
	        left join accident_event ae on
	            ae.accident_no = t.accident_no )
	        select
	            st_numgeometries(gc) as crash_count,
	            ST_AsText(ST_Centroid(gc)) as centroid
	        from
	            (
	            select
	                unnest(ST_ClusterWithin(something.coords, 0.00025)) gc
	            from
	                something ) f
	        order by
	            st_numgeometries(gc) desc
	        limit """ + str(limit)

	    )
	    
	    return(pd.read_sql(query, self.cnx))


	    

	def __del__(self):
		self.cnx.close()

