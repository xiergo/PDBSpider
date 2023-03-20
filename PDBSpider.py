import re
import sys
import urllib.request
import pandas as pd
from bs4 import BeautifulSoup

class PDBSpider:
    """PDB Spider"""
    
    def __init__(self, pdb_id):
        self.pdb_id = pdb_id.upper()
        self.soup = self._get_page_content()

    def _get_page_content(self):
        site_url = 'https://www.rcsb.org/structure/' + self.pdb_id
        page=urllib.request.urlopen(site_url).read().decode('UTF-8')
        soup=BeautifulSoup(page, 'html.parser')
        return soup

    def _get_content_from_keyword(self, soup, pattern, type = None):
        if not soup:
            return ''
        if type:
            ls = [x.text.replace('&nbsp',' ').replace('\xa0', '') for x in soup.find_all(type)]
        else:
            # split by hr/br
            ls = [BeautifulSoup(i, 'html.parser').text for i in re.split('<[bh]r/>', str(soup))]
            
        for x in ls:
            cont=re.search(pattern, x)
            if cont:
                return cont.group(1).strip().replace('\n', ' ')
        return ''
    
    def _get_all_single_chains(self):
        chains = []
        soup = self.soup.find('div', {'id': 'macromoleculespanel'})
        if not soup:
            return chains
        for table in soup.find_all('table', {'class': "table table-bordered table-condensed tableEntity"}):
            chain = {}
            tds = table.find_all('td')
            for i in [1, 4]:
                if tds[i].find('div', {'class': 'hide'}):
                    tds[i] = tds[i].find('div', {'class': 'hide'})
            tds = [i.text.replace('\xa0', ' ').replace('\n', ' ') for i in tds]
            chain['pdb_id'] = self.pdb_id
            chain['molecule'] = tds[0]
            chain['chains'] = tds[1].replace('Less', '').strip()
            chain['sequence_length'] = tds[2]
            chain['organism'] = tds[3]
            chain['details'] = tds[4].replace('Less', '').strip()
            chains.append(chain)
        return chains
    
    def get_content(self):
        content = {}
        content['pdb_id'] = self.pdb_id
        content['resolution'] = self._get_content_from_keyword(self.soup, 'Resolution:(.+)', 'li')
        content['method'] = self._get_content_from_keyword(self.soup, 'Method:(.+)', 'li')
        content['release_date'] = self._get_content_from_keyword(self.soup, 'Released:([0-9\\-]+)', 'li')
        content['deposite_date'] = self._get_content_from_keyword(self.soup, 'Deposited:([0-9\\-]+)', 'li')
        content['classification'] = self._get_content_from_keyword(self.soup, 'Classification:(.+)', 'li')
        content['organisms'] = self._get_content_from_keyword(self.soup, 'Organism\\(s\\):(.+)', 'li')
        content['mutations'] = self._get_content_from_keyword(self.soup, 'Mutation\\(s\\):*(.+)', 'li')
        content['author'] = self._get_content_from_keyword(self.soup, 'Deposition Author\\(s\\):(.+)', 'li')
        content['r_value_free'] = self._get_content_from_keyword(self.soup, 'R-Value Free:(.+)', 'li')
        content['r_value_work'] = self._get_content_from_keyword(self.soup, 'R-Value Work:(.+)', 'li')
        content['r_value_observed'] = self._get_content_from_keyword(self.soup, 'R-Value Observed:(.+)', 'li')
        content['title'] = self.soup.find('span', {'id': 'structureTitle'}).text

        # <div class="well well-sm hidden-sm hidden-xs well-nomar" id="macromoleculeContent">
        soup = self.soup.find('div', {'id': 'macromoleculeContent'})
        content['total_structure_weight'] = self._get_content_from_keyword(soup, 'Total Structure Weight: (.+)', 'li')
        content['atom_count'] = self._get_content_from_keyword(soup, 'Atom Count: (.+)', 'li')
        content['modelled_residue_count'] = self._get_content_from_keyword(soup, 'Modelled Residue Count: (.+)', 'li')
        content['deposited_residue_count'] = self._get_content_from_keyword(soup, 'Deposited Residue Count: (.+)', 'li')
        content['unique_protein_chains'] = self._get_content_from_keyword(soup, 'Unique protein chains: (.+)', 'li')

        # <div class="item imageCarouselItem" id="Carousel-BiologicalUnit1">
        soup = self.soup.find('div', {'id': 'Carousel-BiologicalUnit1'})
        content['global_symmetry'] = self._get_content_from_keyword(soup, 'Global Symmetry: (.+)').replace('(3D View)', '').strip()
        content['global_stoichiometry'] = self._get_content_from_keyword(soup, 'Global Stoichiometry: (.+)').replace('(3D View)', '').strip()
        content['local_symmetry'] = self._get_content_from_keyword(soup, 'Local Symmetry: (.+)').replace('(3D View)', '').strip()
        content['local_stoichiometry'] = self._get_content_from_keyword(soup, 'Local Stoichiometry: (.+)').replace('(3D View)', '').strip()
        # single chains
        content['chains'] = self._get_all_single_chains()
        return content


def main():
    out_path = sys.argv[1]
    pdbs = sys.argv[2:]
    for pdb_id in pdbs:
        try:
            spider = PDBSpider(pdb_id)
        except:
            print(f'{pdb_id} failed')
            continue
        res_dict = spider.get_content()
        chains = res_dict.pop('chains')
        if not chains:
            chains = [{'pdb_id': pdb_id, 'molecule': '', 'chains': '',
                    'seqence_length': '', 'organism': '', 'details': ''}]
        df_chains = pd.DataFrame(chains)
        df = pd.merge(df_chains, pd.DataFrame([res_dict]), on='pdb_id')
        df.to_csv(out_path, sep='\t', mode='a', header=False, index=False)

if __name__ == '__main__':
    main()