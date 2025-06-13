config = {
    # flickr
    "image_root": '/home/chris/Desktop/VLM/datasets/flickr30k/images',
    "caption_file": '/home/chris/Desktop/VLM/datasets/flickr30k/captions.csv',
    "train_dataset_name": "flickr30k",
    "valid_image_root": '/home/chris/Desktop/VLM/datasets/flickr8k/images',
    "valid_caption_file": '/home/chris/Desktop/VLM/datasets/flickr8k/captions.csv',

    # newsDataset
    # "image_root": '/home/chris/Desktop/VLM/datasets/newsDataset/images',
    # "caption_file": '/home/chris/Desktop/VLM/datasets/newsDataset/train_fixed.csv',
    # "train_dataset_name": "flickr30k",
    # "valid_image_root": '/home/chris/Desktop/VLM/datasets/newsDataset/images',
    # "valid_caption_file": '/home/chris/Desktop/VLM/datasets/newsDataset/test_fixed.csv',
    
    # coco
    # "image_root": '/home/chris/Desktop/VLM/datasets/coco_train/images',
    # "caption_file": '/home/chris/Desktop/VLM/datasets/coco_train/train.csv',
    # "train_dataset_name": "coco",
    # "valid_image_root": '/home/chris/Desktop/VLM/datasets/coco_train/images',
    # "valid_caption_file": '/home/chris/Desktop/VLM/datasets/coco_train/test.csv',

    "image_size": 128,

    # 模型
    # "pretrained": False,
    "pretrained": 'https://storage.googleapis.com/sfr-vision-language-research/BLIP/models/model_base_capfilt_large.pth',
    "vit": 'base',
    "vit_grad_ckpt": False,
    "vit_ckpt_layer": 0,
    "prompt": "",

    # 優化器
    "init_lr": 1e-5,
    # "weight_decay": 0.05,
    "weight_decay": 1e-3,

    # 訓練
    "max_epoch": 20,
    "min_lr": 0,
    "batch_size": 50,

    # 存檔
    "recordPath": "/home/chris/Desktop/VLM/BlipV1/record"
}