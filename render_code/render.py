import open3d as o3d
import numpy as np
import os
from tqdm import tqdm
import torch
from PIL import Image
import os
import sys
from camera_in_ex_para import *
from utlis import *
import shutil

import matplotlib.pyplot as plt
import sys, os
sys.path.append("./smpl")
from smpl import SMPL,SMPL_MODEL_DIR
import argparse

def options():
    parser = argparse.ArgumentParser(description='rendering ...')
    parser.add_argument('--pkl_path', type=str, help='pkl path',default='../data/pub_datas.pkl')
    parser.add_argument('--path_root', type=str, help='path_root',default='../data/')
    parser.add_argument('--id', type=int, help='id',default='10')
    args = parser.parse_args()
    return args

other_path_list = ["other_1","other_2","other_3","other_4"]
color_list = [
    [1, 0.75, 0.2],
    [1, 0.75, 0.8],
    [0, 1.0, 0.2],
    [0, 0.2, 1.0]
]
save_obj_path = './save_obj/'
save_gif_path = './gif/'
os.makedirs('./frames/',exist_ok=True)
smpl_model = SMPL(SMPL_MODEL_DIR, create_transl=False)
shape_blob = torch.Tensor(np.loadtxt("./shape.txt"))
    
def main():
    args = options()
    datas = np.load(args.pkl_path,allow_pickle=True)
    
    index = int(args.id) 
    data = datas[index]

    
    name_id = data['index']
    # print(name_id)
    dense_name = data['dense']['dense_name']
    R,T = np.array(data['dense']['R']).reshape(3,3),np.array(data['dense']['T'])

    # prepare for body OBJ saving
    os.makedirs(save_obj_path,exist_ok=True)
    os.makedirs(save_gif_path,exist_ok=True)
    obj_path = f'{save_obj_path}{name_id}_target'
    os.makedirs(obj_path,exist_ok=True)

    for other_id in other_path_list:
        if other_id in data.keys():
            globalR_mul,trans_mul,pose_blob=np.array(data[other_id][:,:3]),np.array(data[other_id][:,3:6]),np.array(data[other_id][:,6:])
            output = smpl_model(betas=shape_blob.reshape(1,-1), 
                                body_pose=torch.Tensor(pose_blob),          # M*69 (pose[:,3:])
                                global_orient=torch.Tensor(globalR_mul),    # M*3  (pose[:,:3])
                                transl=torch.Tensor(trans_mul))             # M*3  global T'''
            obj_path_instance = f'{save_obj_path}{name_id}_{other_id}'
            verts = output.vertices
            if not os.path.exists(obj_path_instance):
                os.makedirs(obj_path_instance,exist_ok=True)
            for j in range(len(verts)):
                smpl2obj(verts[j], f"{obj_path_instance}/{j}.obj")

    globalR,trans,pose_blob=np.array(data["livehps_op"][:,:3]),np.array(data["livehps_op"][:,3:6]),np.array(data["livehps_op"][:,6:])
    output = smpl_model(betas=shape_blob.reshape(1,-1), 
                        body_pose=torch.Tensor(pose_blob),      # M*69 (pose[:,3:])
                        global_orient=torch.Tensor(globalR),    # M*3  (pose[:,:3])
                        transl=torch.Tensor(trans))             # M*3  global T'''

    for j in range(len(output.vertices)):
        smpl2obj(output.vertices[j], f"{obj_path}/{j}.obj")

    # dense scene
    M = 1000000
    ply_file_path = f"{args.path_root}/process/{dense_name}"  # ply path
    point_cloud = o3d.io.read_point_cloud(ply_file_path)
    point_cloud_t = trans_crop(point_cloud,R,T,trans[0])
    downsample = np.random.choice(point_cloud_t.shape[0], M)
    point_cloud_t = point_cloud_t[downsample]
    point_cloud_crop = o3d.geometry.PointCloud()
    point_cloud_crop.points = o3d.utility.Vector3dVector(point_cloud_t[:,:3])
    point_cloud_crop.colors = o3d.utility.Vector3dVector(point_cloud_t[:,3:])
    save_view_point(point_cloud_crop, "camera.json")  # 
    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name='visual', width=800, height=600)
    cam_params = o3d.io.read_pinhole_camera_parameters("camera.json")
    mesh_normal = o3d.geometry.TriangleMesh()
    mesh_other_list = []
    for i in range(4):
        mesh_other_list.append(o3d.geometry.TriangleMesh())

    other_count = 0
    
    ## begin rendering
    for i in range(trans.shape[0]):
        mesh = o3d.io.read_triangle_mesh(f"{obj_path}/{i}.obj")
        mesh_normal.triangles = o3d.utility.Vector3iVector(mesh.triangles)
        mesh_normal.vertices = o3d.utility.Vector3dVector(mesh.vertices)
        mesh_normal.compute_vertex_normals()
        for k in range(4):
            mesh_path = f'{save_obj_path}{name_id}_other_{k + 1}/{i}.obj'
            if os.path.exists(f'{save_obj_path}{name_id}_other_{k + 1}/{i}.obj'): 
                mesh_mul = o3d.io.read_triangle_mesh(mesh_path)
                mesh_other_list[k].triangles = o3d.utility.Vector3iVector(mesh_mul.triangles)
                mesh_other_list[k].vertices = o3d.utility.Vector3dVector(mesh_mul.vertices)
                mesh_other_list[k].compute_vertex_normals()
                num_vertices = np.asarray(mesh_other_list[k].vertices).shape[0]
                color = color_list[k]
                colors = np.repeat([color], num_vertices, axis=0)
                mesh_other_list[k].vertex_colors = o3d.utility.Vector3dVector(colors)
                other_count += 1
        if i==0:
            vis.add_geometry(point_cloud_crop)
            vis.add_geometry(mesh_normal)
            for k in range(other_count):
                vis.add_geometry(mesh_other_list[k])
            view_ctl = vis.get_view_control()
            view_ctl.convert_from_pinhole_camera_parameters(cam_params)
        else: 
            vis.update_geometry(point_cloud_crop)
            vis.update_geometry(mesh_normal)
            for k in range(other_count):
                try:
                    vis.update_geometry(mesh_other_list[k])
                except:
                    pass
        view_ctl = vis.get_view_control()
        view_ctl.convert_from_pinhole_camera_parameters(cam_params)

        vis.poll_events()
        vis.update_renderer()
        image = vis.capture_screen_float_buffer(False)
        image = np.asarray(image)
        plt.imsave(f"frames/frame_{i:03d}.png", np.asarray(image), dpi=1)

    shutil.rmtree(save_obj_path)

    images = [Image.open(f"frames/frame_{i:03d}.png") for i in range(trans.shape[0])]
    gif_filename = f'{save_gif_path}{name_id}.gif'
    images[0].save(gif_filename, save_all=True, append_images=images[1:], optimize=False, duration=3)
    shutil.rmtree('./frames/')

if __name__ == '__main__':
    main()