
import numpy as np
import h5py

# create grid of particles: 10 particles in each direction, spacing of 1
x,y,z = np.meshgrid(np.linspace(0,10,10),np.linspace(0,10,10),np.linspace(0,10,10))

# convert the list of positions
X = np.hstack(( x.reshape(-1,1), y.reshape(-1,1), z.reshape(-1,1) ))

# create example radius
R       = np.ones((X.shape[0]),dtype='float64')
R[::2] *= 2.

# open data file
f = h5py.File('example.hdf5','w')

# write particle positions, and a dummy connectivity
f.create_dataset('/X',data=X)
f.create_dataset('/R',data=R)
f.create_dataset('/connectivity',data=np.arange(X.shape[0]))

# create a sample deformation: simple shear
for inc,gamma in enumerate(np.linspace(0,1,100)):

  # - initialize displacement
  U = np.zeros(X.shape,dtype='float64')
  # - set
  U[:,0] += gamma * X[:,1]
  # - store
  f.create_dataset('/U/%d'%inc,data=U)


# ==================================================================================================

xmf = '''<?xml version="1.0" ?>
<!DOCTYPE Xdmf SYSTEM "Xdmf.dtd" []>
<Xdmf Version="2.0">
  <Domain>
    <Grid Name="TimeSeries" GridType="Collection" CollectionType="Temporal">
{series:s}
    </Grid>
  </Domain>
</Xdmf>
'''

# --------------------------------------------------------------------------------------------------

grid = '''<Grid Name="Time = {inc:d}">
  <Time Value="{inc:d}"/>
  <Topology TopologyType="Polyvertex" NumberOfElements="1000" NodesPerElement="1">
    <DataItem Dimensions="1000 1" Format="HDF">
    example.hdf5:/connectivity
    </DataItem>
  </Topology>
  <Geometry GeometryType="XYZ">
    <DataItem Dimensions="1000 3" Format="HDF">
    example.hdf5:/X
    </DataItem>
  </Geometry>
  <Attribute Name="Radius" AttributeType="Scalar" Center="Node">
     <DataItem Dimensions="1000" NumberType="Float" Precision="8" Format="HDF">
      example.hdf5:/R
     </DataItem>
  </Attribute>
  <Attribute Name="Displacement" AttributeType="Vector" Center="Node">
     <DataItem Dimensions="1000 3" NumberType="Float" Precision="8" Format="HDF">
      example.hdf5:/U/{inc:d}
     </DataItem>
  </Attribute>
</Grid>
'''

# --------------------------------------------------------------------------------------------------

# initialize string that will contain the full time series
series = ''

# loop over all increments, append the time series
for inc in range(100):
  series += grid.format(inc=inc)

# write xmf-file, fix the indentation
open('example.xmf','w').write(xmf.format(series='      '+series.replace('\n','\n      ')))
