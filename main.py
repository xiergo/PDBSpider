import argparse
import os
import warnings
import pandas as pd
from tqdm import tqdm
from PDBSpider import PDBSpider


parser = argparse.ArgumentParser('Crawling for chain information on Protein Data Bank website.')
parser.add_argument('--input_path', help='list for pdb id, one for each line.')
parser.add_argument('--output_path', default=None, help='output file. If None, input file path suffixed with ".out" will be used.')
parser.add_argument('--continu', action='store_true', help='whether or not go on crawling for data from previous results. If set this argument, all pdb entries already existing in the output file will be skipped.')
args = parser.parse_args()
print(args)

def main():
    with open(args.input_path, 'r') as f:
        pdb_list = [i.strip() for i in f.readlines()]
    if args.output_path:
        out_path = args.output_path
    else:
        out_path = args.input_path + '.out'
    if not os.path.isfile(out_path):
        if args.continu:
            warnings.warn(f'set "--continu" but no existing results file "{out_path}" found')
            args.continu = False
    if args.continu:
        with open(out_path, 'r') as f:
            pdb_exist = [i.split('\t')[0] for i in f.readlines()[1:]]
        pdb_list = list(set(pdb_list) - set(pdb_exist))
    
    for i, pdb_id in tqdm(enumerate(pdb_list)):
        spider = PDBSpider(pdb_id)
        res_dict = spider.get_content()
        chains = res_dict.pop('chains')
        df_chains = pd.DataFrame(chains)
        df = pd.merge(df_chains, pd.DataFrame([res_dict]), on='pdb_id')
        if (i == 0) and (not args.continu):
            header = True
            mode = 'w'
        else:
            header = False
            mode = 'a'
        df.to_csv(out_path, sep='\t', mode=mode, header=header, index=False)

if __name__ == '__main__':
    main()




