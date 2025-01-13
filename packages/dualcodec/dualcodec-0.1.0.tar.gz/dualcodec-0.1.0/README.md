# DualCodec
## Installation
```bash
pip install dualcodec
```
## How to inference

Download checkpoints to local: 
```
# export HF_ENDPOINT=https://hf-mirror.com if you're in China
huggingface-cli download facebook/w2v-bert-2.0 --local-dir w2v-bert-2.0
huggingface-cli download amphion/dualcodec --local-dir dualcodec_ckpts
```

To inference an audio: 
```python

```

See "example.ipynb" for example inference scripts.
