
from datatig.jsondeepreaderwriter import JSONDeepReaderWriter

def test_read_root_key():
    obj = JSONDeepReaderWriter(
        {
            'cat':'Miaow',
            'dog':'woof'
        }
    )
    assert obj.read('cat') == 'Miaow'

def test_read_level1_all_keys():
    obj = JSONDeepReaderWriter(
        {
            'cat':{
                'noise':'Miaow',
                'tail':True,
            },
            'dog':'woof'
        }
    )
    assert obj.read('cat/noise') == 'Miaow'
    assert obj.read('cat/tail') == True
