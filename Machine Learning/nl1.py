import argparse
import pandas as pd
from sentence_transformers import CrossEncoder
from transformers import AutoTokenizer
#cross encoder is used for pair wise task like similarity or ranking
import torch
from tqdm import tqdm 
import torch.nn.functional as F
import numpy as np 
import os

#parsing command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Compute semantic similarity using NLI Cross-Encoder.")
    #adding arguments
    parser.add_argument('--input','-i',required=True,help="Input CSV path with 'text1' and 'text2' columns.")
    #input long flag , -i shot flag
    parser.add_argument('--output','-o', required=True,help="output csv with similarity score")
    #optional argument
    parser.add_argument('--model','-m',default= 'cross-encoder/nli-roberta-base',help="pretrained model")
    #can be override or else default model 
    parser.add_argument('--batch_size','-b',type = int,default=16,help="batch size for prediction")
    #if --truncate included , args.truncate becomes true
    parser.add_argument('--truncate',action='store_true',help="truncate long text")
    return parser.parse_args()

#truncate function
def truncate_text(text,tokenizer,max_len): #defaut max_len = 512
    if not text:
        return ""
    tokens = tokenizer.encode(text,truncation = True,max_len = max_len)
    return tokenizer.decode(tokens,skip_special_tokens = True)

def main():
    args = parse_args()
    if not os.path.exists(args.input):
        raise FileNotFoundError(f"input file not not found: {args.input}")
    
    df = pd.read_csv(args.input)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    #loading the cross encoder model
    model = CrossEncoder(args.model,device=device)
    #load tokenizer if truncate is set true
    tokenizer = None
    if args.truncate:
      tokenizer = AutoTokenizer.from_pretrained(args.model,use_fast = True)  
      #use fast = True , uses rust based backed , fast tokenizer
      print(f"[info] tokenizer loaded for truncation (max_len = {args.max_len})")

    #prepare pairs for prediction
    pairs = [] # creates empty list to store pair of sentences
    #df.iterrows -> iterate row over pandas dataframe
    for idx , row in df.iterrows():
        t1 =  str(row['text1']) if not pd.isna(row['text1']) else ""
        t2 =  str(row['text2']) if not pd.isna(row['text2']) else ""
        #pd.isna check for nan or empty values
        if args.truncate and tokenizer:
            t1 = truncate_text(t1,tokenizer,args.max_len)
            t2 = truncate_text(t2,tokenizer,args.max_len)
        pairs.append((t1,t2))
        #prediction loop
    scores = []
    for start in tqdm(range(0,len(pairs),args.batch_size),desc = "predicting batches"):
        end = min(start + args.batch_size,len(pairs))
        batch = pairs[start:end]
        #ensuring no out of bound error 
        logits = model.predict(batch,batch_size=len(batch),show_progress_bar=False)
        logits_tensor = torch.tensor(logits)
        #applyting softmax function
        probs = F.softmax(logits_tensor,dim = 1)
        entailment_probs = probs[:,1].numpy() # torch tensor into numpy tensors
        scores.extend(entailment_probs)

    df['similarity_score']= pd.Series(scores).round(6)
    #pd.series converts list into panda series which a column of data
    df.to_csv(args.output,index = False)
    print(f"[INFO] Similarity scores saved to {args.output}")   
                   
if __name__ == "__main__":
    main()
    
