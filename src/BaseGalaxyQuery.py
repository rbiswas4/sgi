#!/usr/bin/env python
"""
Code to obtain num_gals, sum_mass for galaxies in galaxy Base in redshift
bins of width 0.1 to a maximum redshift of 1.2 

- a threshold on the minimum values of stellar masses and only considers 
 galaxies with stellar masses above this threshold. Currently, this value is
 0.01 * 1.0e10 M_solar / 0.73

- Only a spatial area of ra and dec from -2.0 to 2.0 in each is sampled, to prevent any edge effects of the patch which extends from -2.5 degrees to 2.5 degrees for each coordinate.

- Writes out a csv file with some information about galaxies in bins of redshift. The columns number of galaxies ('numGals'), and sum of galaxy stellar mass
 ('sum_mass') again in the units of 1.0e10 M_\odot / 0.73.
"""
import pandas as pd
import numpy as np
import pymssql


DBconnection = pymssql.connect(user="LSST-2", password="L$$TUser",
                               host="localhost", database="LSST",
                               port='51433')

print 'Connected'
db = DBconnection.cursor()

zvals = np.arange(0., 1.2, 0.1)
data = []
for i, z in enumerate(zvals):
    print 'Begin trying query', i
    query = """
    SELECT COUNT(*) 
        , MIN([redshift])
        , MAX([redshift])
        , MIN([mass_stellar])
        , MAX([mass_stellar])
        , MIN([r_ab])
        , MAX([r_ab])
        , SUM([mass_stellar])
    FROM [LSST].[dbo].[galaxy]
    WHERE redshift > {0:2f} 
        AND redshift < {1:.2f}
        AND mass_stellar > 0.01
        AND ra < 2.0 
        AND ra > -2.0
        AND dec < 2.0
        AND dec > -2.0
    """.format(zvals[i], zvals[i]+ 0.1)
    db.execute(query)
    s = db.fetchall()
    d = list(s[0])
    print d
    data.append(d)
    # print data
df = pd.DataFrame(np.asarray(data),
        columns=['numGals', 'minz', 'maxz', 'min_mass', 'max_mass', 'minrab',\
                 'maxrab', 'sum_mass'])
df.to_csv('fatboy_galaxyBase.csv', index=False)

