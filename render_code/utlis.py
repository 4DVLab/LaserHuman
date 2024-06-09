import open3d as o3d
import numpy as np
import os
from tqdm import tqdm
import torch
from PIL import Image
import os
import sys
import warnings
def smpl2obj(vertices, path):
    fs = list()
    with open("smpl/smpl.obj") as f:
        lines = f.readlines()
        for line in lines:
            l = line.split(" ")
            if "f" in l:
                fs.append((int(l[1]), int(l[2]), int(l[3])))

    with open(path, "w") as f:
        for v in vertices:
            f.write(( 'v %f %f %f\n' % ( v[0], v[1], v[2]) ))
        for face in fs:
            f.write(( 'f %d %d %d\n' % ( face[0], face[1], face[2]) ))


def save_view_point(ply, filename):
    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name='visual', width=800, height=600)
    vis.add_geometry(ply)
    vis.run()  # user changes the view and press "q" to terminate
    param = vis.get_view_control().convert_to_pinhole_camera_parameters()
    o3d.io.write_pinhole_camera_parameters(filename, param)
    vis.destroy_window()

def load_view_point(ply, filename):
    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name='visual',width=800, height=600)
    ctr = vis.get_view_control()
    param = o3d.io.read_pinhole_camera_parameters(filename)
    vis.add_geometry(ply)
    ctr.convert_from_pinhole_camera_parameters(param)
    vis.run()
    vis.destroy_window()

def trans_crop(point_cloud,R,T,trans):
    pc = np.array(point_cloud.points)
    c = np.array(point_cloud.colors)
    T_ = T[:3].dot(R)
    # downsample = np.random.choice(self.vertices.shape[0], self.N)
    # vertices_downsample = self.vertices[downsample]
    # pc = pc[:,:3].dot(R)- T_[:3]
    pc = pc[:,:3] - T
    pc = np.matmul(R.T,pc.T).T

    L = 10
    mask = (pc[:, 0] < trans[0]+L) &  (pc[:, 0] > trans[0]-L) & \
        (pc[:, 1] < trans[1]+L) &  (pc[:, 1] > trans[1]-L) & \
        (pc[:, 2] < trans[2]+2) &  (pc[:, 2] > trans[2]-4) 
    crop_downsample = pc[mask]
    c = c[mask]
    return np.concatenate((crop_downsample,c),1)

