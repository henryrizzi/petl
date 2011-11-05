"""
Tests for the petl.transform module.

"""


from petl.testfun import iassertequal
from petl import rename, fieldnames, cut, cat, convert, translate, extend, \
                rowslice, head, tail, sort, melt, recast, duplicates, conflicts, \
                mergeduplicates, select, complement, diff, stringcapture, \
                stringsplit


def test_rename():
    """Test the rename function."""

    table = [['foo', 'bar'],
             ['M', 12],
             ['F', 34],
             ['-', 56]]
    
    result = rename(table, {'foo': 'foofoo', 'bar': 'barbar'})
    assert list(fieldnames(result)) == ['foofoo', 'barbar']
    
    result = rename(table)
    result['foo'] = 'spong'
    assert list(fieldnames(result)) == ['spong', 'bar']
    
    # TODO test cachetag


def test_cut():
    """Test the cut function."""
    
    table = [['foo', 'bar', 'baz'],
             ['A', 1, 2],
             ['B', '2', '3.4'],
             [u'B', u'3', u'7.8', True],
             ['D', 'xyz', 9.0],
             ['E', None]]

    cut1 = cut(table, 'foo')
    expectation = [['foo'],
                   ['A'],
                   ['B'],
                   [u'B'],
                   ['D'],
                   ['E']]
    iassertequal(expectation, cut1)
    
    cut2 = cut(table, 'foo', 'baz')
    expectation = [['foo', 'baz'],
                   ['A', 2],
                   ['B', '3.4'],
                   [u'B', u'7.8'],
                   ['D', 9.0],
                   ['E', None]]
    iassertequal(expectation, cut2)
    
    cut3 = cut(table, 0, 2)
    expectation = [['foo', 'baz'],
                   ['A', 2],
                   ['B', '3.4'],
                   [u'B', u'7.8'],
                   ['D', 9.0],
                   ['E', None]]
    iassertequal(expectation, cut3)
    
    cut4 = cut(table, 'bar', 0)
    expectation = [['bar', 'foo'],
                   [1, 'A'],
                   ['2', 'B'],
                   [u'3', u'B'],
                   ['xyz', 'D'],
                   [None, 'E']]
    iassertequal(expectation, cut4)
    

def test_cat():
    """Test the cat function."""
    
    table1 = [['foo', 'bar'],
              [1, 'A'],
              [2, 'B']]

    table2 = [['bar', 'baz'],
              ['C', True],
              ['D', False]]
    
    cat1 = cat(table1, table2, missing=None)
    expectation = [['foo', 'bar', 'baz'],
                   [1, 'A', None],
                   [2, 'B', None],
                   [None, 'C', True],
                   [None, 'D', False]]
    iassertequal(expectation, cat1)

    # how does cat cope with uneven rows?
    
    table3 = [['foo', 'bar', 'baz'],
              ['A', 1, 2],
              ['B', '2', '3.4'],
              [u'B', u'3', u'7.8', True],
              ['D', 'xyz', 9.0],
              ['E', None]]

    cat3 = cat(table3, missing=None)
    expectation = [['foo', 'bar', 'baz'],
                   ['A', 1, 2],
                   ['B', '2', '3.4'],
                   [u'B', u'3', u'7.8'],
                   ['D', 'xyz', 9.0],
                   ['E', None, None]]
    iassertequal(expectation, cat3)
    
    # cat more than two tables?
    cat4 = cat(table1, table2, table3)
    expectation = [['foo', 'bar', 'baz'],
                   [1, 'A', None],
                   [2, 'B', None],
                   [None, 'C', True],
                   [None, 'D', False],
                   ['A', 1, 2],
                   ['B', '2', '3.4'],
                   [u'B', u'3', u'7.8'],
                   ['D', 'xyz', 9.0],
                   ['E', None, None]]
    iassertequal(expectation, cat4)
    
    # TODO test cachetag


def test_convert():
    
    table = [['foo', 'bar', 'baz'],
             ['A', 1, 2],
             ['B', '2', '3.4'],
             [u'B', u'3', u'7.8', True],
             ['D', 'xyz', 9.0],
             ['E', None]]
    
    # test the style where the converters functions are passed in as a dictionary
    converters = {'foo': str, 'bar': int, 'baz': float}
    conv = convert(table, converters, errorvalue='error')
    expectation = [['foo', 'bar', 'baz'],
                   ['A', 1, 2.0],
                   ['B', 2, 3.4],
                   ['B', 3, 7.8, True], # N.B., long rows are preserved
                   ['D', 'error', 9.0],
                   ['E', 'error']] # N.B., short rows are preserved
    iassertequal(expectation, conv) 
    
    # test the style where the converters functions are added one at a time
    conv = convert(table, errorvalue='err')
    conv['foo'] = str
    conv['bar'] = int
    conv['baz'] = float 
    expectation = [['foo', 'bar', 'baz'],
                   ['A', 1, 2.0],
                   ['B', 2, 3.4],
                   ['B', 3, 7.8, True],
                   ['D', 'err', 9.0],
                   ['E', 'err']]
    iassertequal(expectation, conv) 
    
    
def test_translate():
    """Test the translate function."""
    
    table = [['foo', 'bar'],
             ['M', 12],
             ['F', 34],
             ['-', 56]]
    
    trans = {'M': 'male', 'F': 'female'}
    result = translate(table, 'foo', trans)
    expectation = [['foo', 'bar'],
                   ['male', 12],
                   ['female', 34],
                   ['-', 56]]
    iassertequal(expectation, result)


def test_extend():
    """Test the extend function."""

    table = [['foo', 'bar'],
             ['M', 12],
             ['F', 34],
             ['-', 56]]
    
    result = extend(table, 'baz', 42)
    expectation = [['foo', 'bar', 'baz'],
                   ['M', 12, 42],
                   ['F', 34, 42],
                   ['-', 56, 42]]
    iassertequal(expectation, result)

    result = extend(table, 'baz', lambda rec: rec['bar'] * 2)
    expectation = [['foo', 'bar', 'baz'],
                   ['M', 12, 24],
                   ['F', 34, 68],
                   ['-', 56, 112]]
    iassertequal(expectation, result)


def test_rowslice():
    """Test the rowslice function."""
    
    table = [['foo', 'bar', 'baz'],
             ['A', 1, 2],
             ['B', '2', '3.4'],
             [u'B', u'3', u'7.8', True],
             ['D', 'xyz', 9.0],
             ['E', None]]

    result = rowslice(table, 0, 2)
    expectation = [['foo', 'bar', 'baz'],
                   ['A', 1, 2],
                   ['B', '2', '3.4']]
    iassertequal(expectation, result)

    result = rowslice(table, 1, 2)
    expectation = [['foo', 'bar', 'baz'],
                   ['B', '2', '3.4']]
    iassertequal(expectation, result)

    result = rowslice(table, 1, 5, 2)
    expectation = [['foo', 'bar', 'baz'],
                   ['B', '2', '3.4'],
                   ['D', 'xyz', 9.0]]
    iassertequal(expectation, result)



def test_head():
    """Test the head function."""
    
    table1 = [['foo', 'bar'],
              ['a', 1],
              ['b', 2],
              ['c', 5],
              ['d', 7],
              ['f', 42],
              ['f', 3],
              ['h', 90],
              ['k', 12],
              ['l', 77],
              ['q', 2]]
    
    table2 = head(table1, 4)
    expect = [['foo', 'bar'],
              ['a', 1],
              ['b', 2],
              ['c', 5],
              ['d', 7]]
    iassertequal(expect, table2)


def test_tail():
    """Test the tail function."""
    
    table1 = [['foo', 'bar'],
              ['a', 1],
              ['b', 2],
              ['c', 5],
              ['d', 7],
              ['f', 42],
              ['f', 3],
              ['h', 90],
              ['k', 12],
              ['l', 77],
              ['q', 2]]
    
    table2 = tail(table1, 4)
    expect = [['foo', 'bar'],
              ['h', 90],
              ['k', 12],
              ['l', 77],
              ['q', 2]]
    iassertequal(expect, table2)
    
    
def test_sort_1():
    
    table = [['foo', 'bar'],
            ['C', '2'],
            ['A', '9'],
            ['A', '6'],
            ['F', '1'],
            ['D', '10']]
    
    result = sort(table, 'foo')
    expectation = [['foo', 'bar'],
                   ['A', '9'],
                   ['A', '6'],
                   ['C', '2'],
                   ['D', '10'],
                   ['F', '1']]
    iassertequal(expectation, result)
    
    
def test_sort_2():
    
    table = [['foo', 'bar'],
            ['C', '2'],
            ['A', '9'],
            ['A', '6'],
            ['F', '1'],
            ['D', '10']]
    
    result = sort(table, key=('foo', 'bar'))
    expectation = [['foo', 'bar'],
                   ['A', '6'],
                   ['A', '9'],
                   ['C', '2'],
                   ['D', '10'],
                   ['F', '1']]
    iassertequal(expectation, result)
    
    result = sort(table) # default is lexical sort
    expectation = [['foo', 'bar'],
                   ['A', '6'],
                   ['A', '9'],
                   ['C', '2'],
                   ['D', '10'],
                   ['F', '1']]
    iassertequal(expectation, result)
    
    
def test_sort_3():
    
    table = [['foo', 'bar'],
            ['C', '2'],
            ['A', '9'],
            ['A', '6'],
            ['F', '1'],
            ['D', '10']]
    
    result = sort(table, 'bar')
    expectation = [['foo', 'bar'],
                   ['F', '1'],
                   ['D', '10'],
                   ['C', '2'],
                   ['A', '6'],
                   ['A', '9']]
    iassertequal(expectation, result)
    
    
def test_sort_4():
    
    table = [['foo', 'bar'],
            ['C', 2],
            ['A', 9],
            ['A', 6],
            ['F', 1],
            ['D', 10]]
    
    result = sort(table, 'bar')
    expectation = [['foo', 'bar'],
                   ['F', 1],
                   ['C', 2],
                   ['A', 6],
                   ['A', 9],
                   ['D', 10]]
    iassertequal(expectation, result)
    
    
def test_sort_5():
    
    table = [['foo', 'bar'],
            [2.3, 2],
            [1.2, 9],
            [2.3, 6],
            [3.2, 1],
            [1.2, 10]]
    
    expectation = [['foo', 'bar'],
                   [1.2, 9],
                   [1.2, 10],
                   [2.3, 2],
                   [2.3, 6],
                   [3.2, 1]]

    # can use either field names or indices (from 1) to specify sort key
    result = sort(table, key=('foo', 'bar'))
    iassertequal(expectation, result)
    result = sort(table, key=(0, 1))
    iassertequal(expectation, result)
    result = sort(table, key=('foo', 1))
    iassertequal(expectation, result)
    result = sort(table, key=(0, 'bar'))
    iassertequal(expectation, result)
    
    
def test_sort_6():
    
    table = [['foo', 'bar'],
            [2.3, 2],
            [1.2, 9],
            [2.3, 6],
            [3.2, 1],
            [1.2, 10]]
    
    expectation = [['foo', 'bar'],
                   [3.2, 1],
                   [2.3, 6],
                   [2.3, 2],
                   [1.2, 10],
                   [1.2, 9]]

    result = sort(table, key=('foo', 'bar'), reverse=True)
    iassertequal(expectation, result)
    
    
def test_melt_1():
    
    table = [['id', 'gender', 'age'],
             [1, 'F', 12],
             [2, 'M', 17],
             [3, 'M', 16]]
    
    expectation = [['id', 'variable', 'value'],
                   [1, 'gender', 'F'],
                   [1, 'age', 12],
                   [2, 'gender', 'M'],
                   [2, 'age', 17],
                   [3, 'gender', 'M'],
                   [3, 'age', 16]]
    
    result = melt(table, key='id')
    iassertequal(expectation, result)

    result = melt(table, key='id', variable_field='variable', value_field='value')
    iassertequal(expectation, result)


def test_melt_2():
    
    table = [['id', 'time', 'height', 'weight'],
             [1, 11, 66.4, 12.2],
             [2, 16, 53.2, 17.3],
             [3, 12, 34.5, 9.4]]
    
    expectation = [['id', 'time', 'variable', 'value'],
                   [1, 11, 'height', 66.4],
                   [1, 11, 'weight', 12.2],
                   [2, 16, 'height', 53.2],
                   [2, 16, 'weight', 17.3],
                   [3, 12, 'height', 34.5],
                   [3, 12, 'weight', 9.4]]
    result = melt(table, key=('id', 'time'))
    iassertequal(expectation, result)

    expectation = [['id', 'time', 'variable', 'value'],
                   [1, 11, 'height', 66.4],
                   [2, 16, 'height', 53.2],
                   [3, 12, 'height', 34.5]]
    result = melt(table, key=('id', 'time'), variables='height')
    iassertequal(expectation, result)
    

def test_recast_1():
    
    table = [['id', 'variable', 'value'],
             [3, 'age', 16],
             [1, 'gender', 'F'],
             [2, 'gender', 'M'],
             [2, 'age', 17],
             [1, 'age', 12],
             [3, 'gender', 'M']]
    
    expectation = [['id', 'age', 'gender'],
                   [1, 12, 'F'],
                   [2, 17, 'M'],
                   [3, 16, 'M']]
    
    result = recast(table) # by default lift 'variable' field, hold everything else
    iassertequal(expectation, result)

    result = recast(table, variable_field='variable')
    iassertequal(expectation, result)

    result = recast(table, key='id', variable_field='variable')
    iassertequal(expectation, result)

    result = recast(table, key='id', variable_field='variable', value_field='value')
    iassertequal(expectation, result)


def test_recast_2():
    
    table = [['id', 'variable', 'value'],
             [3, 'age', 16],
             [1, 'gender', 'F'],
             [2, 'gender', 'M'],
             [2, 'age', 17],
             [1, 'age', 12],
             [3, 'gender', 'M']]
    
    expectation = [['id', 'gender'],
                   [1, 'F'],
                   [2, 'M'],
                   [3, 'M']]
    
    # can manually pick which variables you want to recast as fields
    # TODO this is awkward
    result = recast(table, key='id', variable_field={'variable':['gender']})
    iassertequal(expectation, result)


def test_recast_3():
    
    table = [['id', 'time', 'variable', 'value'],
             [1, 11, 'weight', 66.4],
             [1, 14, 'weight', 55.2],
             [2, 12, 'weight', 53.2],
             [2, 16, 'weight', 43.3],
             [3, 12, 'weight', 34.5],
             [3, 17, 'weight', 49.4]]
    
    expectation = [['id', 'time', 'weight'],
                   [1, 11, 66.4],
                   [1, 14, 55.2],
                   [2, 12, 53.2],
                   [2, 16, 43.3],
                   [3, 12, 34.5],
                   [3, 17, 49.4]]
    result = recast(table)
    iassertequal(expectation, result)

    # in the absence of an aggregation function, list all values
    expectation = [['id', 'weight'],
                   [1, [66.4, 55.2]],
                   [2, [53.2, 43.3]],
                   [3, [34.5, 49.4]]]
    result = recast(table, key='id')
    iassertequal(expectation, result)

    # max aggregation
    expectation = [['id', 'weight'],
                   [1, 66.4],
                   [2, 53.2],
                   [3, 49.4]]
    result = recast(table, key='id', reduce={'weight': max})
    iassertequal(expectation, result)

    # min aggregation
    expectation = [['id', 'weight'],
                   [1, 55.2],
                   [2, 43.3],
                   [3, 34.5]]
    result = recast(table, key='id', reduce={'weight': min})
    iassertequal(expectation, result)

    # mean aggregation
    expectation = [['id', 'weight'],
                   [1, 60.80],
                   [2, 48.25],
                   [3, 41.95]]
    def mean(values):
        return float(sum(values)) / len(values)
    def meanf(precision):
        def f(values):
            v = mean(values)
            v = round(v, precision)
            return v
        return f
    result = recast(table, key='id', reduce={'weight': meanf(precision=2)})
    iassertequal(expectation, result)

    
def test_recast4():
    
    # deal with missing data
    table = [['id', 'variable', 'value'],
             [1, 'gender', 'F'],
             [2, 'age', 17],
             [1, 'age', 12],
             [3, 'gender', 'M']]
    result = recast(table, key='id')
    expect = [['id', 'age', 'gender'],
              [1, 12, 'F'],
              [2, 17, None],
              [3, None, 'M']]
    iassertequal(expect, result)


def test_duplicates():
    
    table = [['foo', 'bar', 'baz'],
             ['A', 1, 2],
             ['B', '2', '3.4'],
             ['D', 'xyz', 9.0],
             ['B', u'3', u'7.8', True],
             ['B', '2', 42],
             ['E', None],
             ['D', 4, 12.3]]

    result = duplicates(table, 'foo')
    expectation = [['foo', 'bar', 'baz'],
                   ['B', '2', '3.4'],
                   ['B', u'3', u'7.8', True],
                   ['B', '2', 42],
                   ['D', 'xyz', 9.0],
                   ['D', 4, 12.3]]
    iassertequal(expectation, result)
    
    # test with compound key
    result = duplicates(table, key=('foo', 'bar'))
    expectation = [['foo', 'bar', 'baz'],
                   ['B', '2', '3.4'],
                   ['B', '2', 42]]
    iassertequal(expectation, result)
    