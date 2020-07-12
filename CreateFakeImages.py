import sys
import time
import numpy as np
import cv2
import os
from tqdm import tqdm
import random
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches
import matplotlib as mpl
from glob import glob
from PIL import Image, ImageDraw, ImageColor

annotations_dir = "img/Results/" # ---------- dir for new annotations
images_dir = "img/Results/" # ---------- dir for new Images

obj_floder_1 = [
    "img/sourse_png/DualShock",
"img/sourse_png/minolta",
"img/sourse_png/Zenit_122",
] # ---------------------------- Folders with images. Each folder is a different class

Count_images_for_each_class = [
    100,100,100
] # ----------------------------How much  images of each class do you want

backgr_folder = [
    "img/backgrounds/"
]   # ---------------------------------- Folders with backgrounds

Count_of_mixed_images = 200 # ----------------------------Amounts of images with a lot of objects

Name_files = "DataSet_v1_" # ------------------------------- Name of output images and annotations

add_filters = False  # --------------------------------- if you want to change colors or color temperature... Don't recommend.

add_MotionBlur = -1 # From -1 to 10  (if 3 then 30% chance of making Blur for each image) (-1 = off)

angle_rotat = 4 # angle of rotation

Size_range_from = 4    # for example:    2.3 ---------->   Original_size_img / 2.3  = size obj_img
Size_range_to = 5

if len(obj_floder_1) != len(Count_images_for_each_class):
    print("Count of folders and count of classes is not the same:" + str(len(obj_floder_1) )+"  "+ str(len(Count_images_for_each_class)))
    exit()


imgs_fns = []
backgr_fns = []
for fold in obj_floder_1:
    imgs_fns.append(glob(fold + "/*.png")) #------------------ change extension if you need
for fold in backgr_folder:
    backgr_fns.append(glob(fold + "/*.jpg"))  #-----------------------change extension if you need



time_show = False          # -------------------------- For debugging


c_maps = [
    # 'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
    #             'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
    #             'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn'

    'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
    'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
    'hot', 'afmhot', 'gist_heat', 'copper',

    # 'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
    #             'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic'
    #
    # 'twilight', 'twilight_shifted', 'hsv'

    # 'Pastel1', 'Pastel2', 'Paired', 'Accent',
    #                         'Dark2', 'Set1', 'Set2', 'Set3',
    #                         'tab10', 'tab20', 'tab20b', 'tab20c'

    'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
    'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg',
    'gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar'
] # ---------------- filters for color change

count = 0

def randomVec():
    randomVector = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 255)
    return randomVector


def watermark_with_transparency(input_image_path, output_image_path, watermark_im, position, scale): #---------- make mask for objeсt image
    base_image = input_image_path
    watermark = watermark_im
    watermark = watermark.resize([scale[1], scale[0]], Image.BICUBIC)
    wW, wH = watermark.size
    width, height = base_image.size
    transparent = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    transparent.paste(base_image, (0, 0))

    mask = Image.new('RGBA', (wW, wH), (0, 0, 0, 0))                                         #Create a mask
    for x in range(0, wW):
        for y in range(0, wH):
            if watermark.getpixel((x, y))[3] > 0:
                mask.putpixel((x, y), (
                    watermark.getpixel((x, y))[3], watermark.getpixel((x, y))[3], watermark.getpixel((x, y))[3],
                    watermark.getpixel((x, y))[3]))
            else:
                mask.putpixel((x, y), (0, 0, 0, 0))


    if random.randrange (0,10) < 3 and add_filters:
        watermark = watermark.convert('L')
        watermark = np.array(watermark)
        c_map = random.choice(c_maps)
        cm_hot = mpl.cm.get_cmap(c_map)
        watermark = cm_hot(watermark)

        watermark = np.uint8(watermark * 255)
        watermark = Image.fromarray(watermark)

    transparent.paste(watermark, (position[0], position[1]), mask=mask)

    return transparent



def MoutionBlur(inp_img):
    rnd_blr = random.randint(1, 200)
    size = rnd_blr
    # size = 0 
    # print(str(n) + " - Got Blur")
    # generating the kernel
    if bool(random.getrandbits(1)):
        # print(True)
        kernel_motion_blur = np.zeros((size, size))
        kernel_motion_blur[:, int((size - 1) / 2)] = np.ones(size)
        kernel_motion_blur = kernel_motion_blur / size
    else:
        # print(False)
        kernel_motion_blur = np.zeros((size, size))
        kernel_motion_blur[int((size - 1) / 2), :] = np.ones(size)
        kernel_motion_blur = kernel_motion_blur / size
    inp_img = cv2.copyMakeBorder(inp_img, 150, 150, 150, 150, cv2.BORDER_CONSTANT, value=[0, 0, 0, 0])
    # applying the kernel to the input image
    output = cv2.filter2D(inp_img, -1, kernel_motion_blur)
    return output


def obj_rotate(input_image_path):
    img = input_image_path
    IMG_width_befor, IMG_height_befor = img.size

    rand_angle = 0
    while(True):
        if rand_angle == 0:
            rand_angle = random.uniform(-1 * angle_rotat, angle_rotat)
        else:
            break
    img = img.rotate(rand_angle, expand=True) # angle of rotatation

    IMG_width_A, IMG_height_A = img.size

    cof_h = IMG_height_befor / IMG_height_A
    if IMG_width_befor <= IMG_width_A:
        cof_w = IMG_width_befor / IMG_width_A
    else:
        cof_w = IMG_width_A / IMG_width_befor
    img = img.resize([int(IMG_width_A), int(IMG_height_A)], Image.BICUBIC)

    return img


def SearchBoundBox(img_r, count_col_d, count_line_d, dist_col_d, dist_line_d, transparent):
    true_culumn = []
    true_line = []
    x = 0
    y = 0
    b_width = 0
    war = False
    xht = 0
    width_d, height_d = img_r.size
    for col in range(count_col_d):
        got = False
        distance_col_div_50 = height_d / 100

        for xt in range(100):
            xh = xt * distance_col_div_50
            xht = col * dist_col_d
            i = img_r.getpixel((xht, xh))
            if max(i) >= 100:
                got = True
                true_culumn.append(xht)
                war = True
        if not got and len(true_culumn) != 0 and len(true_culumn) < 20:
            true_culumn.clear()
    if len(true_culumn) != 0:
        x = true_culumn[0]
    else:
        x = 25 * dist_col_d
        img_r.show()
    b_width = (true_culumn[len(true_culumn) - 1] - x) + dist_col_d / 2
    for line in range(count_line_d):
        got = False
        distance_line_div_70 = width / 100
        for xt in range(100):
            xh = xt * distance_line_div_70
            xht = line * dist_line_d
            i = img_r.getpixel((xh, xht))
            if i[3] >= transparent:
                got = True
                true_line.append(xht)
                break
        if not got and len(true_line) != 0 and len(true_line) < 1:
            true_line.clear()
    y = true_line[0]
    b_height = (true_line[len(true_line) - 1] - y) + dist_line_d / 2
    return [x, y, b_width, b_height]

def CreateImgAndBoundBox (bg, img):
    global t_blur
    global t_convert
    global t_rotat
    global t_findB
    global t_combImg
    global t_DrawB
    height, width, depth = img.shape
    bg_height, bg_width, bg_depth = bg.shape

    if random.randrange(0, 10) < add_MotionBlur:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
        img = Image.fromarray(img)
        img.convert("RGBA")
        img = obj_rotate(img)
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGRA)
        img = MoutionBlur(img)
        t_blur = time.perf_counter()
    else:
        t_blur = "without Blur"
    bg = cv2.cvtColor(bg, cv2.COLOR_BGRA2RGBA)
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
    bg = Image.fromarray(bg)
    img = Image.fromarray(img)
    bg.convert("RGBA")
    img.convert("RGBA")

    img_r = img
    t_convert = time.perf_counter()
    img_r = obj_rotate(img)
    t_rotat = time.perf_counter()
    width, height = img_r.size
    cout_col = 100
    count_line = 100
    dist_col = width / cout_col
    dist_line = height / count_line
    transpar = 100
    BoundBox = SearchBoundBox(img_r, cout_col, count_line, dist_col, dist_line, transpar)
    t_findB = time.perf_counter()

    tru = True
    while (tru):
        rand_sc = random.uniform(Size_range_from, Size_range_to)

        scale_obj = (int(height / rand_sc), int(width / rand_sc))

        c = bg_width - int(scale_obj[0] / 2)
        f = bg_height - int(scale_obj[1] / 2)
        if c != 0 and f != 0:
            rand_x = random.randint(0, bg_width - int(scale_obj[0] / 2))
            rand_y = random.randint(0, bg_height - int(scale_obj[1] / 2))
            tru = False




    BoundBox[0] = (BoundBox[0] / rand_sc) + rand_x
    BoundBox[1] = rand_y + (BoundBox[1] / rand_sc)
    BoundBox[2] = BoundBox[2] / rand_sc
    BoundBox[3] = BoundBox[3] / rand_sc
    final_img = watermark_with_transparency(bg, "", img_r, (rand_x, rand_y), scale_obj)
    t_combImg = time.perf_counter()

    if random.randint(0, 10) > 7:
        draw = ImageDraw.Draw(final_img)
        vec = randomVec()
        tr = True
        while (tr):
            ran_box_x1 = random.randrange(int(BoundBox[0]), int(BoundBox[0] + BoundBox[2]))
            ran_box_y1 = random.randrange(int(BoundBox[1]), int(BoundBox[1] + BoundBox[3]))
            ran_box_x2 = random.randrange(int(BoundBox[0]), int(BoundBox[0] + BoundBox[2]))
            ran_box_y2 = random.randrange(int(BoundBox[1]), int(BoundBox[1] + BoundBox[3]))
            if ran_box_x2 > ran_box_x1:
                if ran_box_y2 > ran_box_y1:
                    ploch_1 = (ran_box_x2 - ran_box_x1) * (ran_box_y2 - ran_box_y1)
                else:
                    ploch_1 = (ran_box_x2 - ran_box_x1) * (ran_box_y1 - ran_box_y2)
            else:
                if ran_box_y2 > ran_box_y1:
                    ploch_1 = (ran_box_x1 - ran_box_x2) * (ran_box_y2 - ran_box_y1)
                else:
                    ploch_1 = (ran_box_x1 - ran_box_x2) * (ran_box_y1 - ran_box_y2)
            if ploch_1 < ( (BoundBox[2] * BoundBox[3]) * 0.15):
                draw.rectangle([ran_box_x1, ran_box_y1, ran_box_x2, ran_box_y2 ], fill=vec)
                tr = False
        tr = True
        vec = randomVec()

        while (tr):

            ran_box_x1 = random.randrange(int(BoundBox[0]), int(BoundBox[0] + BoundBox[2]))
            ran_box_y1 = random.randrange(int(BoundBox[1]), int(BoundBox[1] + BoundBox[3]))
            ran_box_x2 = random.randrange(int(BoundBox[0]), int(BoundBox[0] + BoundBox[2]))
            ran_box_y2 = random.randrange(int(BoundBox[1]), int(BoundBox[1] + BoundBox[3]))
            if ran_box_x2 > ran_box_x1:
                if ran_box_y2 > ran_box_y1:
                    ploch_1 = (ran_box_x2 - ran_box_x1) * (ran_box_y2 - ran_box_y1)
                else:
                    ploch_1 = (ran_box_x2 - ran_box_x1) * (ran_box_y1 - ran_box_y2)
            else:
                if ran_box_y2 > ran_box_y1:
                    ploch_1 = (ran_box_x1 - ran_box_x2) * (ran_box_y2 - ran_box_y1)
                else:
                    ploch_1 = (ran_box_x1 - ran_box_x2) * (ran_box_y1 - ran_box_y2)
            if ploch_1 <( (BoundBox[2] * BoundBox[3]) * 0.1):

                draw.rectangle([ran_box_x1, ran_box_y1, ran_box_x2, ran_box_y2 ], fill=vec)
                tr = False
    else:
        draw = ImageDraw.Draw(final_img)

    t_DrawB = time.perf_counter()
    width, height = final_img.size

    del draw

    x_centr = (BoundBox[0] + (BoundBox[2] / 2)) / width
    y_centr = (BoundBox[1] + (BoundBox[3] / 2)) / height
    x_width = BoundBox[2] / width
    y_heiht = BoundBox[3] / height
    return final_img, x_centr, y_centr,x_width,y_heiht

Count_fal = 0
num_of_obj = 0
for calss_i in Count_images_for_each_class:

    for n in range(0, calss_i):
        try:


            t_start = time.perf_counter()
            img_fn = random.choice(imgs_fns[num_of_obj])
            img = cv2.imread(img_fn, cv2.IMREAD_UNCHANGED)
            height, width, depth = img.shape
            r = 100 / float(width)
            cv2.resize(img, (100, int(height * r)), interpolation=cv2.INTER_AREA)


            backgr_name = random.choice(random.choice(backgr_fns))

            bg = cv2.imread(backgr_name, cv2.IMREAD_UNCHANGED)

            bg_height, bg_width, bg_depth = bg.shape

         

            t_load_img = time.perf_counter()


            final_img, x_centr, y_centr, x_width, y_heiht =CreateImgAndBoundBox(bg,img)
            name_andtation = '{:06}.txt'.format(n)
            name_png = '{:06}.jpg'.format(n)

            annotatoin_string = str(num_of_obj) + " " + str(x_centr) + ' ' + str(y_centr) + ' ' + str(x_width) + ' ' + str(y_heiht) + '\n'

            file = open(annotations_dir  + Name_files + "_" + str(num_of_obj) + "_" + name_andtation, "w")
            file.write(annotatoin_string)
            file.close()

            final_img = final_img.convert("RGB")
            final_img.save(images_dir + Name_files + "_" + str(num_of_obj) + "_" + name_png, "JPEG")
            t_save = time.perf_counter()
            print(str(num_of_obj) + "____" + str(n))

            if (time_show):
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" + "\n" +
                      "Load of images: " + str(t_load_img) + "\n" +
                      "Motion Blur: " + str(t_blur) + "\n" +
                      "Convert from cv2 in np: " + str(t_convert) + "\n" +
                      "Rotate: " + str(t_rotat) + "\n" +
                      "Find of boundaries: " + str(t_findB) + "\n" +
                      "Combine two images :" + str(t_combImg) + "\n" +
                      "Make distortion: " + str(t_DrawB) + "\n" +
                      "Save: " + str(t_save) + "\n" +
                      "Total time for picture: " + str(t_save - t_start))
        except:
            print("Error creating image")
            Count_fal += 1
            print(Count_fal)
    num_of_obj += 1

n = 0
for mix_img in range(0, Count_of_mixed_images):

    try:
        t_start = time.perf_counter()
        count_obj_on_image = random.randint(2, 3)
        # print(count_obj_on_image)
        obj_arr = []

        for obj in range(0,count_obj_on_image ):
            obj_arr.append(random.randint(0,len(Count_images_for_each_class) - 1))

        # print(obj_arr)
        final_img = 0

        x_centr = []
        y_centr = []
        x_width = []
        y_heiht = []

        backgr_name = random.choice(random.choice(backgr_fns))
        # print(backgr_name)
        bg = cv2.imread(backgr_name, cv2.IMREAD_UNCHANGED)
        # bg = cv2.resize(bg,(width,height))
        bg_height, bg_width, bg_depth = bg.shape

        ii = 0
        for index in obj_arr:
            t_start = time.perf_counter()
            img_fn = random.choice(imgs_fns[index])
            # print(img_fn)

            img = cv2.imread(img_fn, cv2.IMREAD_UNCHANGED)
            height, width, depth = img.shape

           

            t_load_img = time.perf_counter()

            final_img, x_c, y_c, x_w, y_h = CreateImgAndBoundBox(bg, img)


            x_centr.append(x_c)
            y_centr.append(y_c)
            x_width.append(x_w)
            y_heiht.append(y_h)
            bg = final_img
            bg = cv2.cvtColor(np.array(bg), cv2.COLOR_RGBA2BGRA)
            ii +=1

        # print(x_width)

        annotatoin_string = ""
        name_str = ""
        index = 0
        for obj in obj_arr:
            annotatoin_string += str(obj_arr[index]) + " " + str(x_centr[index]) + ' ' + str(y_centr[index]) + ' ' + str(x_width[index]) + ' ' + str(
                y_heiht[index]) + '\n'
            name_str += "-" + str(obj_arr[index]) + "-"
            # print(x_centr[index])
            index += 1


        name_andtation = '{:06}.txt'.format(n)
        name_png = '{:06}.jpg'.format(n)

        file = open(annotations_dir + Name_files + "_" + name_str + "_" + name_andtation, "w")
        file.write(annotatoin_string)
        file.close()

        final_img = final_img.convert("RGB")
        final_img.save(images_dir + Name_files + "_" + name_str + "_" + name_png, "JPEG")
        t_save = time.perf_counter()
        print(name_str + "____" + str(n))

        if (time_show):
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" + "\n" +
                   # "Load of images: " + str(t_load_img) + "\n" +
                  "Motion Blur: " + str(t_blur) + "\n" +
                  "Convert from cv2 in np: " + str(t_convert) + "\n" +
                  "Rotate:  " + str(t_rotat) + "\n" +
                  "Find of boundaries:  " + str(t_findB) + "\n" +
                  "Combine two images :" + str(t_combImg) + "\n" +
                  "Make distortion: " + str(t_DrawB) + "\n" +
                  "Save:" + str(t_save) + "\n" +
                  "Total time for picture: " + str(t_save - t_start))
    except:
        print("Error creating image")
        Count_fal += 1
        print(Count_fal)
    n += 1
print("Count of errors: ",  Count_fal )
