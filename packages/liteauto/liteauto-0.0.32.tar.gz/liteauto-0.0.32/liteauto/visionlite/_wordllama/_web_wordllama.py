from ._main import wlsplit,wltopk
from ...searchlite import web
def web_wordllama(query: str, k: int = 1, wk: int = 1, return_chunks=False):
    __chunks = wlsplit(web(query, k=wk))
    answer_chunks = wltopk(__chunks, query, k=k)
    if return_chunks:
        return answer_chunks
    return "\n".join(answer_chunks)
