
import numpy as np
import h5py

# ====================== create fictitious configuration + store to HDF5-file ======================

# create grid of particles: 10 particles in each direction, spacing of 1
x,y,z   = np.meshgrid(np.linspace(0,10,10),np.linspace(0,10,10),np.linspace(0,10,10))

# convert the list of positions
coor       = np.hstack(( x.reshape(-1,1), y.reshape(-1,1), z.reshape(-1,1) ))

# create example radius
radius       = np.ones((coor.shape[0]),dtype='float64')
radius[::2] *= 2.

# open data file
f = h5py.File('example.hdf5','w')

# write particle positions, and a dummy connectivity
f.create_dataset('/coor'  ,data=coor                    )
f.create_dataset('/radius',data=radius                  )
f.create_dataset('/conn'  ,data=np.arange(coor.shape[0]))

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
  <Topology TopologyType="Polyvertex" NumberOfElements="{nnode:d}" NodesPerElement="1">
    <DataItem Dimensions="{nnode:d} 1" Format="HDF">
    example.hdf5:/conn
    </DataItem>
  </Topology>
  <Geometry GeometryType="XYZ">
    <DataItem Dimensions="{nnode:d} 3" Format="HDF">
    example.hdf5:/coor
    </DataItem>
  </Geometry>
  <Attribute Name="Radius" AttributeType="Scalar" Center="Node">
     <DataItem Dimensions="{nnode:d}" NumberType="Float" Precision="8" Format="HDF">
      example.hdf5:/radius
     </DataItem>
  </Attribute>
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
  txt += grid.format(inc=inc,nnode=coor.shape[0])

# write xmf-file, fix the indentation
open('example.xmf','w').write(xmf.format(series='      '+txt.replace('\n','\n      ')))
