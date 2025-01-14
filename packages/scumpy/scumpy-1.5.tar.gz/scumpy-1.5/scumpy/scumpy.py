from sympy import *
from sympy.abc import x, Y

def MatrixOps(num:int, __MatrixName1__: str, __MatrixName2__: str, OPS: list[str]) -> str:
  if 'kron' in OPS:
    return [f'''
__ResultName1__ = {__MatrixName1__}*transpose({__MatrixName2__})
__ResultName2__ = transpose({__MatrixName1__})*{__MatrixName2__}
__ResultName3__ = kronecker_product(__ResultName1__, __ResultName2__)
print(trace(__ResultName1__))
print(trace(__ResultName3__))'''][num-1]
  else:
    return [f'''
__ResultName1__ = {__MatrixName1__}*transpose({__MatrixName2__})
__ResultName2__ = transpose({__MatrixName1__})*{__MatrixName2__}
print(max(__ResultName1__))
print(sum(__ResultName2__))'''][num-1]
  
def MatrixEquations(num: int, name1: str, name2: str, name3: str = None) -> str:
  if name3!=None:
    return [f'''
pretty_print({name1}.inv()*{name3}*({name2}.inv()))'''][num-1]
  else:
    return [f'''
Если у вас вид: AX=B, то код: pretty_print({name1}.inv()*{name2})
Если же вид: XA=B, то код: pretty_print({name2}*({name1}.inv()))'''][num-1]
    
def Deter(num:int, name1: str, name2: str = None) -> str:
  if name2!=None:
    return [f'''
name3={name1}*{name2}
__equationName__ = Eq(det(name3), 0)
VarName=solve(__equationName__)
В оформлении задания на бумаге самостоятельно найдите, линейной комбинацией 
каких строк/столбцов является столбец/строка с параметром'''][num-1]
  else:
    return [f'''
pretty_print(det({name1}))
'''][num-1]
    
def Permute(num: int, permName: str, index: int, btrace: int) -> str:

  return [f'''
# первое решение\n
name=Matrix([])
for i in {permName}:
  name=name.hstack(name, Matrix([0 if k+1!=i else 1 for k in range({len(permName)})]))
  
print(trace(name**{index}))
  
for varName in range(1, 100):
  print(name**varName, varName)
  if trace(name**varName) == {btrace}:
    break
''',
          
f'''
# второе решение\n  
A=zeros(len({permName}))
for i in range({len(permName)}):
    A[{permName}[i]-1,i]=1
print(trace(A**{index}))
m=1
while trace(A**m)!={btrace}:
  m+=1
print(m)
  '''][num-1]
    
def BigMatrices(num: int, order: int, diagstart: float, diagend: float, a12: float = None, a21: float = None, row1end: float = None) -> str:
  if row1end!=None:
    return [f'''
# Первое решение:\n   

VarName1={order} 
Name1={diagstart}
Name2={diagend}
Name3={row1end}

VarName2=(Name3-Name1)/(VarName1-1)
VarName3=(Name2/Name1)**(1/(VarName1-1))

diagonListName=[Name1*(VarName3**i) for i in range(VarName1)]
rowListName=[Name1 + VarName2*i for i in range(VarName1)]

inversed_diagListName=[1/i for i in diagonListName]
inversed_rowListName=[-i/k for i, k in zip(rowListName, diagonListName)]
print(sum(inversed_diagListName)+sum(inversed_rowListName[1:]))
print(min([min(inversed_diagListName), min(inversed_rowListName)]))
''',

f'''
a11 = {diagstart}
a1n = {row1end}
vsego_symbols = {order}
ann = {diagend}
q = solve(ann / x ** vsego_symbols - 1, x, minimal=True)
d = (a1n - a11) / vsego_symbols
spis_stroki = [1]
spis_diag = [1]
for i in range(vsego_symbols-1):
    spis_stroki.append(spis_stroki[-1] + d)
    spis_diag.append(spis_diag[-1] * q)

spis_stroki_B = [1]
spis_diag_B = [1]
for i in range(vsego_symbols-1):
    spis_diag_B.append(1 / spis_diag[1:][i])
    spis_stroki_B.append(-spis_stroki[1:][i] / spis_diag[1:][i])

print(round(min(min(spis_stroki_B), min(spis_diag_B)), 3), round(sum(spis_diag_B) + sum(spis_stroki_B) - 1, 3))'''][num-1]
  else:
    return [f'''
# Первое решение:\n 
            
VarName1={order}
Name2={diagstart}
name3={diagend}
d=(name3-Name2)/(VarName1-1)
listName=[Name2]
for i in range(VarName1-1):
  listName.append(listName[-1]+d)
listName=listName[2:]

VarName2=1
for i in listName:
  VarName2*=i
MatrixName=Matrix([[Name2, {a12}], [{a21}, Name2+d]])
VarName3=det(MatrixName)*VarName2

listName2=[1/i for i in listName]
MatrixName2=MatrixName.inv()

print(VarName3, trace(MatrixName2)+sum(listName2))
''',

f'''
# Второе решение:\n


dlina = {order}
a11 = {diagstart}
ann = {diagend}
a12 = {a12}
a21 = {a21}

spisochek = [i / (dlina - 1) * (ann - a11) + a11 for i in range(dlina)]
diagonal = spisochek[0] * spisochek[1] - a12 * a21
sled = (spisochek[0] + spisochek[1]) / diagonal
for i in spisochek[2:]:
  diagonal *= i
  sled += 1 / i
  
  
print(round(diagonal,3))
print(round(sled,3))
'''][num-1]
    
    
def MatrixRows(num: int, StarterMatrixName: str, symb: float, sm: int, sn: int, bm: int, lesserThan: float) -> str:
  return [f'''
Первое решение:\n
  
__MatrixName__={symb}*{StarterMatrixName}

def FunctionName1(VarName1, VarName2):
  MatrixName1=zeros(2)
  for i in range(VarName1, VarName2+1):
      MatrixName1+=__MatrixName__**i
  return MatrixName1
    
def FunctionName2(VarName3):
  return (eye(2)-__MatrixName__).inv() * __MatrixName__**VarName3

for k in range(300):
  if max(FunctionName2(k))<{lesserThan}:
    print(k)
    break
print(max(FunctionName1({sm}, {sn})), max(FunctionName2({bm})), VarName4)

# В данной задаче необходимо (В оформлении) доказать, что матрица S сходится к B.

''',
f'''
# Второе решение:\n
__MatrixName__={symb}*{StarterMatrixName}

def s(m,n):
  S = zeros(2)
  for i in range(m, n + 1):
    S += A**i
  return S
  
def b(m):
    B = ((I - A).inv()) * (A**m)
    return B
  
print(max(s({sm}, {sn})))
print(max(b({bm})))


for i in range(500):
    if max(b(i)) < {lesserThan}:
        print(i)
        break
'''][num-1]


def arifm_and_geom_matrix_progression(n: int, a11: float, a1n: float, ann: float):
  f'''
a11 = {a11}
a1n = {a1n}
vsego_symbols = {n}
ann = {ann}
q = solve(ann / x ** vsego_symbols - 1, x, minimal=True)
d = (a1n - a11) / vsego_symbols
spis_stroki = [1]
spis_diag = [1]
for i in range(vsego_symbols-1):
    spis_stroki.append(spis_stroki[-1] + d)
    spis_diag.append(spis_diag[-1] * q)

spis_stroki_B = [1]
spis_diag_B = [1]
for i in range(vsego_symbols-1):
    spis_diag_B.append(1 / spis_diag[1:][i])
    spis_stroki_B.append(-spis_stroki[1:][i] / spis_diag[1:][i])

print(round(min(min(spis_stroki_B), min(spis_diag_B)), 3), round(sum(spis_diag_B) + sum(spis_stroki_B) - 1, 3))'''

def arrayy(st: str) -> None:
  if st.lower() in '''
  решите систему уравнений В ответе укажите найденные значения неизвестных. 1) значение 2) значение 3) значение
  найдите значения переменных x,y,z,u,v,w, удовлетворяющие условиям в ответе укажите найденные значения: 1) значение ; 2) значение 
  пусть (x,y,z,u) – решение системы уравнений объясните, почему y можно представить как функцию от x вида y=a+bx, где a,b – константы, зависящие только от коэффициентов исходной системы уравнений. найдите: 1) константу a; 2) константу b
  ''':
    print('gaussian_elim(num: int = [1], __MatrixName__: str) - задания на процедуру Гаусса')
    
  elif st.lower() in '''
  найдите количество решений следующей системы уравнений при различных значениях параметра a в ответе укажите: 1) значение параметра a, при котором система имеет бесконечное число решений
  найдите количество решений следующей системы уравнений при различных значениях параметра a в ответе укажите: 1) значение параметра a, при котором система имеет единственное решение.
  ''':
    print('gaussian_elim_parameters(num: int = [1], __MatrixName__: str) - процедура Гаусса с параметрами')
  elif st.lower() in '''
  даны матрицы: произведение кронекера. найдите: 1) след матрицы c; 2) след матрицы d 
  даны матрицы: найдите: 1) максимум элементов матрицы c; 2) сумму элементов матрицы d
  ''':
    print('MatrixOps(num: int = [1], __MatrixName1__: str, __MatrixName2__: str, OPS: list["kron", если есть кронекер]) - произведение матриц, кронекера')
  elif st.lower() in '''
  даны матрицы: найдите матрицу x из уравнения axb=c. в ответе укажите: 1) след матрицы x; 2) сумму элементов матрицы x
  даны матрицы: Найдите матрицу x из уравнения ax=b. в ответе укажите: 1) наибольший элемент матрицы x; 2) сумму элементов матрицы x.
  ''':
    print('MatrixEquations(num: int = [1], name1: str, name2: str, name3: str = None) - матричные уравнения')
  elif st.lower() in '''
  даны матрицы: при каком t матрица c содержит столбец, являющийся линейной комбинацией других столбцов? 
  даны матрицы: запишите определитель матрицы m в виде многочлена ax2+bx+c. в ответе укажите: 1) значение коэффициента a; 2) значение коэффициента b.
  ''':
    print('Deter(num: int = [1], name1: str, name2: str = None) - задания про определитель')
  elif st.lower() in '''
  для каждого k обозначим ek вектор-столбец размерности n, такой, что его элемент с номером k равен 1, а все остальные элементы равны 0. Пусть σ:{1,…,n}→{1,…,n} некоторая перестановка первых n натуральных чисел. Матрица a однозначно определяется условиями: aek=eσ (k),k=1,…,n. Известно, что n= и результатом применения σ к последовательности будет следующий ряд чисел: Найдите: 1) след матрицы a6; 2) наименьшее натуральное m, такое, что след матрицы am равен
  ''':
    print('Permute(num: int = [1, 2], permName: str, index: int, btrace: int) - перестановки')
  elif st.lower() in '''
  матрица имеет размер n×n, где n=. известно, что ее диагональные элементы образуют арифметическую прогрессию с начальным элементом a1,1= и конечным элементом an,n=. Также известно, что все элементы матрицы a, расположенные вне главной диагонали, равны нулю за исключением двух элементов: a1,2= и a2,1=. Найдите: 1) определитель матрицы a; 2) след матрицы, обратной к a.
  матрица имеет размер n×n, где n=. известно, что: 1) диагональные элементы образуют геометрическую прогрессию с начальным элементом a1,1= и конечным элементом an,n=; 2) элементы первой строки образуют арифметическую прогрессию с конечным элементом a1,n=; 3) все элементы матрицы a, расположенные вне главной диагонали и вне первой строки, равны нулю. найдите обратную матрицу b=a−1 и укажите в ответе: 1) наименьший элемент матрицы b; 2) сумму элементов матрицы b.
  ''':
    print('BigMatrices(num: int = [1, 2], order: int, diagstart: float, diagend: float, a12: float = None, a21: float = None, row1end: float = None) - большие матрицы')
  elif st.lower() in '''
  даны матрицы: i= , a=, где y=. Пусть sm,n=∑ni=mai,bm=(i-a)-1am. 1) найдите наибольший элемент матрицы s=s3,90. 2) найдите наибольший элемент матрицы b=b3. 3) найдите наименьшее k, такое, что при любом n>k наибольший элемент матрицы sk,n меньше
  ''':
    print('MatrixRows(num: int = [1, 2], StarterMatrixName: str, symb: float, sm: int, sn: int, bm: int, lesserThan: float) - матричные ряды')
  elif st.lower() in '''
  пусть комплексный корень из 1 степени, такой, что его мнимая часть больше 0, а действительная часть максимальна среди подобных корней с положительной мнимой частью. даны матрицы: i=, a=. найдите определитель матрицы a+λi и укажите в ответе: 1) действительную часть этого определитля; 2) его мнимую часть
  ''':
    print('ComplexNumbers(num: int = [1, 2], index: int, MatrixName: Matrix) - комплексные числа')
  elif st.lower() in '''
  для многочлена p(x) найдите все его 11 корней: z1,…,z11∈c. в ответе укажите: 1) сумму модулей |z1|+…+|z11|; 2) действительную часть корня, у которого эта действительная часть максимальна.
  ''':
    print('Polynomials(num: int = [1], pol: any (полином вида: 2*x**11 - x**9 ...)) - многочлены')
    
  elif st.lower() in '''
  дана матрица: a=. пусть z - собственное значение матрицы a с наибольшей мнимой частью. найдите z и соответствующий этому собственному значению собственный вектор x, первая координата которого равна 1, x=(1,u,v). в ответе укажите: 1) мнимую часть z; 2) действительную часть u.
  ''':
    print('EigenValsAndVects(num: int = [1, 2], MatrixName:Matrix) - собственные значения + векторы')
    
  elif st.lower() in '''
  на двумерной координатной плоскости заданы точки: a, b и c. пусть d(x,y) - ближайшая к a точка прямой bc. Найдите точку d и расстояние r от a до d. ккажите в ответе: 1) x, первую координату точки d; 2) y, вторую координату точки d; 3) r, расстояние от a до d.
  ''':
    print('Cartesian(num: int = [1, 2], Point1: list, Point2: list, Point3: list) - 2D геометрия')
  else:
    arrayy(input())

def ComplexNumbers(num:int, index: int, MatrixName: Matrix) -> str:
  return [f'''
# Первое решение \n  

VarName1=x**{index} -1
VarName2=nroots(VarName1)
ListName1=[i for i in VarName2 if im(i)>0]
NumberName1=max(ListName1, key=lambda x: re(x))
MatrixName1={MatrixName}
VarName3=det(MatrixName1+NumberName1*eye(2))
print(re(VarName3))
print(im(VarName3))
''',
f'''
# Второе решение \n

from math import cos, sin, pi
stepen_kornya = {index}
roots = []
lambdich = []
maxcosinus = 0
A = {MatrixName}
for i in range(stepen_kornya):
    cosinus = cos(2 * i * pi / stepen_kornya)
    sinus = sin(2 * i * pi / stepen_kornya)
    if sinus > 0 and cosinus > maxcosinus:
        maxcosinus = cosinus
        lambdich = [cosinus, sinus]
lambda_matrix = eye(2)
lambda_matrix *= complex(lambdich[0], lambdich[1])
print(round((lambda_matrix + A).det(), 3))
'''][num-1]


def Polynomials(num:int, pol: any) -> str:
  return [f'''
VarName1={pol}
VarName2=nroots(VarName1)
ListName1=[abs(i) for i in VarName2]
NumberName1=max(VarName2, key=lambda x: re(x))
print(sum(ListName1))
print(re(NumberName1))
'''][num-1]


def gaussian_elim(num:int, __MatrixName__: str) -> str:
  return [f'''
  pretty_print({__MatrixName__}.rref())
  '''][num-1]

def gaussian_elim_parameters(num:int, __MatrixName__: str) -> str:
  return [f'''pretty_print({__MatrixName__}.echelon_form())
Если Необходимо решить непростое уравнение в echelon_form - функция solve() поможет.
'''][num-1]


def EigenValsAndVects(num: int, MatrixName:Matrix) -> str:
  return [f'''
# Первое решение:\n
  
__MatrixName1__={MatrixName}
NumberName1=max(list(__MatrixName1__.eigenvals().keys()), key=lambda x: im(x)).n()
VectorName=Matrix([1, x, y])
EndMatrixName=(__MatrixName1__-NumberName1*eye(3))*VectorName
solutionName=solve([EndMatrixName[0], EndMatrixName[1]])
print(im(Z))
print(re(solutionName[x]))
''',
f'''
# Второе решение:\n

A = {MatrixName}
lambda_values = A.charpoly()

Z = max(solve(lambda_values.args[0]), key=lambda x: im(x))

B = A - (Z * eye(3))
own_vector = [i.n() for i in B.nullspace()[0]]
need_to_mul = solve(own_vector[0] * x - 1, (x))[0]
new_vector_values = [simplify(i * need_to_mul) for i in own_vector]
new_vector_X = Matrix(3, 1, new_vector_values)


print(round(im(Z).n(), 3))
print(round(re(new_vector_X[1]), 3))
'''][num-1]


def Cartesian(num:int, Point1: list, Point2: list, Point3: list) -> str:
  return [f'''
# Первое решение:\n
  
PointName1=Matrix({Point1})
PointName2=Matrix({Point2})
PointName3=Matrix({Point3})
PointName4=Matrix([x, y])
LineName1=PointName3-PointName2
LineName2=PointName4-PointName1
VarName1, VarName2 = symbols('VarName1, VarName2')
__eqName1__=Eq(VarName1*PointName2[0] + VarName2, PointName2[1])
__eqName2__=Eq(VarName1*PointName3[0] + VarName2, PointName2[1])
solutionName1=solve([__eqName1__, __eqName2__])
__eqName3__=Eq(solutionName1[VarName1]*x + solutionName1[VarName2], y)
__eqName4__=Eq(LineName2.dot(LineName1), 0)
solutionName2=solve([__eqName3__, __eqName4__])
LineName2=LineName2.subs(solutionName2)
VarName3=(LineName2.dot(LineName2))**0.5
print(solutionName2[x].n())
print(solutionName2[y].n())
print(VarName3)
''',
f'''
# Второе решение:\n

A = {Point1}
B = {Point2}
C = {Point3}
urav_pryamoy_BC = ((x - B[0]) / (C[0] - B[0])) - ((y - B[1]) / (C[1] - B[1]))

tochka_x = A[0] + urav_pryamoy_BC.coeff(x) * t
tochka_y = A[1] + urav_pryamoy_BC.coeff(y) * t
t_numerical = solve(urav_pryamoy_BC.subs({{x:tochka_x, y:tochka_y}}))[0]
D = [tochka_x.subs({{t:t_numerical}}), tochka_y.subs({{t:t_numerical}})]
urav_pryamoy_BC.subs({{'x:tochka_x, y:tochka_y'}})

print(round(D[0], 3))
print(round(D[1], 3))
print(round(Point(A).distance(D), 3))
'''][num-1]
