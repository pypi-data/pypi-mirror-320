---
license: mit
language:
- en
pipeline_tag: audio-to-audio
---
# AudioZEN

## Prerequisites

```bash
# Install uv for speed up virtual environment creation and management
uv venv -p 3.12 venv/torch251_cu124_py312
source venv/torch251_cu124_py312/bin/activate

# Install the package
uv pip install -e .

# cd to the model directory
uv pip install -r /path/to/requirements.txt
```

## Features

- [x] Gradient accumulation
- [x] Multi-node training
- [x] BF16 support
- [x] Learning rate warmup
- [x] Learning rate decay
  - [x] Linear decay

## Prerequisites

```shell
rsync -avPxH --no-g --chmod=Dg+ /home/xhao/proj/audiozen xhao@10.21.4.91:/home/xhao/proj/audiozen --exclude="*.git" --exclude="*.egg-info" --exclude="*.egg" --exclude="*.pyc" --exclude="*.log" --exclude="*.npy"
```

- How to split the repo into read-only standalone repos? Check out [Monorepo-Management](https://github.com/haoxiangsnr/audiozen/wiki/Monorepo-Management)

## Git LFS

If files are too large and/or change frequently, consider using [Git LFS](https://git-lfs.github.com/).

```shell
git lfs install
git lfs track "*..."
git add .gitattributes
```

For ipynb files, we donnot need to track them as they are not large files and they are not changed frequently.