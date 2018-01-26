
import h5py
import numpy      as np
import lxml.etree as etree

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

# dimensions
nnode = coor.shape[0]
ndim  = coor.shape[1]
nelem = conn.shape[0]
nne   = conn.shape[1]

# open data file
file = h5py.File('example.hdf5','w')

# write nodal coordinate, connectivity, and some dummy element quantity
file['/coor' ] = coor
file['/conn' ] = conn
file['/index'] = np.arange(nelem)

# create a sample deformation: simple shear
for inc,gamma in enumerate(np.linspace(0,1,100)):

  # - initialize displacement (must be always 3-d in ParaView!)
  disp = np.zeros((coor.shape[0],3),dtype='float64')
  # - set
  disp[:,0] += gamma * coor[:,1]
  # - store
  file['/disp/{inc:d}'.format(inc=inc)] = disp

# ======================================== write XDMF-file =========================================

# initialize file
root   = etree.fromstring('<Xdmf Version="2.0"></Xdmf>')
domain = etree.SubElement(root, "Domain")
series = etree.SubElement(domain, "Grid", Name="TimeSeries", GridType="Collection", CollectionType="Temporal")

# loop over increment
for inc in range(100):

  # add time increment
  grid = etree.SubElement(series, "Grid", Name="Increment = {inc:d}".format(inc=inc))

  # set time
  etree.SubElement(grid, "Time", Value="{inc:d}".format(inc=inc))

  # add connectivity
  conn = etree.SubElement(grid, "Topology", TopologyType="Hexahedron", NumberOfElements='{nelem:d}'.format(nelem=nelem))
  data = etree.SubElement(conn, "DataItem", Dimensions='{nelem:d} {nne:d}'.format(nelem=nelem,nne=nne), Format="HDF")
  data.text = "example.hdf5:/conn"

  # add coordinates
  coor = etree.SubElement(grid, "Geometry", GeometryType="XYZ")
  data = etree.SubElement(coor, "DataItem", Dimensions='{nnode:d} {ndim:d}'.format(nnode=nnode,ndim=ndim), Format="HDF")
  data.text = "example.hdf5:/coor"

  # add radius
  index = etree.SubElement(grid, "Attribute", Name="Index", AttributeType="Scalar", Center="Cell")
  data  = etree.SubElement(index, "DataItem", Dimensions='{nelem:d}'.format(nelem=nelem), Format="HDF")
  data.text = "example.hdf5:/index"

  # add displacement
  disp = etree.SubElement(grid, "Attribute", Name="Displacement", AttributeType="Vector", Center="Node")
  data = etree.SubElement(disp, "DataItem", Dimensions='{nnode:d} 3'.format(nnode=nnode), Format="HDF")
  data.text = "example.hdf5:/disp/{inc:d}".format(inc=inc)

# write to file
open('example.xdmf','wb').write(etree.tostring(root, pretty_print=True))
