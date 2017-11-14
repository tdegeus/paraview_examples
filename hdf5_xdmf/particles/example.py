
import numpy as np
import h5py

# create grid of particles: 10 particles in each direction, spacing of 1
x,y,z = np.meshgrid(np.linspace(0,10,10),np.linspace(0,10,10),np.linspace(0,10,10))

# convert the list of positions
X = np.hstack(( x.reshape(-1,1), y.reshape(-1,1), z.reshape(-1,1) ))

# open data file
f = h5py.File('example.hdf5','w')

# write particle positions, and a dummy connectivity
f.create_dataset('/X',data=X)
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
    <Grid Name="Time = {inc:d}">
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
      <Attribute Name="Displacement" AttributeType="Vector" Center="Node">
         <DataItem Dimensions="1000 3" NumberType="Float" Precision="8" Format="HDF">
          example.hdf5:/U/{inc:d}
         </DataItem>
       </Attribute>
    </Grid>
  </Domain>
</Xdmf>
'''


for inc in range(100):

  open('example_%03d.xmf'%inc,'w').write(xmf.format(inc=inc))
