import torch
import torch.nn as nn 

class Encoder(nn.Module):
    def __init__(self,input_dim,emb_dim,hidden_dim,n_layers,dropout):
        super.__init__()
        self.embedding = nn.Embedding(input_dim,emb_dim) #return a tensor containing the embeddings
        