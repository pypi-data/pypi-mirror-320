from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Union, Mapping, Any, Callable, Iterable



# class DocEmbedModel:
#     def __init__(self,
#                  model_name:str=None,
#                  device:str
#                 ):

#         if model_name is None:
#             model_name = "all-MiniLM-L6-v2"

#         self.doc_embed_model = SentenceTransformer(model_name, device=device)

#     def encode(self,
#                docs:List[str],
#                convert_to_tensor: bool=False,
#                verbose:bool=False
#             ):
#         embeddings = self.doc_embed_model.encode(docs, convert_to_tensor=convert_to_tensor, show_progress_bar=verbose)
#         return embeddings
