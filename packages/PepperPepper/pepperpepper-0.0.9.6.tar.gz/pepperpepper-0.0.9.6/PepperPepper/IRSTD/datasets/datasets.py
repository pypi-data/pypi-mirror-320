from PepperPepper.environment import torch, Image, PIL, np, random, os, shutil, torchvision
from PepperPepper.IRSTD.tools.utils import get_img_norm_cfg, Normalized, random_crop, PadImg


class TrainSetLoader(torch.utils.data.Dataset):
    def __init__(self, dataset_dir, dataset_name, patch_size, img_norm_cfg=None):
        super(TrainSetLoader).__init__()
        self.dataset_name = dataset_name
        self.dataset_dir = dataset_dir + '/' + dataset_name
        self.patch_size = patch_size
        if not os.path.exists(self.dataset_dir +'/img_idx/train_' + dataset_name + '.txt') and os.path.exists(self.dataset_dir +'/img_idx/train.txt'):
            shutil.copyfile(self.dataset_dir +'/img_idx/train.txt', self.dataset_dir +'/img_idx/train_' + dataset_name + '.txt')
        with open(self.dataset_dir +'/img_idx/train_' + dataset_name + '.txt', 'r') as f:
            self.train_list = f.read().splitlines()

        with open(self.dataset_dir + '/img_idx/train_' + dataset_name + '.txt', 'r') as f:
            self.train_list = f.read().splitlines()

        if img_norm_cfg == None:
            self.img_norm_cfg = get_img_norm_cfg(dataset_name, dataset_dir)
        else:
            self.img_norm_cfg = img_norm_cfg

        self.tranform = augumentation()


    def __getitem__(self, idx):
        try:
            img = Image.open(
                (self.dataset_dir + '/images/' + self.train_list[idx] + '.png').replace('//', '/')).convert('I')
            mask = Image.open((self.dataset_dir + '/masks/' + self.train_list[idx] + '.png').replace('//', '/'))
        except:
            img = Image.open(
                (self.dataset_dir + '/images/' + self.train_list[idx] + '.bmp').replace('//', '/')).convert('I')
            mask = Image.open((self.dataset_dir + '/masks/' + self.train_list[idx] + '.bmp').replace('//', '/'))
        img = Normalized(np.array(img, dtype=np.float32), self.img_norm_cfg)
        mask = np.array(mask, dtype=np.float32) / 255.0
        if len(mask.shape) > 2:
            mask = mask[:, :, 0]

        img_patch, mask_patch = random_crop(img, mask, self.patch_size, pos_prob=0.5)
        img_patch, mask_patch = self.tranform(img_patch, mask_patch)
        img_patch, mask_patch = img_patch[np.newaxis, :], mask_patch[np.newaxis, :]
        img_patch = torch.from_numpy(np.ascontiguousarray(img_patch))
        mask_patch = torch.from_numpy(np.ascontiguousarray(mask_patch))
        return img_patch, mask_patch

    def __len__(self):
        return len(self.train_list)



class TrainSetLoaderV2(torch.utils.data.Dataset):
    def __init__(self, dataset_dir, dataset_name, patch_size, img_norm_cfg=None):
        super(TrainSetLoaderV2).__init__()
        self.dataset_name = dataset_name
        self.dataset_dir = dataset_dir + '/' + dataset_name
        self.patch_size = patch_size
        if not os.path.exists(self.dataset_dir +'/img_idx/train_' + dataset_name + '.txt') and os.path.exists(self.dataset_dir +'/img_idx/train.txt'):
            shutil.copyfile(self.dataset_dir +'/img_idx/train.txt', self.dataset_dir +'/img_idx/train_' + dataset_name + '.txt')
        with open(self.dataset_dir +'/img_idx/train_' + dataset_name + '.txt', 'r') as f:
            self.train_list = f.read().splitlines()

        with open(self.dataset_dir + '/img_idx/train_' + dataset_name + '.txt', 'r') as f:
            self.train_list = f.read().splitlines()

        if img_norm_cfg == None:
            self.img_norm_cfg = get_img_norm_cfg(dataset_name, dataset_dir)
        else:
            self.img_norm_cfg = img_norm_cfg

        self.tranform = augumentation()


    def __getitem__(self, idx):
        try:
            img = Image.open(
                (self.dataset_dir + '/images/' + self.train_list[idx] + '.png').replace('//', '/')).convert('I')
            mask = Image.open((self.dataset_dir + '/masks/' + self.train_list[idx] + '.png').replace('//', '/'))
        except:
            img = Image.open(
                (self.dataset_dir + '/images/' + self.train_list[idx] + '.bmp').replace('//', '/')).convert('I')
            mask = Image.open((self.dataset_dir + '/masks/' + self.train_list[idx] + '.bmp').replace('//', '/'))

        img = img.resize((self.patch_size, self.patch_size), Image.BILINEAR)
        mask = mask.resize((self.patch_size, self.patch_size), Image.NEAREST)

        img = Normalized(np.array(img, dtype=np.float32), self.img_norm_cfg)
        mask = np.array(mask, dtype=np.float32) / 255.0
        if len(mask.shape) > 2:
            mask = mask[:, :, 0]

        # img_patch, mask_patch = random_crop(img, mask, self.patch_size, pos_prob=0.5)

        img_patch, mask_patch = self.tranform(img, mask)
        img_patch, mask_patch = img_patch[np.newaxis, :], mask_patch[np.newaxis, :]
        img_patch = torch.from_numpy(np.ascontiguousarray(img_patch))
        mask_patch = torch.from_numpy(np.ascontiguousarray(mask_patch))
        return img_patch, mask_patch

    def __len__(self):
        return len(self.train_list)



class TestSetLoaderV2(torch.utils.data.Dataset):
    def __init__(self, dataset_dir, dataset_name , patch_size, img_norm_cfg=None):
        super(TestSetLoaderV2).__init__()
        self.patch_size = patch_size
        self.size = (int(self.patch_size), int(self.patch_size))
        # self.resize_transform = torchvision.transforms.Resize(self.size)  # 新的宽度和高度
        self.dataset_dir = dataset_dir + '/' + dataset_name
        with open(self.dataset_dir + '/img_idx/test_' + dataset_name + '.txt', 'r') as f:
            self.test_list = f.read().splitlines()
        if img_norm_cfg == None:
            self.img_norm_cfg = get_img_norm_cfg(dataset_name, dataset_dir)
        else:
            self.img_norm_cfg = img_norm_cfg


    def __len__(self):
        return len(self.test_list)

    def __getitem__(self, idx):
        try:
            img = Image.open((self.dataset_dir + '/images/' + self.test_list[idx] + '.png').replace('//', '/')).convert('I')
            mask = Image.open((self.dataset_dir + '/masks/' + self.test_list[idx] + '.png').replace('//', '/')).convert('L')
        except:
            img = Image.open((self.dataset_dir + '/images/' + self.test_list[idx] + '.bmp').replace('//', '/')).convert('I')
            mask = Image.open((self.dataset_dir + '/masks/' + self.test_list[idx] + '.bmp').replace('//', '/')).convert('L')

        img = img.resize((self.patch_size, self.patch_size), Image.BILINEAR)
        mask = mask.resize((self.patch_size, self.patch_size), Image.NEAREST)


        img = Normalized(np.array(img, dtype=np.float32), self.img_norm_cfg)
        mask = np.array(mask, dtype=np.float32) / 255.0
        if len(mask.shape) > 2:
            mask = mask[:,:,0]

        h, w = img.shape
        img = PadImg(img)
        mask = PadImg(mask)

        img, mask = img[np.newaxis, :], mask[np.newaxis, :]

        img = img.astype(np.float32)
        mask = mask.astype(np.float32)

        img = torch.from_numpy(np.ascontiguousarray(img))
        mask = torch.from_numpy(np.ascontiguousarray(mask))
        return img, mask,  [self.patch_size, self.patch_size], self.test_list[idx]




class TestSetLoader(torch.utils.data.Dataset):
    def __init__(self, dataset_dir, dataset_name, img_norm_cfg=None):
        super(TestSetLoader).__init__()
        self.dataset_dir = dataset_dir + '/' + dataset_name
        with open(self.dataset_dir + '/img_idx/test_' + dataset_name + '.txt', 'r') as f:
        # with open(r'D:\05TGARS\Upload\datasets\SIRST3\img_idx\val.txt', 'r') as f:
            self.test_list = f.read().splitlines()
        if img_norm_cfg == None:
            self.img_norm_cfg = get_img_norm_cfg(dataset_name, dataset_dir)
        else:
            self.img_norm_cfg = img_norm_cfg

    def __getitem__(self, idx):
        try:
            img = Image.open((self.dataset_dir + '/images/' + self.test_list[idx] + '.png').replace('//', '/')).convert('I')
            mask = Image.open((self.dataset_dir + '/masks/' + self.test_list[idx] + '.png').replace('//', '/'))
        except:
            img = Image.open((self.dataset_dir + '/images/' + self.test_list[idx] + '.bmp').replace('//', '/')).convert('I')
            mask = Image.open((self.dataset_dir + '/masks/' + self.test_list[idx] + '.bmp').replace('//', '/'))
        img = Normalized(np.array(img, dtype=np.float32), self.img_norm_cfg)
        mask = np.array(mask, dtype=np.float32) / 255.0
        if len(mask.shape) > 2:
            mask = mask[:, :, 0]
        h, w = img.shape
        img = PadImg(img)
        mask = PadImg(mask)
        img, mask = img[np.newaxis, :], mask[np.newaxis, :]
        img = torch.from_numpy(np.ascontiguousarray(img))
        mask = torch.from_numpy(np.ascontiguousarray(mask))



        return img, mask, [h, w], self.test_list[idx]

    def __len__(self):
        return len(self.test_list)




class augumentation(object):
    def __call__(self, input, target):
        if random.random() < 0.5:  # 水平反转
            input = input[::-1, :]
            target = target[::-1, :]
        if random.random() < 0.5:  # 垂直反转
            input = input[:, ::-1]
            target = target[:, ::-1]
        if random.random() < 0.5:  # 转置反转
            input = input.transpose(1, 0)
            target = target.transpose(1, 0)
        return input, target







class TrainSetLoaderV3(torch.utils.data.Dataset):
    def __init__(self, dataset_dir, dataset_name, patch_size):
        super(TrainSetLoaderV3).__init__()
        self.dataset_name = dataset_name
        self.dataset_dir = dataset_dir + '/' + dataset_name
        self.patch_size = patch_size
        if not os.path.exists(self.dataset_dir +'/img_idx/train_' + dataset_name + '.txt') and os.path.exists(self.dataset_dir +'/img_idx/train.txt'):
            shutil.copyfile(self.dataset_dir +'/img_idx/train.txt', self.dataset_dir +'/img_idx/train_' + dataset_name + '.txt')
        with open(self.dataset_dir +'/img_idx/train_' + dataset_name + '.txt', 'r') as f:
            self.train_list = f.read().splitlines()

        with open(self.dataset_dir + '/img_idx/train_' + dataset_name + '.txt', 'r') as f:
            self.train_list = f.read().splitlines()

        # if img_norm_cfg == None:
        #     self.img_norm_cfg = get_img_norm_cfg(dataset_name, dataset_dir)
        # else:
        #     self.img_norm_cfg = img_norm_cfg

        self.tranform = augumentation()


    def __getitem__(self, idx):
        try:
            img = Image.open(
                (self.dataset_dir + '/images/' + self.train_list[idx] + '.png').replace('//', '/')).convert('I')
            mask = Image.open((self.dataset_dir + '/masks/' + self.train_list[idx] + '.png').replace('//', '/'))
        except:
            img = Image.open(
                (self.dataset_dir + '/images/' + self.train_list[idx] + '.bmp').replace('//', '/')).convert('I')
            mask = Image.open((self.dataset_dir + '/masks/' + self.train_list[idx] + '.bmp').replace('//', '/'))

        img = img.resize((self.patch_size, self.patch_size), Image.BILINEAR)
        mask = mask.resize((self.patch_size, self.patch_size), Image.NEAREST)

        # img = Normalized(np.array(img, dtype=np.float32), self.img_norm_cfg)
        img = np.array(img, dtype=np.float32) / 255.0
        mask = np.array(mask, dtype=np.float32) / 255.0
        if len(mask.shape) > 2:
            mask = mask[:, :, 0]

        # img_patch, mask_patch = random_crop(img, mask, self.patch_size, pos_prob=0.5)

        img_patch, mask_patch = self.tranform(img, mask)
        img_patch, mask_patch = img_patch[np.newaxis, :], mask_patch[np.newaxis, :]
        img_patch = torch.from_numpy(np.ascontiguousarray(img_patch))
        mask_patch = torch.from_numpy(np.ascontiguousarray(mask_patch))
        return img_patch, mask_patch

    def __len__(self):
        return len(self.train_list)



class TestSetLoaderV3(torch.utils.data.Dataset):
    def __init__(self, dataset_dir, dataset_name , patch_size):
        super(TestSetLoaderV3).__init__()
        self.patch_size = patch_size
        self.size = (int(self.patch_size), int(self.patch_size))
        # self.resize_transform = torchvision.transforms.Resize(self.size)  # 新的宽度和高度
        self.dataset_dir = dataset_dir + '/' + dataset_name
        with open(self.dataset_dir + '/img_idx/test_' + dataset_name + '.txt', 'r') as f:
            self.test_list = f.read().splitlines()
        # if img_norm_cfg == None:
        #     self.img_norm_cfg = get_img_norm_cfg(dataset_name, dataset_dir)
        # else:
        #     self.img_norm_cfg = img_norm_cfg


    def __len__(self):
        return len(self.test_list)

    def __getitem__(self, idx):
        try:
            img = Image.open((self.dataset_dir + '/images/' + self.test_list[idx] + '.png').replace('//', '/')).convert('I')
            mask = Image.open((self.dataset_dir + '/masks/' + self.test_list[idx] + '.png').replace('//', '/')).convert('L')
        except:
            img = Image.open((self.dataset_dir + '/images/' + self.test_list[idx] + '.bmp').replace('//', '/')).convert('I')
            mask = Image.open((self.dataset_dir + '/masks/' + self.test_list[idx] + '.bmp').replace('//', '/')).convert('L')

        img = img.resize((self.patch_size, self.patch_size), Image.BILINEAR)
        mask = mask.resize((self.patch_size, self.patch_size), Image.NEAREST)

        #
        # img = Normalized(np.array(img, dtype=np.float32), self.img_norm_cfg)
        img = np.array(img, dtype=np.float32) / 255.0
        mask = np.array(mask, dtype=np.float32) / 255.0
        if len(mask.shape) > 2:
            mask = mask[:,:,0]

        h, w = img.shape
        # img = PadImg(img)
        # mask = PadImg(mask)

        img, mask = img[np.newaxis, :], mask[np.newaxis, :]

        img = img.astype(np.float32)
        mask = mask.astype(np.float32)

        img = torch.from_numpy(np.ascontiguousarray(img))
        mask = torch.from_numpy(np.ascontiguousarray(mask))
        return img, mask,  [h, w], self.test_list[idx]



