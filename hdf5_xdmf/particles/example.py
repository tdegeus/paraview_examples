
import h5py
import numpy      as np
import lxml.etree as etree

# ====================== create fictitious configuration + store to HDF5-file ======================

# create grid of particles: 10 particles in each direction, spacing of 1
x,y,z = np.meshgrid(np.linspace(0,10,10),np.linspace(0,10,10),np.linspace(0,10,10))

# convert the list of positions
coor  = np.hstack(( x.reshape(-1,1), y.reshape(-1,1), z.reshape(-1,1) ))
nnode = coor.shape[0]
ndim  = coor.shape[1]

# create example radius
radius       = np.ones((coor.shape[0]),dtype='float64')
radius[::2] *= 2.

# open data file
file = h5py.File('example.hdf5','w')

# write particle positions, and a dummy connectivity
file['/coor'  ] = coor
file['/radius'] = radius
file['/conn'  ] = np.arange(coor.shape[0])

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
  conn = etree.SubElement(grid, "Topology", TopologyType="Polyvertex", NumberOfElements='{nnode:d}'.format(nnode=nnode), NodesPerElement="1")
  data = etree.SubElement(conn, "DataItem", Dimensions='{nnode:d} 1'.format(nnode=nnode), Format="HDF")
  data.text = "example.hdf5:/conn"

  # add coordinates
  coor = etree.SubElement(grid, "Geometry", GeometryType="XYZ")
  data = etree.SubElement(coor, "DataItem", Dimensions='{nnode:d} {ndim:d}'.format(nnode=nnode,ndim=ndim), Format="HDF")
  data.text = "example.hdf5:/coor"

  # add radius
  radius = etree.SubElement(grid, "Attribute", Name="Radius", AttributeType="Scalar", Center="Node")
  data   = etree.SubElement(radius, "DataItem", Dimensions='{nnode:d}'.format(nnode=nnode), Format="HDF")
  data.text = "example.hdf5:/radius"

  # add displacement
  disp = etree.SubElement(grid, "Attribute", Name="Displacement", AttributeType="Vector", Center="Node")
  data = etree.SubElement(disp, "DataItem", Dimensions='{nnode:d} 3'.format(nnode=nnode), Format="HDF")
  data.text = "example.hdf5:/disp/{inc:d}".format(inc=inc)

# write to file
open('example.xdmf','wb').write(etree.tostring(root, pretty_print=True))
