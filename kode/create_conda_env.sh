conda config --add channels conda-forge
conda config --set channel_priority strict
conda create -n statsbudsjett fiona geojson geopandas numpy openpyxl pandas pandoc pandocfilters pyproj shapely xlrd xlsxwriter xmltodict ipykernel ipympl nb_conda_kernels nodejs ipdb
conda activate statsbudsjett
