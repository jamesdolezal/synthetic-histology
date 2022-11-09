# histologic-sheep

## Requirements
- Python >= 3.8
- Slideflow == 1.3.1
- Tensorflow >= 2.7.0
- PyTorch >= 1.10.0

Please refer to our [installation instructions](https://slideflow.dev/installation.html) for a guide to installing Slideflow and its prerequisites.

## Installation

If you plan to train models from scratch, [Openslide](https://openslide.org/download/) and [Libvips](https://libvips.github.io/libvips/) version 8.9 - 8.12 must first be installed. These are not required if you plan to only use pretrained models.

Finally, install the required dependencies using anaconda:

```
conda env create -f environment.yml
```

## Pretrained Models

We offer three pretrained classifiers and three pretrained cGAN models:

- **[lung-adeno-squam-v1](https://huggingface.co/jamesdolezal/lung-adeno-squam-v1)**: Binary classification model with Xception backbone trained to predict lung adenocarcinoma (=0) vs. squamous cell carcinoma (=1).
- **[lung-adeno-squam-gan-v1](https://huggingface.co/jamesdolezal/lung-adeno-squam-gan-v1)**: Conditional GAN (StyleGAN2) conditioned on lung adenocarcinoma (=0) vs. squamous cell carcinoma (=1).
- **[breast-er-v1](https://huggingface.co/jamesdolezal/breast-er-v1)**: Binary classification model with Xception backbone trained to predict breast estrogen receptor (ER) negative (=0) vs. ER-positive (=1), with ER status determined through immunohistochemical (IHC) testing.
- **[breast-er-gan-v1](https://huggingface.co/jamesdolezal/breast-er-gan-v1)**: Conditional GAN (StyleGAN2) conditioned on breast ER-negative (=0) vs. ER-positive (=1).
- **[thyroid-brs-v1](https://huggingface.co/jamesdolezal/thyroid-brs-v1)**: Regression model with Xception backbone trained to predict thyroid BRAF-RAS gene expression score (score from -1 to +1, where -1=BRAF-like and +1=RAS-like).
- **[thyroid-brs-gan-v1](https://huggingface.co/jamesdolezal/thyroid-brs-gan-v1)**: Conditional GAN (StyleGAN2) conditioned on thyroid BRAF-like (BRS < 0) vs. RAS-like (BRS > 0)

The easiest way to interface with the pretrained models is by using [Workbench](https://slideflow.dev/workbench_tools.html).


```
python3 workbench.py
```

Load GAN and/or classifier models via drag-and-drop, or with File -> Load GAN or File -> Load Model. See [our guide](https://slideflow.dev/workbench_tools.html#stylegan) for more information.

## Training Models

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

## Generating Images

Generate images from a trained network pickle by using ``generate.py``. For example, to generate BRAF-like (class=0) images from the pretrained Thyroid GAN for seeds 0-100, saving results as PNG images:

```
python3 generate.py
    --network=thyroid-brs-gan-v1.pkl
    --seeds=0-100
    --class=0
    --outdir=/some/path
    --format=png
```

Additional options can be seen by running ``generate.py --help``.

## Assessing Classifier Concordance

Classifier concordance can be assessed with ``concordance.py``. For example, to assess classifier concordance for seeds 0-1000 using the Thyroid model:

```
python3 concordance.py
    --network=thyroid-brs-gan-v1.pkl
    --classifier=/path/to/thyroid-brs-v1
    --out=/some/path/results.csv
    --outcome_idx=0
    --thresh_low=-0.5
    --thresh_mid=0
    --thresh_high=0.5
    --seeds=0-1000
```

Additional options can be seen by running ``concordance.py --help``.

## Generating Class-Blended Images

Class blending can be performed with ``interpolate.py``, creating side-by-side images during interpolation, saving images separately, or merging into a video. For example, to create a video interpolation for seed=0 using the Thyroid GAN:

```
python3 interpolate.py
    --network=thyroid-brs-gan-v1.pkl
    --seeds=0
    --outdir=/some/path
    --video=True
    --steps=100
```

Additional options can be seen by running ``interpolate.py --help``.

## Assessing Interpolation Probability

To assess interpolation probability for a range of seeds and save results as a figure, use ``interpolation_probability.py``. For example:

```
python3 interpolation_probability.py
    --network=thyroid-brs-gan-v1.pkl
    --classifier=/path/to/thyroid-brs-v1
    --outcome_idx=0
    --thresh_low=-0.5
    --thresh_mid=0
    --thresh_high=0.5
    --seeds=0-1000
    --out=probability.png
```
## License

This code is made available under the GPLv3 License and is available for non-commercial academic purposes.

## Reference

If you find our work useful for your research, or if you use parts of this code, please consider citing as follow:

🚧 Under construction 🚧
