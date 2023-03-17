import argparse
import pandas as pd
from tqdm import tqdm
from PDBSpider import PDBSpider


parser = argparse.ArgumentParser('Crawling for chain information on Protein Data Bank website.')
parser.add_argument('--input_path', help='list for pdb id, one for each line.')
parser.add_argument('--output_path', default=None, help='output file. If None, input file path suffixed with ".out" will be used.')
args = parser.parse_args()
print(args)

def main():
    with open(args.input_path, 'r') as f:
        pdb_list = f.readlines()
    if args.output_path:
        out_path = args.output_path
    else:
        out_path = args.input_path + '.out'
    for i, pdb_id in tqdm(enumerate(pdb_list)):
        spider = PDBSpider(pdb_id.strip())
        res_dict = spider.get_content()
        chains = res_dict.pop('chains')
        df_chains = pd.DataFrame(chains)
        df = pd.merge(df_chains, pd.DataFrame([res_dict]), on='pdb_id')
        if i == 0:
            header = True
            mode = 'w'
        else:
            header = False
            mode = 'a'
        df.to_csv(out_path, sep='\t', mode=mode, header=header, index=False)

if __name__ == '__main__':
    main()




