class Sudoku(object):
    '''Defines a sudoku object.'''

    def __init__(self, sudokuData):
        if not (isinstance(sudokuData, str) and len(sudokuData) == 81 and sudokuData.isdigit()):
            raise ValueError('invalid sudoku data')
        
        self._sudoku = [[sudokuData[i*9+j] for i in range(9)] for j in range(9)]
        self._smalls = []
        for x in range(0,8,3):
            for y in range(0,8,3):
                self._smalls.append([(x+xi,y+yi) for xi in range(3) for yi in range(3)])

    def display(self):
        for i in range(9):
            print(' ',end='')
            for j in range(9):
                if j in (2,5):
                    print(self._sudoku[j][i], end=' ┃ ')
                else:
                    print(self._sudoku[j][i], end='  ')
            if i in (2,5):
                print('\n━━━━━╋━━━━━━╋━━━━━', end='')
            print()

    def solve(self, x=0, y=0):
        x, y = self._nextBlank()
        if x == -1:
            return True
        for val in range(1,10):
            val = str(val)
            if self._isLegit(x, y, val):
                self._sudoku[x][y] = val
                if self.solve(x, y):
                    return True
                self._sudoku[x][y] = '0'
        return False

    def _nextBlank(self):
        for x in range(9):
            for y in range(9):
                if self._sudoku[x][y] == '0':
                    return x,y
        return -1,-1

    def _isLegit(self, x, y, value):
        if self._sudoku[x][y] != '0':
            return False
        for i in range(8):
            if self._sudoku[i][y] == value or self._sudoku[x][i] == value:
                return False
        for i in self._smalls:
            if (x,y) in i:
                group = self._smalls.index(i)
                break
        for i in self._smalls[group]:
            if i != (x,y) and self._sudoku[i[0]][i[1]] == value:
                return False
        return True


s = Sudoku('600087000000905706040000080030002000004000690000410023500030170080090200001076300')
s.display()
s.solve()
s.display()
