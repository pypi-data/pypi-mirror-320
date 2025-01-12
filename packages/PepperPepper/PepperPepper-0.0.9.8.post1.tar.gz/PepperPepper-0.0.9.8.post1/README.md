# Pepper
## Version:0.0.9.6
PepperV0.0.9.6

FFT_PriorFilter: We added a Fourier prior module to the layers/custom_layer.py for prior knowledge filter.

SCTransNet: We reproduce the SCTrans model for infrared small target detection

## Version:0.0.9.7
get_all_images: It can get all the images in a directory and pass set the load_images to control whether it load the image or return path.it locate the datasets/dataset_utils.py

get_img_norm_cfg: It can get the norm parameters in a directory all the images to adjust.it locate the datasets/dataset_utils.py

DataSetLoader: It is Dataset for IRSTD datasets.it locate the IRSTD/datasets

## Version:0.0.9.8
IRSTDTrainer: The training of the task is integrated for IRSTD. It locate the IRSTD/callbacks

## Version:0.0.9.8-1
We repair the IRSTDTrainer's Test epoch num error
