import numpy as np
import cv2
import matplotlib.pyplot as plt
from skimage.transform import PiecewiseAffineTransform, warp
from skimage import data


im = cv2.imread("assets\\testgrid.png")
im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

# src_cols = np.linspace(0, cols, 5)
# src_rows = np.linspace(0, rows, 5)
# src_rows, src_cols = np.meshgrid(src_rows, src_cols)
# src = np.dstack([src_cols.flat, src_rows.flat])[0]

# print( src)

# # add sinusoidal oscillation to row coordinates
# dst_rows = src[:, 1] + np.cos(np.linspace(0, 2 * np.pi, src.shape[0])) * 64
# dst_cols = src[:, 0]
# dst = np.vstack([dst_cols, dst_rows]).T

# tform = cv2.getPerspectiveTransform(src, dst)
# out = cv2.warpPerspective(image,tform,(rows,cols))

# fig, ax = plt.subplots()
# ax.imshow(out)
# ax.plot(tform.inverse(src)[:, 0], tform.inverse(src)[:, 1], '.b')
# ax.axis((0, out_cols, out_rows, 0))
# plt.show()



loop = 0
while True:
  loop = loop + 1

  # generate a test image
  h, w = im.shape[0], im.shape[1]

  # Number of grid cells
  nx, ny = 8, 8
  p0 = np.meshgrid(np.linspace(0, w-1, nx+1, dtype='f'), np.linspace(0, h-1, ny+1, dtype='f'))
  p1 = [v.copy() for v in p0]

  for i in range(nx+1):
    for j in range(ny+1):
      p1[0][i,j] += np.sin(i/4*np.pi + (loop/6 % (2*np.pi))) * 40
      p1[1][i,j] += np.cos(j/4*np.pi + (loop/6 % (2*np.pi))) * 40


  im1 = np.zeros_like(im)
  for i in range(nx):
    for j in range(ny):
      x0, y0 = p0[0][j,i], p0[1][j,i]

      sourceSqr = np.stack((p0[0][j:(j+2),i:(i+2)].ravel() - x0 , p0[1][j:(j+2),i:(i+2)].ravel() - y0 ))
      destSqr = np.stack((p1[0][j:(j+2),i:(i+2)].ravel() , p1[1][j:(j+2),i:(i+2)].ravel() ))
      iSourceSqr = np.round(np.stack((p0[0][j:(j+2),i:(i+2)].ravel(), p0[1][j:(j+2),i:(i+2)].ravel()))).astype('i')
      iDestSqr = np.round(np.stack((p1[0][j:(j+2),i:(i+2)].ravel(), p1[1][j:(j+2),i:(i+2)].ravel()))).astype('i')

      #pad the squares to try to eliminate seam
      # if i > 0:
      #   iSourceSqr[0] += [-1, 0, -1, 0]
      #   iDestSqr[0] += [-1, 0, -1, 0]
      # if i < nx-1:
      #   iSourceSqr[0] += [0, 1, 0, 1]
      #   iDestSqr[0] += [0, 1, 0, 1]
      # if j > 0:
      #   iSourceSqr[1] += [-1, -1, 0, 0]
      #   iDestSqr[1] += [-1, -1, 0, 0]
      # if j < ny-1:
      #   iSourceSqr[1] += [0, 0, 1, 1]
      #   iDestSqr[1] += [0, 0, 1, 1]

      for indexSet in ([0,1,2],[1,3,2]):
        srcTri = sourceSqr.T[indexSet]
        destTri = destSqr.T[indexSet]
        iDestTri = iDestSqr.T[indexSet]
        M = cv2.getAffineTransform(srcTri, destTri)
        imw = cv2.warpAffine(im[iSourceSqr[1,0]:iSourceSqr[1,3], iSourceSqr[0,0]:iSourceSqr[0,3]], M, (w, h))
        # cv2.imshow("Test_" + str(i) + "_" + str(j) + "_" + str(indexSet[0]), imw)
        shard = cv2.fillConvexPoly(np.zeros_like(im), iDestTri, 255) & imw
        # im1 = np.where(shard == 0, im1, shard) // poor performance
        im1 |= shard

  cv2.imshow("Test", im1)
  
  key = cv2.waitKey(1)

  if key == ord('q'):
      break
  if key == 27: #esc
      break
