
import numpy as np
import h5py

# ====================== create fictitious configuration + store to HDF5-file ======================

# nodal positions
coor = np.array([
  [0., 0., 0.], #  0
  [1., 0., 0.], #  1
  [2., 0., 0.], #  2
  [0., 1., 0.], #  3
  [1., 1., 0.], #  4
  [2., 1., 0.], #  5
  [0., 0., 1.], #  6
  [1., 0., 1.], #  7
  [2., 0., 1.], #  8
  [0., 1., 1.], #  9
  [1., 1., 1.], # 10
  [2., 1., 1.], # 11
])

# connectivity (8-node quadrilaterals)
conn = np.array([
  [0,1,4,3,6,7,10,9],
  [1,2,5,4,7,8,11,10],
])

# open data file
f = h5py.File('example.hdf5','w')

# write particle positions, and a dummy connectivity
f.create_dataset('/coor',data=coor)
f.create_dataset('/conn',data=conn)

# create a sample deformation: simple shear
for inc,gamma in enumerate(np.linspace(0,1,100)):

  # - initialize displacement (must be always 3-d in ParaView!)
  disp = np.zeros((coor.shape[0],3),dtype='float64')
  # - set
  disp[:,0] += gamma * coor[:,1]
  # - store
  f.create_dataset('/disp/%d'%inc,data=disp)

# ======================================== write XDMF-file =========================================

# --------------------------------- format of the main structure ----------------------------------

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

# ----------------------------- format of an increment in time-series ------------------------------

grid = '''<Grid Name="Increment = {inc:d}">
  <Time Value="{inc:d}"/>
  <Topology TopologyType="Hexahedron" NumberOfElements="{nelem:d}">
    <DataItem Dimensions="{nelem:d} {nne:d}" Format="HDF">
    example.hdf5:/conn
    </DataItem>
  </Topology>
  <Geometry GeometryType="XYZ">
    <DataItem Dimensions="{nnode:d} 3" Format="HDF">
    example.hdf5:/coor
    </DataItem>
  </Geometry>
  <Attribute Name="Displacement" AttributeType="Vector" Center="Node">
     <DataItem Dimensions="{nnode:d} 3" NumberType="Float" Precision="8" Format="HDF">
      example.hdf5:/disp/{inc:d}
     </DataItem>
  </Attribute>
</Grid>
'''

# ------------------------------------------- write file -------------------------------------------

# initialize string that will contain the full time series
txt = ''

# loop over all increments, append the time series
for inc in range(100):
  txt += grid.format(inc=inc,nnode=coor.shape[0],nelem=conn.shape[0],nne=conn.shape[1])

# write xmf-file, fix the indentation
open('example.xmf','w').write(xmf.format(series='      '+txt.replace('\n','\n      ')))
