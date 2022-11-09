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
