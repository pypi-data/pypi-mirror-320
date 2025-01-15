import sys

class InfiniGramEngine:

    def __init__(self, index_dir, eos_token_id,
                 load_to_ram=False, ds_prefetch_depth=1, sa_prefetch_depth=3, od_prefetch_depth=3,
                 max_support=1000, max_clause_freq=50000, max_diff_tokens=100, maxnum=1, max_disp_len=1000,
                 dtype='u16',
                 ):

        assert sys.byteorder == 'little', 'This code is designed to run on little-endian machines only!'

        assert dtype in ['u16', 'u32']
        self.dtype = dtype
        if dtype == 'u16':
            self.token_id_max = 2**16 - 1
            from .cpp_engine import Engine
        elif dtype == 'u32':
            self.token_id_max = 2**32 - 1
            from .cpp_engine_u32 import Engine

        if type(index_dir) == str:
            index_dir = [index_dir]
        assert type(index_dir) == list and all(type(d) == str for d in index_dir)
        assert type(eos_token_id) == int and 0 <= eos_token_id and eos_token_id < self.token_id_max
        assert type(load_to_ram) == bool
        assert type(ds_prefetch_depth) == int and ds_prefetch_depth > 0
        assert type(sa_prefetch_depth) == int and sa_prefetch_depth > ds_prefetch_depth
        assert type(od_prefetch_depth) == int and od_prefetch_depth > 0
        assert type(max_support) == int and max_support > 0
        assert type(max_clause_freq) == int and max_clause_freq > 0
        assert type(max_diff_tokens) == int and max_diff_tokens > 0
        assert type(maxnum) == int and maxnum > 0
        assert type(max_disp_len) == int and max_disp_len > 0

        self.max_support = max_support
        self.max_clause_freq = max_clause_freq
        self.max_diff_tokens = max_diff_tokens
        self.maxnum = maxnum
        self.max_disp_len = max_disp_len

        self.engine = Engine(index_dir, eos_token_id, load_to_ram, ds_prefetch_depth, sa_prefetch_depth, od_prefetch_depth)

    def check_query_ids(self, query_ids, allow_empty):
        if not (type(query_ids) == list and (allow_empty or len(query_ids) > 0)):
            return False
        for q in query_ids:
            if not (type(q) == int and 0 <= q and q <= self.token_id_max):
                return False
        return True

    def check_cnf(self, cnf):
        if not (type(cnf) == list and len(cnf) > 0):
            return False
        for disj_clause in cnf:
            if not (type(disj_clause) == list and len(disj_clause) > 0):
                return False
            for query_ids in disj_clause:
                if not (type(query_ids) == list and len(query_ids) > 0):
                    return False
                for q in query_ids:
                    if not (type(q) == int and 0 <= q and q <= self.token_id_max):
                        return False
        return True

    def find(self, input_ids):
        if not self.check_query_ids(input_ids, allow_empty=True):
            return {'error': f'input_ids must be a list of integers in range [0, {self.token_id_max}]'}
        result = self.engine.find(input_ids=input_ids)
        return {'cnt': result.cnt, 'segment_by_shard': result.segment_by_shard}

    def find_cnf(self, cnf, max_clause_freq=None, max_diff_tokens=None):
        if max_clause_freq is None:
            max_clause_freq = self.max_clause_freq
        if max_diff_tokens is None:
            max_diff_tokens = self.max_diff_tokens
        if not (type(max_clause_freq) == int and max_clause_freq > 0):
            return {'error': 'max_clause_freq must be a positive integer'}
        if not (type(max_diff_tokens) == int and max_diff_tokens > 0):
            return {'error': 'max_diff_tokens must be a positive integer'}
        if not self.check_cnf(cnf):
            return {'error': f'cnf must be a non-empty, triply-nested list of integers in range [0, {self.token_id_max}]'}
        result = self.engine.find_cnf(cnf=cnf, max_clause_freq=max_clause_freq, max_diff_tokens=max_diff_tokens)
        return {'cnt': result.cnt, 'approx': result.approx, 'ptrs_by_shard': result.ptrs_by_shard}

    def count(self, input_ids):
        if not self.check_query_ids(input_ids, allow_empty=True):
            return {'error': f'input_ids must be a list of integers in range [0, {self.token_id_max}]'}
        result = self.engine.count(input_ids=input_ids)
        return {'count': result.count, 'approx': result.approx}

    def count_cnf(self, cnf, max_clause_freq=None, max_diff_tokens=None):
        if max_clause_freq is None:
            max_clause_freq = self.max_clause_freq
        if max_diff_tokens is None:
            max_diff_tokens = self.max_diff_tokens
        if not (type(max_clause_freq) == int and max_clause_freq > 0):
            return {'error': 'max_clause_freq must be a positive integer'}
        if not (type(max_diff_tokens) == int and max_diff_tokens > 0):
            return {'error': 'max_diff_tokens must be a positive integer'}
        if not self.check_cnf(cnf):
            return {'error': f'cnf must be a non-empty, triply-nested list of integers in range [0, {self.token_id_max}]'}
        result = self.engine.count_cnf(cnf=cnf, max_clause_freq=max_clause_freq, max_diff_tokens=max_diff_tokens)
        return {'count': result.count, 'approx': result.approx}

    def prob(self, prompt_ids, cont_id):
        if not self.check_query_ids(prompt_ids, allow_empty=True):
            return {'error': f'prompt_ids must be a non-empty list of integers in range [0, {self.token_id_max}]'}
        if not (type(cont_id) == int and 0 <= cont_id and cont_id <= self.token_id_max):
            return {'error': f'cont_id must be an integer in range [0, {self.token_id_max}]'}
        result = self.engine.prob(prompt_ids=prompt_ids, cont_id=cont_id)
        return {'prompt_cnt': result.prompt_cnt, 'cont_cnt': result.cont_cnt, 'prob': result.prob}

    def ntd(self, prompt_ids, max_support=None):
        if max_support is None:
            max_support = self.max_support
        if not (type(max_support) == int and max_support > 0):
            return {'error': 'max_support must be a positive integer'}
        if not self.check_query_ids(prompt_ids, allow_empty=True):
            return {'error': f'prompt_ids must be a list of integers in range [0, {self.token_id_max}]'}
        result = self.engine.ntd(prompt_ids=prompt_ids, max_support=max_support)
        result_by_token_id = {token_id: {'cont_cnt': r.cont_cnt, 'prob': r.prob} for token_id, r in result.result_by_token_id.items()}
        return {'prompt_cnt': result.prompt_cnt, 'result_by_token_id': result_by_token_id, 'approx': result.approx}

    def infgram_prob(self, prompt_ids, cont_id):
        if not self.check_query_ids(prompt_ids, allow_empty=True):
            return {'error': f'prompt_ids must be a non-empty list of integers in range [0, {self.token_id_max}]'}
        if not (type(cont_id) == int and 0 <= cont_id and cont_id <= self.token_id_max):
            return {'error': f'cont_id must be an integer in range [0, {self.token_id_max}]'}
        result = self.engine.infgram_prob(prompt_ids=prompt_ids, cont_id=cont_id)
        return {'prompt_cnt': result.prompt_cnt, 'cont_cnt': result.cont_cnt, 'prob': result.prob, 'suffix_len': result.suffix_len}

    def infgram_ntd(self, prompt_ids, max_support=None):
        if max_support is None:
            max_support = self.max_support
        if not (type(max_support) == int and max_support > 0):
            return {'error': 'max_support must be a positive integer'}
        if not self.check_query_ids(prompt_ids, allow_empty=True):
            return {'error': f'prompt_ids must be a list of integers in range [0, {self.token_id_max}]'}
        result = self.engine.infgram_ntd(prompt_ids=prompt_ids, max_support=max_support)
        result_by_token_id = {token_id: {'cont_cnt': r.cont_cnt, 'prob': r.prob} for token_id, r in result.result_by_token_id.items()}
        return {'prompt_cnt': result.prompt_cnt, 'result_by_token_id': result_by_token_id, 'approx': result.approx, 'suffix_len': result.suffix_len}

    def search_docs(self, input_ids, maxnum=None, max_disp_len=None):
        if maxnum is None:
            maxnum = self.maxnum
        if max_disp_len is None:
            max_disp_len = self.max_disp_len
        if not (type(maxnum) == int and maxnum > 0):
            return {'error': 'maxnum must be a positive integer'}
        if not (type(max_disp_len) == int and max_disp_len > 0):
            return {'error': 'max_disp_len must be a positive integer'}
        if not self.check_query_ids(input_ids, allow_empty=True):
            return {'error': f'input_ids must be a list of integers in range [0, {self.token_id_max}]'}

        result = self.engine.search_docs(input_ids=input_ids, maxnum=maxnum, max_disp_len=max_disp_len)

        documents = [{'doc_ix': d.doc_ix, 'doc_len': d.doc_len, 'disp_len': d.disp_len, 'metadata': d.metadata, 'token_ids': d.token_ids} for d in result.docs]
        return {'cnt': result.cnt, 'approx': result.approx, 'idxs': result.idxs, 'documents': documents}

    def search_docs_cnf(self, cnf, maxnum=None, max_disp_len=None, max_clause_freq=None, max_diff_tokens=None):
        if maxnum is None:
            maxnum = self.maxnum
        if max_disp_len is None:
            max_disp_len = self.max_disp_len
        if max_clause_freq is None:
            max_clause_freq = self.max_clause_freq
        if max_diff_tokens is None:
            max_diff_tokens = self.max_diff_tokens
        if not (type(maxnum) == int and maxnum > 0):
            return {'error': 'maxnum must be a positive integer'}
        if not (type(max_disp_len) == int and max_disp_len > 0):
            return {'error': 'max_disp_len must be a positive integer'}
        if not (type(max_clause_freq) == int and max_clause_freq > 0):
            return {'error': 'max_clause_freq must be a positive integer'}
        if not (type(max_diff_tokens) == int and max_diff_tokens > 0):
            return {'error': 'max_diff_tokens must be a positive integer'}
        if not self.check_cnf(cnf):
            return {'error': f'cnf must be a non-empty, triply-nested list of integers in range [0, {self.token_id_max}]'}

        result = self.engine.search_docs_cnf(cnf=cnf, maxnum=maxnum, max_disp_len=max_disp_len, max_clause_freq=max_clause_freq, max_diff_tokens=max_diff_tokens)

        documents = [{'doc_ix': d.doc_ix, 'doc_len': d.doc_len, 'disp_len': d.disp_len, 'metadata': d.metadata, 'token_ids': d.token_ids} for d in result.docs]
        return {'cnt': result.cnt, 'approx': result.approx, 'idxs': result.idxs, 'documents': documents}

    def get_doc_by_rank(self, s, rank, max_disp_len=None):
        if max_disp_len is None:
            max_disp_len = self.max_disp_len
        if not (type(max_disp_len) == int and max_disp_len > 0):
            return {'error': 'max_disp_len must be a positive integer'}
        num_shards = self.engine.get_num_shards()
        if not (type(s) == int and 0 <= s and s < num_shards):
            return {'error': f's must be an integer in range [0, {num_shards})'}
        tok_cnt = self.engine.get_tok_cnt(s=s)
        if not (type(rank) == int and 0 <= rank and rank < tok_cnt):
            return {'error': f'ptr must be an integer in range [0, {tok_cnt})'}

        result = self.engine.get_doc_by_rank(s=s, rank=rank, max_disp_len=max_disp_len)
        return {'doc_ix': result.doc_ix, 'doc_len': result.doc_len, 'disp_len': result.disp_len, 'metadata': result.metadata, 'token_ids': result.token_ids}

    def get_doc_by_ptr(self, s, ptr, max_disp_len=None):
        if max_disp_len is None:
            max_disp_len = self.max_disp_len
        if not (type(max_disp_len) == int and max_disp_len > 0):
            return {'error': 'max_disp_len must be a positive integer'}
        num_shards = self.engine.get_num_shards()
        if not (type(s) == int and 0 <= s and s < num_shards):
            return {'error': f's must be an integer in range [0, {num_shards})'}
        ds_size = self.engine.get_ds_size(s=s)
        if not (type(ptr) == int and 0 <= ptr and ptr < ds_size and ptr % 2 == 0):
            return {'error': f'ptr must be an even integer in range [0, {ds_size})'}

        result = self.engine.get_doc_by_ptr(s=s, ptr=ptr, max_disp_len=max_disp_len)
        return {'doc_ix': result.doc_ix, 'doc_len': result.doc_len, 'disp_len': result.disp_len, 'metadata': result.metadata, 'token_ids': result.token_ids}

    def get_doc_by_ix(self, doc_ix, max_disp_len=None):
        if max_disp_len is None:
            max_disp_len = self.max_disp_len
        if not (type(max_disp_len) == int and max_disp_len > 0):
            return {'error': 'max_disp_len must be a positive integer'}
        total_doc_cnt = self.engine.get_total_doc_cnt()
        if not (type(doc_ix) == int and 0 <= doc_ix and doc_ix < total_doc_cnt):
            return {'error': f'doc_ix must be an integer in range [0, {total_doc_cnt})'}

        result = self.engine.get_doc_by_ix(doc_ix=doc_ix, max_disp_len=max_disp_len)
        return {'doc_ix': result.doc_ix, 'doc_len': result.doc_len, 'disp_len': result.disp_len, 'metadata': result.metadata, 'token_ids': result.token_ids}

    def get_total_doc_cnt(self):
        return self.engine.get_total_doc_cnt()
