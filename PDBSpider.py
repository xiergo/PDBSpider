import re
import urllib.request
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
                return cont.group(1).strip()
        return ''
    
    def _get_all_single_chains(self):
        chains = []
        soup = self.soup.find('div', {'id': 'macromoleculespanel'})
        if not soup:
            return chains
        for table in soup.find_all('table', {'class': "table table-bordered table-condensed tableEntity"}):
            chain = {}
            tds = [i.text.replace('\xa0', ' ') for i in table.find_all('td')]
            chain['pdb_id'] = self.pdb_id
            chain['molecule'] = tds[0]
            chain['chains'] = tds[1]
            chain['sequence_length'] = tds[2]
            chain['organism'] = tds[3]
            chain['details'] = tds[4]
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