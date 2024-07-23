from math import ceil
from typing import Generator, List, Union

import numpy as np
import torch
from oneliner_utils import read_jsonl
from torch import Tensor, einsum
from torch.nn.functional import normalize
from tqdm import tqdm
from transformers import AutoConfig, AutoModel, AutoTokenizer

from ..paths import embeddings_folder_path, encoder_state_path

pbar_kwargs = dict(position=0, dynamic_ncols=True, mininterval=1.0)


def count_lines(path: str):
    """Counts the number of lines in a file."""
    return sum(1 for _ in open(path))


def generate_batch(docs: Union[List, Generator], batch_size: int) -> Generator:
    texts = []

    for doc in docs:
        texts.append(doc["text"])

        if len(texts) == batch_size:
            yield texts
            texts = []

    if texts:
        yield texts


class Encoder:
    def __init__(
        self,
        index_name: str = "new-index",
        model: str = "../../local_model",
        normalize: bool = True,
        return_numpy: bool = True,
        max_length: int = 128,
        device: str = "cpu",
    ):
        self.index_name = index_name
        self.model = model
        # BERT tokenizer: input text into a sequence of tokens (numerical representations of words or subwords)
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        # SBERT encoder:
        # 1. compute three embedding: Token Embeddings, Segment Embeddings, Position Embeddings
        # 2. Passed through several layers of transformer encoders. Each encoder consists of a self-attention mechanism and a feed-forward neural network.
        # Pooling the output of transformer encoders to get a single vector representation for the sentence
        self.encoder = AutoModel.from_pretrained(model).to(device).eval()
        self.embedding_dim = AutoConfig.from_pretrained(model).hidden_size
        self.max_length = max_length
        self.normalize = normalize
        self.return_numpy = return_numpy
        self.device = device
        self.tokenizer_kwargs = {
            "padding": True,
            "truncation": True,
            "max_length": self.max_length,
            "return_tensors": "pt",
        }

    def save(self):
        state = dict(
            index_name=self.index_name,
            model=self.model,
            normalize=self.normalize,
            return_numpy=self.return_numpy,
            max_length=self.max_length,
            device=self.device,
        )
        np.save(encoder_state_path(self.index_name), state)

    @staticmethod
    def load(index_name: str, device: str = None):
        state = np.load(encoder_state_path(index_name), allow_pickle=True)[()]
        if device is not None:
            state["device"] = device
        return Encoder(**state)

    def change_device(self, device: str = "cpu"):
        self.device = device
        self.encoder.to(device)

    def tokenize(self, texts: List[str]):
        tokens = self.tokenizer(texts, **self.tokenizer_kwargs)
        return {k: v.to(self.device) for k, v in tokens.items()}

    def mean_pooling(self, embeddings: Tensor, mask: Tensor) -> Tensor:
        numerators = einsum("xyz,xy->xyz", embeddings, mask).sum(dim=1)
        denominators = torch.clamp(mask.sum(dim=1), min=1e-9)
        return einsum("xz,x->xz", numerators, 1 / denominators)

    def __call__(
        self,
        x: Union[str, List[str]],
        batch_size: int = 32,
        show_progress: bool = True,
    ):
        if isinstance(x, str):
            return self.encode(x)
        else:
            return self.bencode(x, batch_size=batch_size, show_progress=show_progress)

    def encode(self, text: str):
        return self.bencode([text], batch_size=1, show_progress=False)[0]

    def bencode(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = True,
    ):
        embeddings = []

        pbar = tqdm(
            total=len(texts),
            desc="Generating embeddings",
            disable=not show_progress,
            **pbar_kwargs,
        )
        # process sentences in batches
        for i in range(ceil(len(texts) / batch_size)):
            start, stop = i * batch_size, (i + 1) * batch_size
            # Tokenize current sentences/documents batch
            tokens = self.tokenize(texts[start:stop])

            with torch.no_grad():
                # Encode: compute embedding, pass through SBERT to get output embedding
                # emb = self.encoder(**tokens).last_hidden_state is generating embeddings for a batch of documents. 
                # The last_hidden_state is a tensor of shape (batch_size=#docs, doc_length, hidden_size), 
                # doc_length is maximum number of tokens in any document in the batch.
                # and hidden_size is the dimension of the BERT embeddings vector.

                # E.g. ['doc1', 'doc2', 'doc3'] -> BERT-tokenizer -> [(#token*vecotr dim)], no matter the doc text is a single sentence or multiple sentences, it tokenize the same way.
                # Tokenization detail: 
                # Split into sentences
                # 1. Tokenize into words: ['This', 'is', 'a', 'sentence']
                # 2. If the word is not within its vocabulary, use 'WordPiece', e.g. embeddins-> [“em”, “##bed”, “##ding”, “##s”], ## indicate it is a subword from a larger word
                # 3. It adds special tokens like [CLS] at the beginning and [SEP] at the end of each sentence to distinguish sentences
                # 4. Convert each token into an ID(n-dim vector) predefined in BERT vocabulary (n = 768)
                emb = self.encoder(**tokens).last_hidden_state
                # Pooling to generate vector representation of sentence(s)
                # reduces the doc_length dimension by taking the mean across all tokens in each sentence, 
                # resulting in a tensor of shape (batch_size, hidden_size). 
                # emb at this point contains one vector embedding for each document in the batch.
                # takes the mean of the token-level vectors in emb, but ignores the vectors for padding tokens. The tokens["attention_mask"]
                emb = self.mean_pooling(emb, tokens["attention_mask"])
                if self.normalize:
                    emb = normalize(emb, dim=-1)
            # sentences embedding for each batch
            # [[batch1_emb], [batch2_emb], ..]
            embeddings.append(emb)

            pbar.update(stop - start)
        pbar.close()

        # concat all all sentences embeddings into a single embedding
        # Or, one sentence embedding to one sentence embedding
        # [[batch1_emb], [batch2_emb], ..] -> [all_batch_embs]
        embeddings = torch.cat(embeddings)

        if self.return_numpy:
            embeddings = embeddings.detach().cpu().numpy()

        return embeddings

    def encode_collection(
        self,
        path: str,
        batch_size: int = 512,
        callback: callable = None,
        show_progress: bool = True,
    ):
        n_docs = count_lines(path)
        collection = read_jsonl(path, callback=callback, generator=True)

        # a large np array to hold embedding
        reservoir = np.empty((1_000_000, self.embedding_dim), dtype=np.float32)
        reservoir_n = 0
        offset = 0

        pbar = tqdm(
            total=n_docs,
            desc="Embedding documents",
            disable=not show_progress,
            **pbar_kwargs,
        )
        # texts = [doc1_text, doc2_text, ...], list_length = batch_size
        for texts in generate_batch(collection, batch_size):
            # Compute embeddings -----------------------------------------------
            embeddings = self.bencode(texts, batch_size=len(texts), show_progress=False)

            # Compute new offset -----------------------------------------------
            new_offset = offset + len(embeddings)

            # if reservoir is full, save to disck and initialize a new one
            if new_offset >= len(reservoir):
                np.save(
                    embeddings_folder_path(self.index_name)
                    / f"chunk_{reservoir_n}.npy",
                    reservoir[:offset],
                )
                reservoir = np.empty((1_000_000, self.embedding_dim), dtype=np.float32)
                reservoir_n += 1
                offset = 0
                new_offset = len(embeddings)

            # Save embeddings in the reservoir ---------------------------------
            reservoir[offset:new_offset] = embeddings

            # Update offeset ---------------------------------------------------
            offset = new_offset

            pbar.update(len(embeddings))

        if offset < len(reservoir):
            np.save(
                embeddings_folder_path(self.index_name) / f"chunk_{reservoir_n}.npy",
                reservoir[:offset],
            )
            reservoir = []

        assert len(reservoir) == 0, "Reservoir is not empty."
