import numpy as np
import cv2

distortion_coefficients1 = np.array([-0.145834, 0.197798, -0.001340, -0.000277, 0.000000])
distortion_coefficients2 = np.array([-0.1377, 0.1915, -0.002118, -0.000510, 0.000000])
distortion_coefficients6 = np.array([-0.148392, 0.208062, -0.000187, 0.000458, 0.000000])
distortion_coefficients = np.array([0,0,0,0,0])
'''
This can be used for projcet the pc on the images, we only use front three cameras
(cam1,cam2,cam6,cam1 is the center camera)
'''
h, w = 1200, 1920
ex_matrix_cam1 = np.array([ # cam1
    [0.017452406437283574, -0.999847695156391, -5.551115123125783e-17, -0.024703597383298997],
    [-0.012215140126845492, -0.00021321606402130433, -0.999925369660452, 0.03975440225788578],
    [0.9997730761834054, 0.01745110395826527, -0.012217000835247127, -0.09080308692722944]
])
ex_matrix_cam2 = np.array([ # cam2
    [-0.8598522715968737, -0.5105429179116056, 0.0, -0.009863877519666886],
    [0.004455270896599028, -0.0075035313714476234, -0.9999619230641715, -0.06082809641205974],
    [0.5105234780016824, -0.8598195310571061, 0.008726535498373912, -0.08629482217741014]
])
ex_matrix_cam6 = np.array([ # cam6
    [0.8720692724321204, -0.4893824517488462, 0.0, -0.00012454852885848515],
    [8.326672684688674e-17, 1.6653345369377348e-16, -0.9999999999999998, -0.04931984031870221],
    [0.48938245174884615, 0.8720692724321204, 1.6653345369377348e-16, -0.08243496651085405]
])
in_matrix_cam1 = np.array([
    [1288.27043,    0.     ,  944.73479],
            [0.     , 1288.57055,  617.01932],
            [0.     ,    0.     ,    1.     ]
])
in_matrix_cam2 = np.array([[1293.11391,    0.     ,  974.14537],
            [0.     , 1295.19251,  644.25513],
            [0.     ,    0.     ,    1.     ]
])
in_matrix_cam6 = np.array([
[1294.81375,    0.     ,  926.57962],
            [0.     , 1295.83987,  624.76414],
            [0.     ,    0.     ,    1.     ]
])

# in_matrix
newcameramtx_cam1, _ = cv2.getOptimalNewCameraMatrix(in_matrix_cam1, distortion_coefficients1, (w,h), 0, (w,h))
newcameramtx_cam2, _ = cv2.getOptimalNewCameraMatrix(in_matrix_cam2, distortion_coefficients2, (w,h), 0, (w,h))
newcameramtx_cam6, _ = cv2.getOptimalNewCameraMatrix(in_matrix_cam6, distortion_coefficients, (w,h), 0, (w,h))



''' sample code

# lidar2camera
    points = np.fromfile(data_path, dtype=np.float32).reshape([-1,3])
    points = np.concatenate((points,np.ones((points.shape[0],1))),1)
    points_T = np.transpose(points)

    points_T_camera = np.dot(ex_matrix_cam, points_T)
# camera2pixel
    pixel = np.dot(in_matrix_cam, points_T_camera).T
    pixel_xy = np.array([x / x[2] for x in pixel])[:, 0:2]
    pixel_xy = np.around(pixel_xy).astype(int)

    image = np.array(cv2.imread(image_path))
    mask = (pixel_xy[:, 0] >= 0) & (pixel_xy[:, 0] < 1920) & \
        (pixel_xy[:, 1] >= 0) & (pixel_xy[:, 1] < 1200) & \
        (points_T_camera[2, :] > 0)

    filtered_coords = pixel_xy[mask]
'''