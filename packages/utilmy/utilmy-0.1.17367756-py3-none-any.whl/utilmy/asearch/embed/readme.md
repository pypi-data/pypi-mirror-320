
#### Embeddding echo embedding

```


https://github.com/jakespringer/echo-embeddings



from echo_embeddings import EchoEmbeddingsMistral, EchoPooling, EchoParser

Generate embedding from gemma2 model

Your did before:
    take the last token


Echo embedding use another way to get embedding:

     you can do in Kaggle and notebook

     make the kaggle private.

     I will my kaggle account after.


Copy paste the coder here

https://github.com/jakespringer/echo-embeddings/blob/master/echo_embeddings.py



### Run some benchmark on MTEB (Japanese)

https://huggingface.co/datasets/sbintuitions/JMTEB

aske chatGPT for the coe,.






### GRIT Embedding

https://docs.google.com/presentation/d/1OkPWkeNt1-Mj2Lh7m01FNhmcs-dAn7f1XTJOL1gofIM/edit#slide=id.g16197112905_0_0







```













# Language-Model-STS-CFT finetune gemma-2-2b-jpn-it

- Resources:
    - Train: [llm-lm-sts-cft-finetuning.ipynb](llm-lm-sts-cft-finetuning.ipynb)
    - Eval: [llm-lm-sts-cft-eval.ipynb](llm-lm-sts-cft-eval.ipynb)
    - Infer: [llm-lm-sts-cft-infer.ipynb](llm-lm-sts-cft-infer.ipynb)
    - Dataset:
        - Build from [shunk031/jsnli](https://huggingface.co/datasets/shunk031/jsnli) following the approach in the paper
        - Script: [llm-jsnli-for-simcse.ipynb](llm-jsnli-for-simcse.ipynb)
        - Output: [https://www.kaggle.com/datasets/hahunavth/jsnli-for-simcse](https://www.kaggle.com/datasets/hahunavth/jsnli-for-simcse/settings)
    - Wandb: [https://wandb.ai/hahunavth/minicpm-dense-retrieval?nw=nwuserhahunavth](https://wandb.ai/hahunavth/minicpm-dense-retrieval?nw=nwuserhahunavth)
    - Checkpoints: [https://www.kaggle.com/datasets/hahunavth/llm-gemma-2-2b-jpn-it-finetune](https://www.kaggle.com/datasets/hahunavth/llm-gemma-2-2b-jpn-it-finetune/settings)

---
## Download train set
```bash
# jsnli-for-simcse/jsnli-for-simcse.csv
curl -L -o archive.zip https://www.kaggle.com/api/v1/datasets/download/hahunavth/jsnli-for-simcse
unzip archive.zip -d jsnli-for-simcse
rm archive.zip
```

## Evaluation results

## Before

- [https://www.kaggle.com/code/hahunavth/llm-lm-sts-cft-eval/output?scriptVersionId=205157869](https://www.kaggle.com/code/hahunavth/llm-lm-sts-cft-eval/output?scriptVersionId=205157869)

### STS

```json
// JSICK.json
{
  "dataset_revision": "e4af6c73182bebb41d94cb336846e5a452454ea7",
  "evaluation_time": 573.9168074131012,
  "kg_co2_emissions": null,
  "mteb_version": "1.18.8",
  "scores": {
    "test": [
      {
        "cosine_pearson": 0.4550543931596049,
        "cosine_spearman": 0.4957290274490716,
        "euclidean_pearson": 0.459242984610333,
        "euclidean_spearman": 0.4683170022477207,
        "hf_subset": "default",
        "languages": [
          "jpn-Jpan"
        ],
        "main_score": 0.4957290274490716,
        "manhattan_pearson": 0.5314646963178258,
        "manhattan_spearman": 0.5126982468847882,
        "pearson": 0.4550543931596049,
        "spearman": 0.4957290274490716
      }
    ]
  },
  "task_name": "JSICK"
}
```

```json
// JSTS.json
{
  "dataset_revision": "50e79c314a7603ebc92236b66a0973d51a00ed8c",
  "evaluation_time": 421.3893961906433,
  "kg_co2_emissions": null,
  "mteb_version": "1.18.9",
  "scores": {
    "validation": [
      {
        "cosine_pearson": 0.4860971540657163,
        "cosine_spearman": 0.5291011116381971,
        "euclidean_pearson": 0.40064737143402873,
        "euclidean_spearman": 0.43811912895253924,
        "hf_subset": "default",
        "languages": [
          "jpn-Jpan"
        ],
        "main_score": 0.5291011116381971,
        "manhattan_pearson": 0.592069742985967,
        "manhattan_spearman": 0.588222408391436,
        "pearson": 0.4860971540657163,
        "spearman": 0.5291011116381971
      }
    ]
  },
  "task_name": "JSTS"
}
```

## After finetune 500 step

- [https://www.kaggle.com/code/hahunavth/llm-lm-sts-cft-eval/output?scriptVersionId=205156738](https://www.kaggle.com/code/hahunavth/llm-lm-sts-cft-eval/output?scriptVersionId=205156738)

### STS

```json
// JSICK.json
{
  "dataset_revision": "e4af6c73182bebb41d94cb336846e5a452454ea7",
  "evaluation_time": 661.5448136329651,
  "kg_co2_emissions": null,
  "mteb_version": "1.18.8",
  "scores": {
    "test": [
      {
        "cosine_pearson": 0.7205766820120738,
        "cosine_spearman": 0.68986846553398,
        "euclidean_pearson": 0.7283792249399142,
        "euclidean_spearman": 0.6872592886559902,
        "hf_subset": "default",
        "languages": [
          "jpn-Jpan"
        ],
        "main_score": 0.68986846553398,
        "manhattan_pearson": 0.7316020349708938,
        "manhattan_spearman": 0.6905517935859593,
        "pearson": 0.7205766820120738,
        "spearman": 0.68986846553398
      }
    ]
  },
  "task_name": "JSICK"
}
```

```json
// JSTS.json
{
  "dataset_revision": "50e79c314a7603ebc92236b66a0973d51a00ed8c",
  "evaluation_time": 486.2406406402588,
  "kg_co2_emissions": null,
  "mteb_version": "1.18.6",
  "scores": {
    "validation": [
      {
        "cosine_pearson": 0.8573408182452251,
        "cosine_spearman": 0.819712282938052,
        "euclidean_pearson": 0.8618836234410696,
        "euclidean_spearman": 0.8215412984796615,
        "hf_subset": "default",
        "languages": [
          "jpn-Jpan"
        ],
        "main_score": 0.819712282938052,
        "manhattan_pearson": 0.8626249181685782,
        "manhattan_spearman": 0.8221035526794916,
        "pearson": 0.8573408182452251,
        "spearman": 0.819712282938052
      }
    ]
  },
  "task_name": "JSTS"
}
```

## 1000 step

- [https://www.kaggle.com/code/hahunavth/llm-lm-sts-cft-finetuning?scriptVersionId=205273527](https://www.kaggle.com/code/hahunavth/llm-lm-sts-cft-finetuning?scriptVersionId=205273527)

### STS

```json
// JSICK.json
{
  "dataset_revision": "e4af6c73182bebb41d94cb336846e5a452454ea7",
  "evaluation_time": 658.5403158664703,
  "kg_co2_emissions": null,
  "mteb_version": "1.18.9",
  "scores": {
    "test": [
      {
        "cosine_pearson": 0.7357637592152135,
        "cosine_spearman": 0.7053214175402621,
        "euclidean_pearson": 0.7440310614597485,
        "euclidean_spearman": 0.7039474989434563,
        "hf_subset": "default",
        "languages": [
          "jpn-Jpan"
        ],
        "main_score": 0.7053214175402621,
        "manhattan_pearson": 0.7465521028949238,
        "manhattan_spearman": 0.7068911757977828,
        "pearson": 0.7357637592152135,
        "spearman": 0.7053214175402621
      }
    ]
  },
  "task_name": "JSICK"
}
```

```json
// JSTS.json
{
  "dataset_revision": "50e79c314a7603ebc92236b66a0973d51a00ed8c",
  "evaluation_time": 485.02149987220764,
  "kg_co2_emissions": null,
  "mteb_version": "1.18.9",
  "scores": {
    "validation": [
      {
        "cosine_pearson": 0.8562721583813664,
        "cosine_spearman": 0.8190004060232174,
        "euclidean_pearson": 0.8603774661265796,
        "euclidean_spearman": 0.8177723845767197,
        "hf_subset": "default",
        "languages": [
          "jpn-Jpan"
        ],
        "main_score": 0.8190004060232174,
        "manhattan_pearson": 0.8608270700100589,
        "manhattan_spearman": 0.8181731276383554,
        "pearson": 0.8562721583813664,
        "spearman": 0.8190004060232174
      }
    ]
  },
  "task_name": "JSTS"
}
```

---

## Try evaluate author’s gemma-2b-it

## Before

[https://www.kaggle.com/code/hahunavth/llm-lm-sts-cft-eval?scriptVersionId=205158033](https://www.kaggle.com/code/hahunavth/llm-lm-sts-cft-eval?scriptVersionId=205158033)

```json
// STS12.json
{
  "dataset_revision": "a0d554a64d88156834ff5ae9920b964011b16384",
  "evaluation_time": 853.6547706127167,
  "kg_co2_emissions": null,
  "mteb_version": "1.18.6",
  "scores": {
    "test": [
      {
        "cosine_pearson": 0.4038037048822222,
        "cosine_spearman": 0.4376575225711096,
        "euclidean_pearson": 0.4213808888966663,
        "euclidean_spearman": 0.4439914415715377,
        "hf_subset": "default",
        "languages": [
          "eng-Latn"
        ],
        "main_score": 0.4376575225711096,
        "manhattan_pearson": 0.4315099673133428,
        "manhattan_spearman": 0.44887416765329174,
        "pearson": 0.4038037048822222,
        "spearman": 0.4376575225711096
      }
    ]
  },
  "task_name": "STS12"
}
```

## After

[https://www.kaggle.com/code/hahunavth/llm-lm-sts-cft-eval?scriptVersionId=205161268](https://www.kaggle.com/code/hahunavth/llm-lm-sts-cft-eval?scriptVersionId=205161268)

```json
// STS12.json
{
  "dataset_revision": "a0d554a64d88156834ff5ae9920b964011b16384",
  "evaluation_time": 934.233898639679,
  "kg_co2_emissions": null,
  "mteb_version": "1.18.6",
  "scores": {
    "test": [
      {
        "cosine_pearson": 0.8457361223677784,
        "cosine_spearman": 0.757068134190354,
        "euclidean_pearson": 0.8192566679017707,
        "euclidean_spearman": 0.7550940173365444,
        "hf_subset": "default",
        "languages": [
          "eng-Latn"
        ],
        "main_score": 0.757068134190354,
        "manhattan_pearson": 0.8141931021717521,
        "manhattan_spearman": 0.7514437125495047,
        "pearson": 0.8457361223677784,
        "spearman": 0.757068134190354
      }
    ]
  },
  "task_name": "STS12"
}
```
