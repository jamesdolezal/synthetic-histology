# histologic-sheep

## Requirements
- Python >= 3.8
- Slideflow == 1.3.1
- Tensorflow >= 2.7.0
- PyTorch >= 1.10.0

Please refer to our [installation instructions](https://slideflow.dev/installation.html) for a guide to installing Slideflow and its prerequisites.

## Installation

🚧 Under construction 🚧

## Pretrained models

We offer three pretrained classifiers and three pretrained cGAN models:

- **lung-adeno-squam-classifier-v1**: Binary classification model with Xception backbone trained to predict lung adenocarcinoma (=0) vs. squamous cell carcinoma (=1).
- **lung-adeno-squam-gan-v1**: Conditional GAN (StyleGAN2) conditioned on lung adenocarcinoma (=0) vs. squamous cell carcinoma (=1).
- **breast-er-classifier-v1**: Binary classification model with Xception backbone trained to predict breast estrogen receptor (ER) negative (=0) vs. ER-positive (=1), with ER status determined through immunohistochemical (IHC) testing.
- **breast-er-gan-v1**: Conditional GAN (StyleGAN2) conditioned on breast ER-negative (=0) vs. ER-positive (=1).
- **thyroid-brs-classifier-v1**: Regression model with Xception backbone trained to predict thyroid BRAF-RAS gene expression score (score from -1 to +1, where -1=BRAF-like and +1=RAS-like)
- **thyroid-brs-gan-v1**: Conditional GAN (StyleGAN2) conditioned on thyroid BRAF-like (BRS < 0) vs. RAS-like (BRS > 0)

The easiest way to interface with the pretrained models is by using [Workbench](https://slideflow.dev/workbench_tools.html).


```
python3 workbench.py
```

Load GAN and/or classifier models via drag-and-drop, or with File -> Load GAN or File -> Load Model. See [our guide](https://slideflow.dev/workbench_tools.html#stylegan) for more information.

## Training models

We also provide configuration files that can be used to reproduce training of GANs and classifiers. Configuration files are available in ``./experiment/``.

To train a model with a given configuration, use the ``train_classifier.py`` and ``train_gan.py`` scripts.

```
python3 train_gan.py \
    --exp=experiment/thyroid/thyroid_brs_gan.json
    --download
    --md5
```

Whole-slide images will be automatically downloaded from TCGA if the ``--download`` flag is provided. File integrity will be verified via MD5 hash is the ``--md5`` flag is provided.

By default, a project folder will be created in the current working directory containing extracted tiles and saved models. This path can be overwritten with the ``--outdir`` argument. In a given project directory, classifier models will be saved in the ``./models/`` subfolder, and GAN networks will be saved in ``./gan/``.