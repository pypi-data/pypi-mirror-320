# Copyright 2024 Mario Graff (https://github.com/mgraffg)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import argparse
from itertools import count
from urllib import request
from urllib.error import HTTPError
try:
    USE_TQDM = True
    from tqdm import tqdm
except ImportError:
    USE_TQDM = False
from microtc.utils import tweet_iterator, Counter
from microtc import emoticons
from b4msa import TextModel
import numpy as np
import gzip
import json
import os
import encexp


DialectID_URL = 'https://github.com/INGEOTEC/dialectid/releases/download/data'
EncExp_URL = 'https://github.com/INGEOTEC/EncExp/releases/download/data'
MODELS = os.path.join(os.path.dirname(__file__),
                      'models')

class Download(object):
    """Download
    
    >>> from EncExp.utils import Download
    >>> d = Download("http://github.com", "t.html")
    """

    def __init__(self, url, output='t.tmp') -> None:
        self._url = url
        self._output = output
        self._use_tqdm = USE_TQDM
        try:
            request.urlretrieve(url, output, reporthook=self.progress)
        except HTTPError as exc:
            self._use_tqdm = False
            self.close()
            raise RuntimeError(f'URL=> {url}') from exc
        self.close()

    @property
    def tqdm(self):
        """tqdm"""

        if not self._use_tqdm:
            return None
        try:
            return self._tqdm
        except AttributeError:
            self._tqdm = tqdm(total=self._nblocks,
                              leave=False, desc=self._output)
        return self._tqdm

    def close(self):
        """Close tqdm if used"""
        if self._use_tqdm:
            self.tqdm.close()

    def update(self):
        """Update tqdm if used"""
        if self._use_tqdm:
            self.tqdm.update()

    def progress(self, nblocks, block_size, total):
        """tqdm progress"""

        self._nblocks = total // block_size
        self.update()


def b4msa_params(lang='es'):
    """B4MSA default parameters"""

    from microtc.params import OPTION_DELETE, OPTION_NONE
    tm_kwargs=dict(num_option=OPTION_NONE,
                   usr_option=OPTION_DELETE,
                   url_option=OPTION_DELETE,
                   emo_option=OPTION_NONE,
                   hashtag_option=OPTION_NONE,
                   ent_option=OPTION_NONE,
                   lc=True,
                   del_dup=False,
                   del_punc=True,
                   del_diac=True,
                   select_ent=False,
                   select_suff=False,
                   select_conn=False,
                   max_dimension=False,
                   unit_vector=True,
                   q_grams_words=True,
                   norm_emojis=True)
    if lang == 'ja' or lang == 'zh':
        tm_kwargs['token_list'] = [1, 2, 3]
    else:
        tm_kwargs['token_list'] = [-1, 2, 3, 4, 5, 6, 7, 8]
    return tm_kwargs


def progress_bar(data, total=np.inf,
                 use_tqdm: bool=True,
                 **kwargs):
    """Progress bar"""

    if not USE_TQDM or not use_tqdm:
        return data
    if total == np.inf:
        total = None
    return tqdm(data, total=total, **kwargs)


def compute_b4msa_vocabulary(filename, limit=None, lang='es',
                             **kwargs):
    """Compute the vocabulary"""

    params = b4msa_params(lang=lang)
    params.update(kwargs)
    tokenize = replace_tokens(TextModel(**params)).tokenize
    if limit is None:
        limit = np.inf
    counter = Counter()
    if limit == np.inf:
        loop = count()
    else:
        loop = range(limit)
    for tweet, _ in progress_bar(zip(tweet_iterator(filename),
                                        loop), total=limit,
                                        desc=filename):
        counter.update(set(tokenize(tweet)))
    _ = dict(update_calls=counter.update_calls,
             dict=dict(counter.most_common()))
    data = dict(counter=_, params=params)
    return data


def compute_seqtm_vocabulary(instance, vocabulary,
                             filename, limit=None,
                             voc_size_exponent=13,
                             prefix_suffix=False):
    """Compute SeqTM"""

    def current_lost_words():
        words = [w for w, _ in base_voc.most_common() if w[:2] != 'q:']
        current = words[:2**voc_size_exponent]
        lost =  words[2**voc_size_exponent:]
        return current, lost

    def tokenizer(length, current):
        length += 2
        cnt = Counter()
        for k, v in base_voc.items():
            if k[:2] != 'q:' or len(k) != length:
                continue
            if prefix_suffix and length < 6 and k[3] != '~' and k[-1] != '~':
                continue
            cnt[k] = v
        for token in current:
            freq = base_voc[token]
            if freq == 0:
                continue
            cnt[token] = freq
        cnt.update_calls = base_voc.update_calls
        _ = dict(params=vocabulary['params'], counter=cnt)
        return instance(vocabulary=_).tokenize

    def optimize_vocabulary():
        words = [token for token in base_voc if token[:2] != 'q:']
        current, _ = current_lost_words()
        lengths = sorted([length
                          for length in vocabulary['params']['token_list']
                          if length > 0], reverse=True)
        for length in progress_bar(lengths, desc='qgrams'):
            tokenize = tokenizer(length, current)
            cnt = Counter()
            vacia = set(['~'])
            for word in words:
                tokens = set(tokenize(word)) - vacia
                _ = {token: base_voc[word] for token in tokens}
                cnt.update(_)
            current = [k for k, v in cnt.most_common(n=2**voc_size_exponent)]
        return cnt.most_common(n=2**voc_size_exponent)

    limit = np.inf if limit is None else limit
    loop = count() if limit == np.inf else range(limit)
    base_voc = Counter(vocabulary['counter']["dict"],
                       vocabulary['counter']["update_calls"])
    voc = optimize_vocabulary()
    cnt = Counter(dict(voc),
                  update_calls=base_voc.update_calls)
    _ = dict(params=vocabulary['params'], counter=cnt)
    tokenize = instance(vocabulary=_).tokenize
    counter = Counter()
    for tweet, _ in progress_bar(zip(tweet_iterator(filename),
                                        loop), total=limit,
                                        desc=filename):
        counter.update(set(tokenize(tweet)))
    _ = dict(update_calls=counter.update_calls,
             dict=dict(counter.most_common()[:2**voc_size_exponent]))
    data = dict(counter=_, params=vocabulary['params'])
    return data


def uniform_sample(N, avail_data):
    """Uniform sample from the available data"""
    remaining = avail_data.copy()
    M = 0
    while M < N:
        index = np.where(remaining > 0)[0]
        if index.shape[0] == 0:
            break
        sample = np.random.randint(index.shape[0], size=N - M)
        sample_i, sample_cnt = np.unique(index[sample], return_counts=True)
        remaining[sample_i] = remaining[sample_i] - sample_cnt
        remaining[remaining < 0] = 0
        M = (avail_data - remaining).sum()
    return avail_data - remaining


def unit_length(data):
    """Convert EncExp weights to have unit length"""
    if data.dtype == np.float16:
        data = data.astype(np.float32)
    w = np.linalg.norm(data, axis=0)
    w[w == 0] = 1
    return data / w


def set_to_zero(data, percentage: float=0.95):
    """Set elements to zero"""
    if percentage == 1:
        data[data < 0] = 0
        return data
    ss = np.argsort(data, axis=0)[::-1]
    tot = data.sum(axis=0)
    tot[tot == 0] = 1
    cum = np.cumsum(np.take_along_axis(data / tot,
                                       ss, axis=0), axis=0)
    a, b = np.where(np.diff(cum <= percentage,
                            axis=0))
    a += 1
    _ = b.argsort()
    a, b = a[_], b[_]
    values = data[ss[a, b], b]
    if values.shape[0] != data.shape[0]:
        a_n = np.zeros(data.shape[0], dtype=values.dtype)
        a_n[b] = values
        values = a_n
    data[data < values] = 0
    return data


def replace_tokens(tm):
    """Replace tokens on TextModel"""
    tm.norm_tokens = emoticons.read_emojis()
    _ = {f'~{jaja}~': '~ja~' for jaja in ['jaja', 'jajaj', 'jajaja', 'jajajaj',
                                          'jajajaja', 'jajajajaj', 'jajajajaja',
                                          'jajajajajaja', 'jajajajajajaja',
                                          'jajajajajajajaja', 'ajaj', 'ajaja',
                                          'ajajajaj', 'aja', 'jaa', 'jaj', 'jajja']}
    tm.norm_tokens.update(_)
    _ = {f'~{haha}~': '~ha~' for haha in ['haha', 'hahaha', 'hahahaha']}
    tm.norm_tokens.update(_)
    _ = {x: True for x in tm.norm_tokens}
    tm.norm_head = emoticons.create_data_structure(_)
    return tm


def transform_from_tokens(enc):
    """Transform from token list"""

    def dense(text):
        token2id = enc.bow.token2id
        seq = []
        for token in text:
            try:
                seq.append(token2id[token])
            except KeyError:
                continue
        W = enc.weights
        if len(seq) == 0:
            x = np.ones(W.shape[0], dtype=W.dtype)
        else:
            x = W[:, seq].sum(axis=1)
        return x

    def inner(texts):
        X = np.r_[[dense(text) for text in texts]]
        _norm = np.linalg.norm(X, axis=1)
        _norm[_norm == 0] = 1
        return X / np.c_[_norm]

    return inner
