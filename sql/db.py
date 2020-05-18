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
	    
	    query = """
    
	        with route_pts as (
	        select
	            n.coords coords,
	            n.accident_no
	        from
	            node n
	        where
	            st_contains( ST_Buffer( st_linefromencodedpolyline('""" + polyline + """'),
	            0.0005),
	            n.coords) ),
	            
	        clusters as (
	        select
	            unnest(ST_ClusterWithin(route_pts.coords, 0.00025)) gc
	        from
	            route_pts
	        left join accident_event ae on
	            ae.accident_no = route_pts.accident_no ),
	            
	        cluster_info as (
	        select
	            gc geom,
	            st_numgeometries(gc) as crash_count,
	            ST_AsText(ST_Centroid(gc)) as centroid
	        from
	            clusters
	        order by
	            st_numgeometries(gc) desc
	        limit """ + str(limit) + """ ),
	        
	        sex as (
	        select
	            array_agg(sex) sex,
	            cluster_info.geom geom,
	            cluster_info.centroid,
	            cluster_info.crash_count
	        from
	            (
	            select
	                n.coords,
	                p.sex
	            from
	                node n
	            left join person p on
	                n.accident_no = p.accident_no
	            where
	                sex not in ('',
	                'U') ) inter_1,
	            cluster_info
	        where
	            st_intersects(cluster_info.geom,
	            inter_1.coords)
	        group by
	            cluster_info.geom,
	            cluster_info.centroid,
	            cluster_info.crash_count ),
	            
	        vtype as (
	        select
	            array_agg(vehicle_type_desc) vehicle_type_desc,
	            cluster_info.geom geom
	        from
	            (
	            select
	                n.coords,
	                v.vehicle_type_desc
	            from
	                node n
	            left join vehicle v on
	                n.accident_no = v.accident_no
	            where
	                vehicle_type_desc not in ('Other Vehicle',
	                'Station Wagon',
	                'Not Applicable',
	                'Car',
	                'Unknown') ) inter_2,
	            cluster_info
	        where
	            st_intersects(cluster_info.geom,
	            inter_2.coords)
	        group by
	            cluster_info.geom )
	            
	        select
	            s.sex,
	            v.vehicle_type_desc vehicle,
	            s.crash_count,
	            s.centroid
	        from
	            sex s
	        left join vtype v on
	            s.geom = v.geom
	        order by
	            s.crash_count desc

    	"""
	    
	    return(pd.read_sql(query, self.cnx))



	def get_heat_data(self, lat, lon):
    
	    query = """
	            with crashes as (
	        select
	            coords
	        from
	            node n
	        where
	            st_distancesphere('Point(""" + str(lon) + " " +  str(lat) + """)',
	            n.coords) < 3000 ),
	        cluster_info as (
	        select
	            gc geom,
	            st_numgeometries(gc) as crash_count,
	            ST_AsText(ST_Centroid(gc)) as centroid
	        from
	            (
	            select
	                unnest(ST_ClusterWithin(crashes.coords, 0.00025)) gc
	            from
	                crashes ) f
	        order by
	            st_numgeometries(gc) desc
	        limit 10 ),
	        vtype as (
	        select
	            array_agg(vehicle_type_desc) vehicle_type_desc,
	            cluster_info.geom geom,
	            cluster_info.crash_count,
	            cluster_info.centroid
	        from
	            (
	            select
	                n.coords,
	                v.vehicle_type_desc
	            from
	                node n
	            left join vehicle v on
	                n.accident_no = v.accident_no
	            where
	                vehicle_type_desc not in ('Other Vehicle',
	                'Station Wagon',
	                'Not Applicable',
	                'Car',
	                'Unknown') ) inter_1,
	            cluster_info
	        where
	            st_intersects(cluster_info.geom,
	            inter_1.coords)
	        group by
	            cluster_info.geom,
	            cluster_info.crash_count,
	            cluster_info.centroid )
	        select
	            v.vehicle_type_desc vehicle,
	            st_astext(v.centroid) centroid,
	            v.crash_count crash_count
	        from
	            vtype v
	    """
	    
	    return pd.read_sql(query, self.cnx)


	    

	def __del__(self):
		self.cnx.close()

