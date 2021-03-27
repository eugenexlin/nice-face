import numpy as np
from PIL import Image
import cv2

def quad_as_rect(quad):
    if quad[0] != quad[2]: return False
    if quad[1] != quad[7]: return False
    if quad[4] != quad[6]: return False
    if quad[3] != quad[5]: return False
    return True

def quad_to_rect(quad):
    assert(len(quad) == 8)
    assert(quad_as_rect(quad))
    return (quad[0], quad[1], quad[4], quad[3])

def rect_to_quad(rect):
    assert(len(rect) == 4)
    return (rect[0], rect[1], rect[0], rect[3], rect[2], rect[3], rect[2], rect[1])

def shape_to_rect(shape):
    assert(len(shape) == 2)
    return (0, 0, shape[0], shape[1])

def griddify(rect, w_div, h_div):
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]
    x_step = w / float(w_div)
    y_step = h / float(h_div)
    y = rect[1]
    grid_vertex_matrix = []
    for _ in range(h_div + 1):
        grid_vertex_matrix.append([])
        x = rect[0]
        for _ in range(w_div + 1):
            grid_vertex_matrix[-1].append([int(x), int(y)])
            x += x_step
        y += y_step
    grid = np.array(grid_vertex_matrix)
    return grid

def distort_grid(org_grid, max_shift, wavePeriodDivisor, offset):
    new_grid = np.copy(org_grid)
    sh = org_grid.shape
    for i in range(sh[0]):
      for j in range(sh[1]):
        new_grid[i][j] += int(np.sin(i/wavePeriodDivisor*np.pi + (offset/6 % (2*np.pi))) * max_shift)
        new_grid[i][j] += int(np.cos(j/wavePeriodDivisor*np.pi + (offset/6 % (2*np.pi))) * max_shift)
    return new_grid

def grid_to_mesh(src_grid, dst_grid):
    assert(src_grid.shape == dst_grid.shape)
    mesh = []
    for i in range(src_grid.shape[0] - 1):
        for j in range(src_grid.shape[1] - 1):
            src_quad = [src_grid[i    , j    , 0], src_grid[i    , j    , 1],
                        src_grid[i + 1, j    , 0], src_grid[i + 1, j    , 1],
                        src_grid[i + 1, j + 1, 0], src_grid[i + 1, j + 1, 1],
                        src_grid[i    , j + 1, 0], src_grid[i    , j + 1, 1]]
            dst_quad = [dst_grid[i    , j    , 0], dst_grid[i    , j    , 1],
                        dst_grid[i + 1, j    , 0], dst_grid[i + 1, j    , 1],
                        dst_grid[i + 1, j + 1, 0], dst_grid[i + 1, j + 1, 1],
                        dst_grid[i    , j + 1, 0], dst_grid[i    , j + 1, 1]]
            dst_rect = quad_to_rect(dst_quad)
            mesh.append([dst_rect, src_quad])
    return mesh

testGrid = Image.open("assets\\testgrid.png")
testEye = Image.open("assets\\testeye.png")

loop = 0
while True:
    loop = loop + 1


    im = testGrid
    dst_grid = griddify(shape_to_rect(im.size), 32, 32)
    src_grid = distort_grid(dst_grid, 50, 9, loop)
    mesh = grid_to_mesh(src_grid, dst_grid)
    im = im.transform(im.size, Image.MESH, mesh)

    open_cv_image = cv2.cvtColor(np.array(im), cv2.COLOR_RGBA2BGRA)

    im = testEye
    # im = im.resize((round(im.size[0]*2), round(im.size[1]*2)))
    im = im.resize((round(im.size[0]*.2), round(im.size[1]*.2)))
    dst_grid = griddify(shape_to_rect(im.size), 6, 4)
    src_grid = distort_grid(dst_grid, np.abs(15-loop*3%30), 6, 20)
    mesh = grid_to_mesh(src_grid, dst_grid)
    im = im.transform(im.size, Image.MESH, mesh)
    # im = im.resize((round(im.size[0]*0.5), round(im.size[1]*0.5)))
    open_cv_eye = cv2.cvtColor(np.array(im), cv2.COLOR_RGBA2BGRA)

    x, y = open_cv_eye.shape[0], open_cv_eye.shape[1]
    alpha = open_cv_eye[:, :, 3] / 255.0

    srcRGB = open_cv_image[...,:3]
    dstRGB = open_cv_eye[...,:3]
    srcA = open_cv_image[...,3]/255.0
    dstA = open_cv_eye[...,3]/255.0
    outA = srcA[400:400+x, 400:400+y] + dstA*(1-srcA[400:400+x, 400:400+y])
    outRGB = (srcRGB[400:400+x, 400:400+y]*srcA[400:400+x, 400:400+y,np.newaxis] + dstRGB*dstA[...,np.newaxis]*(1-srcA[400:400+x, 400:400+y,np.newaxis])) / outA[...,np.newaxis]
    # open_cv_image[:, :, 0] = (1. - alpha) * open_cv_image[:, :, 0] + alpha * open_cv_eye[:, :, 0]
    # open_cv_image[:, :, 1] = (1. - alpha) * open_cv_image[:, :, 1] + alpha * open_cv_eye[:, :, 1]
    # open_cv_image[:, :, 2] = (1. - alpha) * open_cv_image[:, :, 2] + alpha * open_cv_eye[:, :, 2]
    # open_cv_image[400:400+x, 400:400+x,  0] = (1. - alpha) * open_cv_image[400:400+x, 400:400+y,  0] + alpha * open_cv_eye[:, :, 0]
    # open_cv_image[400:400+x, 400:400+x,  1] = (1. - alpha) * open_cv_image[400:400+x, 400:400+y,  1] + alpha * open_cv_eye[:, :, 1]
    # open_cv_image[400:400+x, 400:400+x, 2] = (1. - alpha) * open_cv_image[400:400+x, 400:400+y,  2] + alpha * open_cv_eye[:, :, 2]
    # open_cv_image[400:400+x, 400:400+y, 0:3] = (1. - alpha) * open_cv_image[400:400+x, 400:400+y, 0:3] + alpha * open_cv_eye[:, :, 0:3]
    open_cv_image[400:400+x, 400:400+y] = np.dstack((outRGB,outA*255)).astype(np.uint8)


    cv2.imshow("Test", open_cv_image)


    key = cv2.waitKey(1)

    if key == ord('q'):
        break
    if key == 27: #esc
        break
