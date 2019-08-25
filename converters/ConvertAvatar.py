import cv2
import numpy as np

import imagelib
from facelib import FaceType, LandmarksProcessor
from utils.cv2_utils import *

def process_frame_info(frame_info, inp_sh):
    img_uint8 = cv2_imread (frame_info.filename)
    img_uint8 = imagelib.normalize_channels (img_uint8, 3)        
    img = img_uint8.astype(np.float32) / 255.0        

    img_mat = LandmarksProcessor.get_transform_mat (frame_info.landmarks_list[0], inp_sh[0], face_type=FaceType.FULL_NO_ALIGN)
    img = cv2.warpAffine( img, img_mat, inp_sh[0:2], flags=cv2.INTER_CUBIC )
    return img
    
def ConvertFaceAvatar (cfg, prev_temporal_frame_infos, frame_info, next_temporal_frame_infos):
    inp_sh = cfg.predictor_input_shape

    prev_imgs=[]
    next_imgs=[]
    for i in range(cfg.temporal_face_count):
        prev_imgs.append( process_frame_info(prev_temporal_frame_infos[i], inp_sh) )
        next_imgs.append( process_frame_info(next_temporal_frame_infos[i], inp_sh) )
    img = process_frame_info(frame_info, inp_sh)

    prd_f = cfg.predictor_func ( prev_imgs, img, next_imgs )

    if cfg.super_resolution_mode != 0:
        prd_f = cfg.superres_func(cfg.super_resolution_mode, prd_f)
        
    out_img = np.clip(prd_f, 0.0, 1.0)

    if cfg.add_source_image:
        out_img = np.concatenate ( [cv2.resize ( img, (prd_f.shape[1], prd_f.shape[0])  ), 
                                    out_img], axis=1 )

    return (out_img*255).astype(np.uint8)