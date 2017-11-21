
import numpy as np
import h5py

# nodal positions
coor = np.array([
  [0., 0.], # 0
  [1., 0.], # 1
  [2., 0.], # 2
  [0., 1.], # 3
  [1., 1.], # 4
  [2., 1.], # 5
  [0., 2.], # 6
  [1., 2.], # 7
  [2., 2.], # 8
])

# connectivity (4-node quadrilaterals)
conn = np.array([
  [0,1,4,3],
  [1,2,5,4],
  [3,4,7,6],
  [4,5,8,7],
])

# open data file
f = h5py.File('example.hdf5','w')

# write particle positions, and a dummy connectivity
f.create_dataset('/coor',data=coor)
f.create_dataset('/conn',data=conn)

# create a sample deformation: simple shear
for inc,gamma in enumerate(np.linspace(0,1,100)):

  # - initialize displacement (should be 3-d for ParaView)
  U = np.zeros((coor.shape[0],3),dtype='float64')
  # - set
  U[:,0] += gamma * coor[:,1]
  # - store
  f.create_dataset('/disp/%d'%inc,data=U)


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

grid = '''<Grid Name="Increment = {inc:d}">
  <Time Value="{inc:d}"/>
  <Topology TopologyType="Quadrilateral" NumberOfElements="4">
    <DataItem Dimensions="4 4" Format="HDF">
    example.hdf5:/conn
    </DataItem>
  </Topology>
  <Geometry GeometryType="XY">
    <DataItem Dimensions="9 2" Format="HDF">
    example.hdf5:/coor
    </DataItem>
  </Geometry>
  <Attribute Name="Displacement" AttributeType="Vector" Center="Node">
     <DataItem Dimensions="9 3" NumberType="Float" Precision="8" Format="HDF">
      example.hdf5:/disp/{inc:d}
     </DataItem>
  </Attribute>
</Grid>
'''

series = ''

for inc in range(100):
  series += grid.format(inc=inc)

series = '      '+series.replace('\n','\n      ')

open('example.xmf','w').write(xmf.format(series=series))
