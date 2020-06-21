# This code uses Astropy package to match catalogs from SExtractor outputs.

# Importing numpy and plot functions
import numpy as np 
from matplotlib import pyplot as plt 

# Importing Astropy packages
from astropy import units as u
from astropy import table
from astropy.coordinates import SkyCoord, match_coordinates_sky
from astropy.table import Table, setdiff, vstack
from astropy.io import ascii

# Importing the catalogs: cat_base is the base catalog whose objects we want to match
# [!] len(cat_base) > len(cat)

catA= Table.read('/home/augusto/Pilot/NGC1600_MOSAIC_i_gauss_4.0_7x7.reg',
                           format = 'ascii') # catalog we want to match
catB = Table.read('/home/augusto/Pilot/NGC1600_MOSAIC_i_mex_4.0_9x9.reg',
                           format = 'ascii') # base catalog

if len(catA) > len(catB):
    cat_base = catA
    cat = catB
else:
    cat_base = catB
    cat = catA

# Using SkyCoord to extract the ra and dec columns
cat1 = SkyCoord(ra=cat_base['ALPHA_J2000'], dec=cat_base['DELTA_J2000'],unit='deg') # gaussian filter
cat2 = SkyCoord(ra=cat['ALPHA_J2000'], dec=cat['DELTA_J2000'],unit='deg') # mexhat filter

# Matching the catalogs

#idx, sep, d3d = coord1.match_to_catalog_sky(coord2)
idx, sep, d3d = match_coordinates_sky(cat2, cat1, nthneighbor=1)

# In the above line of code, idx are the indexes of the closest matches, sep is 
# the on-sky distance between the matches and d3d is the real-space distances
# between the matches

# Finding the histogram of matches

matches = cat1[idx]
print(str('The total number of matched objects between catalogs is'))
print(len(matches))

plt.hist(sep.arcsec, histtype='step', range=(0,8))
plt.xlabel('separation [arcsec]')
plt.tight_layout()

# Getting the indexes of the matched objects to pass these into the original catalog

max_sep = 1*u.arcsec # Maximum separation constraint
idx1, sep1, d3d1 = match_coordinates_sky(matches[sep > max_sep], cat2, nthneighbor=1)

# Passing the indexes into the original catalog

cat_updated = table.unique(cat[idx1],keys='NUMBER') # This catalog contains only the non-matches between cat and cat_base
print(str('The number of objects in cat that are not in cat_base is'))
print(len(cat_updated))

print(str('The first 5 items of the updated catalog are'))
print(cat_updated[:5])

# Merging cat_updated and cat_base

final_catalog = vstack([cat_base, cat_updated])

print(str('The number of objects in the final catalog is'))
print(len(final_catalog))

# Writing the final catalog

ascii.write(final_catalog, 'MOSAIC_i_final.txt', overwrite=True)

# Writing the final catalog as a .reg file to import to DS9

ascii.write(final_catalog['X_IMAGE_DBL','Y_IMAGE_DBL'], 'MOSAIC_i_final.reg', overwrite=True)