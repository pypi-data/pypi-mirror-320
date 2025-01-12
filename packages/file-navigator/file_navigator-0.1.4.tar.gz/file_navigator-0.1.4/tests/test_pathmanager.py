import unittest
from file_navigator.pathfinder import _PathManager
from file_navigator.abc_loader import ABLoader

class Test_PathManager(unittest.TestCase):
       
    def test_empty_init(self):
        with self.assertRaises(ValueError):
           _PathManager([])

    
    def test_select_paths(self):
        mock_dir = r"C:\mock_directory"        
        mock_files = ['Forex.xlsx','EURGBP_H4.csv','EURGBP_M5.csv',
                      'EURJPY_H1.csv','EURJPY_M30.csv', 'EURUSD_M5.csv',
                      'audcad.txt','audchf.txt','audusd.txt',
                      'cadaud.txt','cadeur.txt','cadjpy.txt',
                      'cadpln.txt','cadusd.txt','chfgbp.txt',
                      'chfpln.txt','chfusd.txt','euraud.txt',
                      'eurchf.txt','eurgbp.txt','eurjpy.txt',
                      'eurpln.txt','gbpcad.txt','gbpchf.txt',
                      'gbpeur.txt','gbpjpy.txt','gbppln.txt',
                      'jpyaud.txt','jpypln.txt','nzdusd.txt',
                      'usdcad.txt','usdchf.txt','usdjpy.txt',
                      'usdpln.txt','xaggbp.txt','xauchf.txt',
                      'xaueur.txt','xaugbp.txt']

                
        mock_paths = [
            (mock_dir, f)   if 'xlsx' in f 
            else ('\\'.join([mock_dir, 'CURR']),f) if 'csv' in f 
            else ('\\'.join([mock_dir, f[:3].upper()]), f)
            for f in mock_files
            ]
        
        args = [
            ('J.*|X.*',  'regex'),
            ('*',  'glob'),
            ('N', 'isin'),
            ('XAG|NZD', 'regex'),
            (r'C:\mock_directory\CURR', 'eq')
            ]
        expected = {
            ('J.*|X.*',  'regex'): ['jpyaud.txt', 'jpypln.txt', 'xaggbp.txt',
                                    'xauchf.txt', 'xaueur.txt', 'xaugbp.txt'],
            ('*', 'glob'): mock_files,
            ('N', 'isin'): ['nzdusd.txt'],
            ('XAG|NZD', 'regex'): ['xaggbp.txt', 'nzdusd.txt'],
            (r'C:\mock_directory\CURR', 'eq'): ['EURGBP_H4.csv', 'EURGBP_M5.csv',
                                                'EURJPY_H1.csv','EURJPY_M30.csv', 
                                                'EURUSD_M5.csv']
                }
        
        for arg in args:
            with self.subTest(arg = arg):
                result = [p[0] for p in _PathManager(mock_paths).select_paths(*arg).paths]
                self.assertCountEqual(result, expected[arg])
                with self.assertRaises(ValueError):
                    _PathManager(mock_paths).select_paths(('XXXXXXX',  'eq'))
        

    
    def test_groupby(self):
        mock_dir = r"C:\mock_directory"        
        mock_files = ['Forex.xlsx','EURGBP_H4.csv','EURGBP_M5.csv',
                      'EURJPY_H1.csv','EURJPY_M30.csv', 'EURUSD_M5.csv',
                      'audcad.txt','audchf.txt','audusd.txt',
                      'cadaud.txt','cadeur.txt','cadjpy.txt',
                      'cadpln.txt','cadusd.txt','chfgbp.txt',
                      'chfpln.txt','chfusd.txt','euraud.txt',
                      'eurchf.txt','eurgbp.txt','eurjpy.txt',
                      'eurpln.txt','gbpcad.txt','gbpchf.txt',
                      'gbpeur.txt','gbpjpy.txt','gbppln.txt',
                      'jpyaud.txt','jpypln.txt','nzdusd.txt',
                      'usdcad.txt','usdchf.txt','usdjpy.txt',
                      'usdpln.txt','xaggbp.txt','xauchf.txt',
                      'xaueur.txt','xaugbp.txt']

                
        mock_paths = [
            (mock_dir, f)   if 'xlsx' in f 
            else ('\\'.join([mock_dir, 'CURR']),f) if 'csv' in f 
            else ('\\'.join([mock_dir, f[:3].upper()]), f)
            for f in mock_files
            ]
        args = [('ext',None),
                ('path',None),
                ('name',None),
                ('ext','.txt','eq'), 
                ('path', '*AG','glob'), 
                ('name', r'^eur.*|^chf.*', 'regex')]
        expected = {
            ('ext',None): {'.xlsx':_PathManager(('C:\\mock_directory', 'Forex.xlsx')).paths,
                    '.csv':_PathManager([('C:\\mock_directory\\CURR', 'EURGBP_H4.csv'),
                                       ('C:\\mock_directory\\CURR', 'EURGBP_M5.csv'),
                                       ('C:\\mock_directory\\CURR', 'EURJPY_H1.csv'),
                                       ('C:\\mock_directory\\CURR', 'EURJPY_M30.csv'),
                                       ('C:\\mock_directory\\CURR', 'EURUSD_M5.csv')]
                                       ).paths,
                    '.txt':_PathManager([('C:\\mock_directory\\AUD', 'audcad.txt'),
                                        ('C:\\mock_directory\\AUD', 'audchf.txt'),
                                        ('C:\\mock_directory\\AUD', 'audusd.txt'),
                                        ('C:\\mock_directory\\CAD', 'cadaud.txt'),
                                        ('C:\\mock_directory\\CAD', 'cadeur.txt'),
                                        ('C:\\mock_directory\\CAD', 'cadjpy.txt'),
                                        ('C:\\mock_directory\\CAD', 'cadpln.txt'),
                                        ('C:\\mock_directory\\CAD', 'cadusd.txt'),
                                        ('C:\\mock_directory\\CHF', 'chfgbp.txt'),
                                        ('C:\\mock_directory\\CHF', 'chfpln.txt'),
                                        ('C:\\mock_directory\\CHF', 'chfusd.txt'),
                                        ('C:\\mock_directory\\EUR', 'euraud.txt'),
                                        ('C:\\mock_directory\\EUR', 'eurchf.txt'),
                                        ('C:\\mock_directory\\EUR', 'eurgbp.txt'),
                                        ('C:\\mock_directory\\EUR', 'eurjpy.txt'),
                                        ('C:\\mock_directory\\EUR', 'eurpln.txt'),
                                        ('C:\\mock_directory\\GBP', 'gbpcad.txt'),
                                        ('C:\\mock_directory\\GBP', 'gbpchf.txt'),
                                        ('C:\\mock_directory\\GBP', 'gbpeur.txt'),
                                        ('C:\\mock_directory\\GBP', 'gbpjpy.txt'),
                                        ('C:\\mock_directory\\GBP', 'gbppln.txt'),
                                        ('C:\\mock_directory\\JPY', 'jpyaud.txt'),
                                        ('C:\\mock_directory\\JPY', 'jpypln.txt'),
                                        ('C:\\mock_directory\\NZD', 'nzdusd.txt'),
                                        ('C:\\mock_directory\\USD', 'usdcad.txt'),
                                        ('C:\\mock_directory\\USD', 'usdchf.txt'),
                                        ('C:\\mock_directory\\USD', 'usdjpy.txt'),
                                        ('C:\\mock_directory\\USD', 'usdpln.txt'),
                                        ('C:\\mock_directory\\XAG', 'xaggbp.txt'),
                                        ('C:\\mock_directory\\XAU', 'xauchf.txt'),
                                        ('C:\\mock_directory\\XAU', 'xaueur.txt'),
                                        ('C:\\mock_directory\\XAU', 'xaugbp.txt')]
                                        ).paths
                    },
            ('path',None):{
                'C:\\mock_directory': _PathManager(
                    ('C:\\mock_directory', 'Forex.xlsx')
                    ).paths,
                'C:\\mock_directory\\CURR': _PathManager(
                    [('C:\\mock_directory\\CURR', 'EURGBP_H4.csv'),
                    ('C:\\mock_directory\\CURR', 'EURGBP_M5.csv'),
                    ('C:\\mock_directory\\CURR', 'EURJPY_H1.csv'),
                    ('C:\\mock_directory\\CURR', 'EURJPY_M30.csv'),
                    ('C:\\mock_directory\\CURR', 'EURUSD_M5.csv')]
                    ).paths,
                'C:\\mock_directory\\AUD': _PathManager(
                    [('C:\\mock_directory\\AUD', 'audcad.txt'),
                    ('C:\\mock_directory\\AUD', 'audchf.txt'),
                    ('C:\\mock_directory\\AUD', 'audusd.txt')]
                    ).paths,
                'C:\\mock_directory\\CAD': _PathManager(
                    [('C:\\mock_directory\\CAD', 'cadaud.txt'),
                    ('C:\\mock_directory\\CAD', 'cadeur.txt'),
                    ('C:\\mock_directory\\CAD', 'cadjpy.txt'),
                    ('C:\\mock_directory\\CAD', 'cadpln.txt'),
                    ('C:\\mock_directory\\CAD', 'cadusd.txt')]
                    ).paths,
                'C:\\mock_directory\\CHF': _PathManager(
                    [('C:\\mock_directory\\CHF', 'chfgbp.txt'),
                    ('C:\\mock_directory\\CHF', 'chfpln.txt'),
                    ('C:\\mock_directory\\CHF', 'chfusd.txt')]
                    ).paths,
                'C:\\mock_directory\\EUR': _PathManager(
                    [('C:\\mock_directory\\EUR', 'euraud.txt'),
                    ('C:\\mock_directory\\EUR', 'eurchf.txt'),
                    ('C:\\mock_directory\\EUR', 'eurgbp.txt'),
                    ('C:\\mock_directory\\EUR', 'eurjpy.txt'),
                    ('C:\\mock_directory\\EUR', 'eurpln.txt')]
                    ).paths,
                'C:\\mock_directory\\GBP': _PathManager(
                    [('C:\\mock_directory\\GBP', 'gbpcad.txt'),
                    ('C:\\mock_directory\\GBP', 'gbpchf.txt'),
                    ('C:\\mock_directory\\GBP', 'gbpeur.txt'),
                    ('C:\\mock_directory\\GBP', 'gbpjpy.txt'),
                    ('C:\\mock_directory\\GBP', 'gbppln.txt')]
                    ).paths,
                'C:\\mock_directory\\JPY': _PathManager(
                    [('C:\\mock_directory\\JPY', 'jpyaud.txt'),
                    ('C:\\mock_directory\\JPY', 'jpypln.txt')]
                    ).paths,
                'C:\\mock_directory\\NZD': _PathManager(
                    [('C:\\mock_directory\\NZD', 'nzdusd.txt')]
                    ).paths,
                'C:\\mock_directory\\USD': _PathManager(
                    [('C:\\mock_directory\\USD', 'usdcad.txt'),
                    ('C:\\mock_directory\\USD', 'usdchf.txt'),
                    ('C:\\mock_directory\\USD', 'usdjpy.txt'),
                    ('C:\\mock_directory\\USD', 'usdpln.txt')]
                    ).paths,
                'C:\\mock_directory\\XAG': _PathManager(
                    ('C:\\mock_directory\\XAG', 'xaggbp.txt')
                    ).paths,
                'C:\\mock_directory\\XAU': _PathManager(
                    [('C:\\mock_directory\\XAU', 'xauchf.txt'),
                    ('C:\\mock_directory\\XAU', 'xaueur.txt'),
                    ('C:\\mock_directory\\XAU', 'xaugbp.txt')]
                    ).paths
                },
            ('name',None):{
                'Forex': _PathManager(('C:\\mock_directory', 'Forex.xlsx')).paths,
                'EURGBP_H4': _PathManager(('C:\\mock_directory\\CURR', 'EURGBP_H4.csv')).paths,
                'EURGBP_M5': _PathManager(('C:\\mock_directory\\CURR', 'EURGBP_M5.csv')).paths,
                'EURJPY_H1': _PathManager(('C:\\mock_directory\\CURR', 'EURJPY_H1.csv')).paths,
                'EURJPY_M30': _PathManager(('C:\\mock_directory\\CURR', 'EURJPY_M30.csv')).paths,
                'EURUSD_M5': _PathManager(('C:\\mock_directory\\CURR', 'EURUSD_M5.csv')).paths,
                'audcad': _PathManager(('C:\\mock_directory\\AUD', 'audcad.txt')).paths,
                'audchf': _PathManager(('C:\\mock_directory\\AUD', 'audchf.txt')).paths,
                'audusd': _PathManager(('C:\\mock_directory\\AUD', 'audusd.txt')).paths,
                'cadaud': _PathManager(('C:\\mock_directory\\CAD', 'cadaud.txt')).paths,
                'cadeur': _PathManager(('C:\\mock_directory\\CAD', 'cadeur.txt')).paths,
                'cadjpy': _PathManager(('C:\\mock_directory\\CAD', 'cadjpy.txt')).paths,
                'cadpln': _PathManager(('C:\\mock_directory\\CAD', 'cadpln.txt')).paths,
                'cadusd': _PathManager(('C:\\mock_directory\\CAD', 'cadusd.txt')).paths,
                'chfgbp': _PathManager(('C:\\mock_directory\\CHF', 'chfgbp.txt')).paths,
                'chfpln': _PathManager(('C:\\mock_directory\\CHF', 'chfpln.txt')).paths,
                'chfusd': _PathManager(('C:\\mock_directory\\CHF', 'chfusd.txt')).paths,
                'euraud': _PathManager(('C:\\mock_directory\\EUR', 'euraud.txt')).paths,
                'eurchf': _PathManager(('C:\\mock_directory\\EUR', 'eurchf.txt')).paths,
                'eurgbp': _PathManager(('C:\\mock_directory\\EUR', 'eurgbp.txt')).paths,
                'eurjpy': _PathManager(('C:\\mock_directory\\EUR', 'eurjpy.txt')).paths,
                'eurpln': _PathManager(('C:\\mock_directory\\EUR', 'eurpln.txt')).paths,
                'gbpcad': _PathManager(('C:\\mock_directory\\GBP', 'gbpcad.txt')).paths,
                'gbpchf': _PathManager(('C:\\mock_directory\\GBP', 'gbpchf.txt')).paths,
                'gbpeur': _PathManager(('C:\\mock_directory\\GBP', 'gbpeur.txt')).paths,
                'gbpjpy': _PathManager(('C:\\mock_directory\\GBP', 'gbpjpy.txt')).paths,
                'gbppln': _PathManager(('C:\\mock_directory\\GBP', 'gbppln.txt')).paths,
                'jpyaud': _PathManager(('C:\\mock_directory\\JPY', 'jpyaud.txt')).paths,
                'jpypln': _PathManager(('C:\\mock_directory\\JPY', 'jpypln.txt')).paths,
                'nzdusd': _PathManager(('C:\\mock_directory\\NZD', 'nzdusd.txt')).paths,
                'usdcad': _PathManager(('C:\\mock_directory\\USD', 'usdcad.txt')).paths,
                'usdchf': _PathManager(('C:\\mock_directory\\USD', 'usdchf.txt')).paths,
                'usdjpy': _PathManager(('C:\\mock_directory\\USD', 'usdjpy.txt')).paths,
                'usdpln': _PathManager(('C:\\mock_directory\\USD', 'usdpln.txt')).paths,
                'xaggbp': _PathManager(('C:\\mock_directory\\XAG', 'xaggbp.txt')).paths,
                'xauchf': _PathManager(('C:\\mock_directory\\XAU', 'xauchf.txt')).paths,
                'xaueur': _PathManager(('C:\\mock_directory\\XAU', 'xaueur.txt')).paths,
                'xaugbp': _PathManager(('C:\\mock_directory\\XAU', 'xaugbp.txt')).paths
                },
            ('ext','.txt','eq'): {
                False:_PathManager([('C:\\mock_directory', 'Forex.xlsx'),
                                    ('C:\\mock_directory\\CURR', 'EURGBP_H4.csv'),
                                    ('C:\\mock_directory\\CURR', 'EURGBP_M5.csv'),
                                    ('C:\\mock_directory\\CURR', 'EURJPY_H1.csv'),
                                    ('C:\\mock_directory\\CURR', 'EURJPY_M30.csv'),
                                    ('C:\\mock_directory\\CURR', 'EURUSD_M5.csv')
                                    ]).paths,
                True:_PathManager([('C:\\mock_directory\\AUD', 'audcad.txt'),
                                   ('C:\\mock_directory\\AUD', 'audchf.txt'),
                                   ('C:\\mock_directory\\AUD', 'audusd.txt'),
                                   ('C:\\mock_directory\\CAD', 'cadaud.txt'),
                                   ('C:\\mock_directory\\CAD', 'cadeur.txt'),
                                   ('C:\\mock_directory\\CAD', 'cadjpy.txt'),
                                   ('C:\\mock_directory\\CAD', 'cadpln.txt'),
                                   ('C:\\mock_directory\\CAD', 'cadusd.txt'),
                                   ('C:\\mock_directory\\CHF', 'chfgbp.txt'),
                                   ('C:\\mock_directory\\CHF', 'chfpln.txt'),
                                   ('C:\\mock_directory\\CHF', 'chfusd.txt'),
                                   ('C:\\mock_directory\\EUR', 'euraud.txt'),
                                   ('C:\\mock_directory\\EUR', 'eurchf.txt'),
                                   ('C:\\mock_directory\\EUR', 'eurgbp.txt'),
                                   ('C:\\mock_directory\\EUR', 'eurjpy.txt'),
                                   ('C:\\mock_directory\\EUR', 'eurpln.txt'),
                                   ('C:\\mock_directory\\GBP', 'gbpcad.txt'),
                                   ('C:\\mock_directory\\GBP', 'gbpchf.txt'),
                                   ('C:\\mock_directory\\GBP', 'gbpeur.txt'),
                                   ('C:\\mock_directory\\GBP', 'gbpjpy.txt'),
                                   ('C:\\mock_directory\\GBP', 'gbppln.txt'),
                                   ('C:\\mock_directory\\JPY', 'jpyaud.txt'),
                                   ('C:\\mock_directory\\JPY', 'jpypln.txt'),
                                   ('C:\\mock_directory\\NZD', 'nzdusd.txt'),
                                   ('C:\\mock_directory\\USD', 'usdcad.txt'),
                                   ('C:\\mock_directory\\USD', 'usdchf.txt'),
                                   ('C:\\mock_directory\\USD', 'usdjpy.txt'),
                                   ('C:\\mock_directory\\USD', 'usdpln.txt'),
                                   ('C:\\mock_directory\\XAG', 'xaggbp.txt'),
                                   ('C:\\mock_directory\\XAU', 'xauchf.txt'),
                                   ('C:\\mock_directory\\XAU', 'xaueur.txt'),
                                   ('C:\\mock_directory\\XAU', 'xaugbp.txt')
                                    ]).paths
                }, 
            ('path', '*AG','glob'): {
                False:_PathManager([('C:\\mock_directory', 'Forex.xlsx'),
                                    ('C:\\mock_directory\\CURR', 'EURGBP_H4.csv'),
                                    ('C:\\mock_directory\\CURR', 'EURGBP_M5.csv'),
                                    ('C:\\mock_directory\\CURR', 'EURJPY_H1.csv'),
                                    ('C:\\mock_directory\\CURR', 'EURJPY_M30.csv'),
                                    ('C:\\mock_directory\\CURR', 'EURUSD_M5.csv'),
                                    ('C:\\mock_directory\\AUD', 'audcad.txt'),
                                    ('C:\\mock_directory\\AUD', 'audchf.txt'),
                                    ('C:\\mock_directory\\AUD', 'audusd.txt'),
                                    ('C:\\mock_directory\\CAD', 'cadaud.txt'),
                                    ('C:\\mock_directory\\CAD', 'cadeur.txt'),
                                    ('C:\\mock_directory\\CAD', 'cadjpy.txt'),
                                    ('C:\\mock_directory\\CAD', 'cadpln.txt'),
                                    ('C:\\mock_directory\\CAD', 'cadusd.txt'),
                                    ('C:\\mock_directory\\CHF', 'chfgbp.txt'),
                                    ('C:\\mock_directory\\CHF', 'chfpln.txt'),
                                    ('C:\\mock_directory\\CHF', 'chfusd.txt'),
                                    ('C:\\mock_directory\\EUR', 'euraud.txt'),
                                    ('C:\\mock_directory\\EUR', 'eurchf.txt'),
                                    ('C:\\mock_directory\\EUR', 'eurgbp.txt'),
                                    ('C:\\mock_directory\\EUR', 'eurjpy.txt'),
                                    ('C:\\mock_directory\\EUR', 'eurpln.txt'),
                                    ('C:\\mock_directory\\GBP', 'gbpcad.txt'),
                                    ('C:\\mock_directory\\GBP', 'gbpchf.txt'),
                                    ('C:\\mock_directory\\GBP', 'gbpeur.txt'),
                                    ('C:\\mock_directory\\GBP', 'gbpjpy.txt'),
                                    ('C:\\mock_directory\\GBP', 'gbppln.txt'),
                                    ('C:\\mock_directory\\JPY', 'jpyaud.txt'),
                                    ('C:\\mock_directory\\JPY', 'jpypln.txt'),
                                    ('C:\\mock_directory\\NZD', 'nzdusd.txt'),
                                    ('C:\\mock_directory\\USD', 'usdcad.txt'),
                                    ('C:\\mock_directory\\USD', 'usdchf.txt'),
                                    ('C:\\mock_directory\\USD', 'usdjpy.txt'),
                                    ('C:\\mock_directory\\USD', 'usdpln.txt'),
                                    ('C:\\mock_directory\\XAU', 'xauchf.txt'),
                                    ('C:\\mock_directory\\XAU', 'xaueur.txt'),
                                    ('C:\\mock_directory\\XAU', 'xaugbp.txt')
                                    ]).paths,
                True:_PathManager([('C:\\mock_directory\\XAG', 'xaggbp.txt')]).paths
                }, 
            ('name', r'^eur.*|^chf.*', 'regex'): {
                False:_PathManager([('C:\\mock_directory', 'Forex.xlsx'),
                                    ('C:\\mock_directory\\CURR', 'EURGBP_H4.csv'),
                                    ('C:\\mock_directory\\CURR', 'EURGBP_M5.csv'),
                                    ('C:\\mock_directory\\CURR', 'EURJPY_H1.csv'),
                                    ('C:\\mock_directory\\CURR', 'EURJPY_M30.csv'),
                                    ('C:\\mock_directory\\CURR', 'EURUSD_M5.csv'),
                                    ('C:\\mock_directory\\AUD', 'audcad.txt'),
                                    ('C:\\mock_directory\\AUD', 'audchf.txt'),
                                    ('C:\\mock_directory\\AUD', 'audusd.txt'),
                                    ('C:\\mock_directory\\CAD', 'cadaud.txt'),
                                    ('C:\\mock_directory\\CAD', 'cadeur.txt'),
                                    ('C:\\mock_directory\\CAD', 'cadjpy.txt'),
                                    ('C:\\mock_directory\\CAD', 'cadpln.txt'),
                                    ('C:\\mock_directory\\CAD', 'cadusd.txt'),
                                    ('C:\\mock_directory\\GBP', 'gbpcad.txt'),
                                    ('C:\\mock_directory\\GBP', 'gbpchf.txt'),
                                    ('C:\\mock_directory\\GBP', 'gbpeur.txt'),
                                    ('C:\\mock_directory\\GBP', 'gbpjpy.txt'),
                                    ('C:\\mock_directory\\GBP', 'gbppln.txt'),
                                    ('C:\\mock_directory\\JPY', 'jpyaud.txt'),
                                    ('C:\\mock_directory\\JPY', 'jpypln.txt'),
                                    ('C:\\mock_directory\\NZD', 'nzdusd.txt'),
                                    ('C:\\mock_directory\\USD', 'usdcad.txt'),
                                    ('C:\\mock_directory\\USD', 'usdchf.txt'),
                                    ('C:\\mock_directory\\USD', 'usdjpy.txt'),
                                    ('C:\\mock_directory\\USD', 'usdpln.txt'),
                                    ('C:\\mock_directory\\XAG', 'xaggbp.txt'),
                                    ('C:\\mock_directory\\XAU', 'xauchf.txt'),
                                    ('C:\\mock_directory\\XAU', 'xaueur.txt'),
                                    ('C:\\mock_directory\\XAU', 'xaugbp.txt')
                                    ]).paths,
                True:_PathManager([('C:\\mock_directory\\CHF', 'chfgbp.txt'),
                                   ('C:\\mock_directory\\CHF', 'chfpln.txt'),
                                   ('C:\\mock_directory\\CHF', 'chfusd.txt'),
                                   ('C:\\mock_directory\\EUR', 'euraud.txt'),
                                   ('C:\\mock_directory\\EUR', 'eurchf.txt'),
                                   ('C:\\mock_directory\\EUR', 'eurgbp.txt'),
                                   ('C:\\mock_directory\\EUR', 'eurjpy.txt'),
                                   ('C:\\mock_directory\\EUR', 'eurpln.txt')
                                   ]).paths
                }
            }
        
        for arg in args:
            with self.subTest(arg = arg):
                result = {k: v.paths for k, v in _PathManager(mock_paths).groupby(*arg).items()}
                self.assertCountEqual(result, expected[arg])
                self.assertCountEqual(result.values(), expected[arg].values())
        
               
    def test_load(self):
        
        class MockLoader(ABLoader):
            
            def load(self, path, **kwargs):
                return f"{path} with {kwargs}"
            
        mock_dir = r"C:\mock_directory"        
        mock_files = ['Forex.xlsx', 'EURGBP_H4.csv', 'audcad.txt', 'audchf.txt']

                
        mock_paths = [
            (mock_dir, f)   if 'xlsx' in f 
            else ('\\'.join([mock_dir, 'CURR']),f) if 'csv' in f 
            else ('\\'.join([mock_dir, f[:3].upper()]), f)
            for f in mock_files
            ]
            
        kwargs = {'key1': 'value1'}
        expected = [
                    f"{p[0]} with {p[1]}" for p in 
                    [('\\'.join(p), kwargs)for p in mock_paths]
                    ]
        pm = _PathManager(mock_paths)
        self.assertCountEqual(pm.load(MockLoader(), **kwargs), expected)
        
    def test_load_bad_loader(self):
        
        class MockLoader:
            
            def load(self, path):
                return "Im not following ABLoader interface!"

        pm = _PathManager([(r"C:\mock_directory", 'Forex.xlsx')])
        kwargs = {'key1': 'value1'}
        with self.assertRaises(TypeError):
            pm.load(MockLoader(), **kwargs)
        

    
def suite():
    suite = unittest.TestSuite()
    suite.addTest(Test_PathManager('test_empty_init'))
    suite.addTest(Test_PathManager('test_select_paths'))
    suite.addTest(Test_PathManager('test_groupby'))
    suite.addTest(Test_PathManager('test_load'))
    suite.addTest(Test_PathManager('test_load_bad_loader'))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())