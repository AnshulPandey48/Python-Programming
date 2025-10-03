import torch
import torch.nn as nn 

class Encoder(nn.Module):
    def __init__(self,input_dim,emb_dim,hidden_dim,n_layers,dropout):
        super.__init__()
        self.embedding = nn.Embedding(input_dim,emb_dim) #return a tensor containing the embeddings
        self.lstm = nn.LSTM(emb_dim,hidden_dim,n_layers,dropout=dropout,batch_first=True)
    def forward(self,src):
        embedded = self.embedding(src)
        output,(hidden,cell) = self.lstm(embedded)
        return hidden , cell
class 