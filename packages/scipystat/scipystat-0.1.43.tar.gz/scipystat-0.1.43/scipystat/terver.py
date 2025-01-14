import pyperclip

def z_5_1(data = 1, gamma = 1, yr_qvant = 0.9):
    data = f"'''{data}'''"
    anser = f'''
import numpy as np
import scipy.stats as sts
import matplotlib.pyplot as plt
import pandas as pd

data = {data}
gamma = {gamma}
yr_qvant = {yr_qvant}

data = data.split(sep='; ')
data_grap = data.copy()
n = len(data)
print('Объем выборки ', n)
count_NA = data.count('NA')
print('Количество NA', count_NA)
data = [i for i in data if (i != ' NA') and (i != 'NA')]
data = pd.Series([float(i) for i in data if (i != ' NA') or (i != 'NA')])
n_without = len(data)
print('Объем без NA ', n_without)

print('Минимальное значение в вариационном ряду', min(data))
print('Максимальное значение в вариационном ряду', max(data))
print('Размах выборки', max(data) - min(data))
Q1 = np.quantile(data, 0.25)
print('Значение первой квартили (Q1)', Q1)
Q2 = np.quantile(data, 0.5)
print('Значение медианы (Q2)', Q2)
Q3 = np.quantile(data, 0.75)
print('Значение третьей квартили (Q3)', Q3)
R = Q3 - Q1
print('Квартильный размах', R)
mean = data.mean()
print('Среднее выборочное значение', mean)
std_corr = data.std(ddof=1)
print('Стандартное отклонение (S) корень из дисп.в (исправленной)', std_corr)
var_corr = data.var(ddof=1)
print('Исправленная дисперсия ', var_corr)
kurt = sts.kurtosis(data, bias=False)
print('Эксцесс (формула по умолчанию в Excel)', sts.kurtosis(data, bias=False))
skew = sts.skew(data, bias=False)
print('Коэффициент асимметрии (формула по умолчанию в Excel)', skew)
error = std_corr / n_without**0.5
print('Ошибка выборки', error)
print('Значение ', yr_qvant, ' квантили', np.quantile(data, yr_qvant))
x_stat_max = Q3 + 1.5 * R
print('Верхняя граница нормы (Xst_max)', x_stat_max)
x_stat_min = Q1 - 1.5 * R
print('Нижняя граница нормы (Xst_min)', x_stat_min)
print('Количество выбросов ниже нижней нормы', len(data[data < x_stat_min]))
print('Количество выбросов выше верхней нормы', len(data[data > x_stat_max]))
print('Общее количество выбросов', len(data[(data > Q3 + 1.5 * R) | (data < Q1 - 1.5 * R)]))

interv = sts.t.interval(gamma, n - 1, mean, std_corr / np.sqrt(n_without))
print('доверительный интервал для E(X)', gamma, ' уровняя ', interv)

chi2_gamma1 = sts.chi2.ppf((1 - gamma) / 2, n_without - 1)
chi2_gamma2 = sts.chi2.ppf((1 + gamma) / 2, n_without - 1)
print('доверительный интервал для Var(X)', gamma, ' уровняя ', 
      (n_without - 1) * var_corr / chi2_gamma2, (n_without - 1) * var_corr / chi2_gamma1)

data = pd.Series([float(i.replace(',', '.')) for i in data_grap if i != 'NA'])

plt.figure(figsize=(8, 4))
plt.hist(data, bins=10, edgecolor='black')
plt.title('Гистограмма c выбросами')
plt.show()

plt.figure(figsize=(8, 4))
plt.boxplot(data, vert=True, patch_artist=True, showmeans=True)
plt.title('Диаграмма "Ящик с усиками" с выбросами')
plt.show()

data = pd.Series([i for i in data if i != np.nan])
data = data[(data < x_stat_max) & (data > x_stat_min)]

plt.figure(figsize=(8, 4))
plt.hist(data, bins=10, edgecolor='black')
plt.title('Гистограмма без выбросов и NA ')
plt.show()

plt.figure(figsize=(8, 4))
plt.boxplot(data, vert=True, patch_artist=True, showmeans=True)
plt.title('Диаграмма "Ящик с усиками" без выбросов и NA')
plt.show()
'''
    pyperclip.copy(anser)
    pyperclip.paste()

def z_5_2(data='1',alpha1 = 0.05, alpha2 = 0.05):
    data = f"'''{data}'''"
    ansver = f'''
import pandas as pd
import numpy as np
import scipy.stats as sts
import matplotlib.pyplot as plt
data = {data}
data = data.replace(' ','').replace('\\n','').split(sep = ';')
n_all = len(data)
data = np.array([i for i in data if i!= 'NA'])
uniq = np.unique(data)
print('количество различных вариантов ответов респондентов, встречающиеся в очищенной выборке',len(uniq))
n = len(data)
print('объем очищенной от "NA" выборки',n)
print('количество пропущенных данных "NA" в исходной выборке',n_all-n)
ni_obs = np.array([list(data).count(i) for i in uniq])
print('Введите количество респондентов, которые дали ответ "..."',ni_obs,uniq)
n_pi = ni_obs/np.sum(ni_obs)
print('Введите долю респондентов, которые дали ответ "..."',n_pi,uniq)
alpha = {alpha1}
z_cr = sts.norm.ppf(1-alpha/2)
print('интервал',n_pi[1] - z_cr * np.sqrt(n_pi[1]* (1 - n_pi[1]) / n), n_pi[1] + z_cr * np.sqrt(n_pi[1]* (1 - n_pi[1]) / n))
alpha = {alpha2}
chi2_cr = sts.chi2.ppf(1 - alpha, len(ni_obs)-1)
print('Введите количество степеней свободы ',len(ni_obs)-1)
print('критическое значение chi2',chi2_cr)
k = len(uniq) 
N = sum(ni_obs)
ni_exp =[N/k] * k
chi2_obs = ((ni_obs- ni_exp)**2 / ni_exp).sum()
print('Введите наблюдаемое значение хи-квадрат ',chi2_obs)
print('H0 принимается') if chi2_obs < chi2_cr else print('H1 принимается')
plt.hist(data)
plt.show()
'''
    pyperclip.copy(ansver)
    pyperclip.paste()

def z_5_3(data = 1, flag1 = '!=', alpha1 = 0.05, flag2 = '!=', alpha2 = 0.05):
    df = f"'''{data}'''"
    ansver = f'''
import pandas as pd
import scipy.stats as sts
df = {df}
df = [eval(i) for i in df.replace('\\n','').replace('NA', 'None').split(';')]
df = pd.DataFrame(df).dropna()

print('Введите выборочный коэффициент корреляции Пирсона между X и Y',sts.pearsonr(df[0],df[1]))'''

    if flag1 == '!=':
        ansver += f'''
# H0 : mu0 = mu1
# H1 : mu0 != mu1
_, p_val = sts.ttest_ind(df[0],df[1], equal_var=False, alternative='two-sided')
alpha = {alpha1}
print('принимаем H0') if p_val>alpha else print('принимаем H1')
print('p-value ',p_val)'''


    if flag1 == '<':
        ansver += f'''
# H0 : mu0 = mu1
# H1 : mu0 < mu1
_, p_val = sts.ttest_ind(df[0],df[1], equal_var=False, alternative='less')
alpha = {alpha1}
print('принимаем H0') if p_val>alpha else print('принимаем H1')
print('p-value ',p_val)'''


    if flag1 == '>' :
        ansver += f'''
# H0 : mu0 = mu1
# H1 : mu0 > mu1
alpha = {alpha1}
_, p_val = sts.ttest_ind(df[0],df[1], equal_var=False, alternative='greater')
print('принимаем H0') if p_val>alpha else print('принимаем H1')
print('p-value ',p_val)'''

    if flag2 == '!=' :
        ansver+= f'''
# H0 : sigma_x = sigma_y
# H1 : sigma_x != sigma_y

m = len(df[0])
n = len(df[1])
s2_x = df[0].var(ddof = 1)
s2_y = df[1].var(ddof = 1)
f_obs = max(s2_x,s2_y)/min(s2_x,s2_y)

if s2_x>s2_y:
    k1 = m-1
    k2 = n-1
else: 
    k1 = n-1
    k2= m-1
p_val = 2* min(sts.f.cdf(f_obs,k1,k2),sts.f.sf(f_obs,k1,k2))
alpha = {alpha2}
print('принимаем H0') if p_val>alpha else print('принимаем H1')
print('p-value ',p_val)'''


    if flag2 == '<' :
        ansver+= f'''
# H0  : sigma_x = sigma_y
# H1 : sigma_x < sigma_y

m = len(df[0])
n = len(df[1])
s2_x = df[0].var(ddof = 1)
s2_y = df[1].var(ddof = 1)
f_obs = max(s2_x,s2_y)/min(s2_x,s2_y)

if s2_x>s2_y:
    k1 = m-1
    k2 = n-1
else: 
    k1 = n-1
    k2= m-1
p_val = sts.f.sf(f_obs,k1,k2)
alpha = {alpha2}
print('принимаем H0') if p_val>alpha else print('принимаем H1')
print('p-value ',p_val)'''


    if flag2 == '>' :
        ansver+= f'''
# H0  : sigma_x = sigma_y
# H1 : sigma_x > sigma_y

m = len(df[0])
n = len(df[1])
s2_x = df[0].var(ddof = 1)
s2_y = df[1].var(ddof = 1)

f_obs = max(s2_x,s2_y)/min(s2_x,s2_y)

if s2_x>s2_y:
    k1 = m-1
    k2 = n-1
else: 
    k1 = n-1
    k2= m-1

p_val = sts.f.sf(f_obs,k1,k2)
alpha = {alpha2}
print('принимаем H0') if p_val>alpha else print('принимаем H1')
print('p-value ',p_val)'''
    pyperclip.copy(ansver)
    pyperclip.paste()

def z_2_1():
    ans = f'''
import scipy.stats as sts
import numpy as np
data = '83, 100, 100, 51, 94, 53, 17, 46, 53, 76, 88, 72, 57, 53, 70, 94, 0, 95, 0, 93, 25, 23, 87, 81, 43'
data = np.array([eval(i) for i in data.split(sep = ',')])
n=9
var = data.var(ddof=0)/n
mu3 = sts.moment(data, 3)/n**2
print('дисперсия',var)
print('центральный момент',mu3)
'''
    pyperclip.copy(ans)
    pyperclip.paste()

def z_2_2():
    ans = '''
import numpy as np
scores = np.array([46, 86, 82, 84, 70, 72, 83, 0, 0, 53, 98, 51, 66, 45, 92, 84, 92, 76, 76, 65, 88, 0, 66, 72, 70, 90])
N = len(scores)  
n = 5
mu = np.mean(scores)
sigma2 = np.var(scores, ddof=0)  
E_X_bar = mu
Var_X_bar = (sigma2 / n) * ((N - n) / (N - 1))
print(f"Математическое ожидание E(X(ср)): {E_X_bar:.3f}")
print(f"Дисперсия Var(X(ср)): {Var_X_bar:.3f}")'''
    pyperclip.copy(ans)
    pyperclip.paste()

def z_2_3():
    ans = '''
import numpy as np
ni = [2,3,4,5]
pi = [7,48,8,105]
n_prepog = 6
X = np.array([x for x, count in zip(ni, pi) for _ in range(count)])
mu = X.mean()
s = X.std() * np.sqrt((len(X) - len(X)/n_prepog)/(len(X)/n_prepog * (len(X)-1)) )
    
print('математическое ожидание = ',mu)
print('стандартное отклонение = ',s)'''
    pyperclip.copy(ans)
    pyperclip.paste()

def z_2_4():
    ans = '''
N = 36  # Общее количество уникальных комбинаций (6 красных * 6 синих)
n = 19  # Количество выбранных уникальных комбинаций

E_R = np.sum([1+2+3+4+5+6])/6
E_B = np.sum([1+2+3+4+5+6])/6
Var_R = np.sum([1+2*2+3*3+4*4+5*5+6*6])/6 - (np.sum([1+2+3+4+5+6])/6)**2
Var_B = np.sum([1+2*2+3*3+4*4+5*5+6*6])/6 - (np.sum([1+2+3+4+5+6])/6)**2
# из функции
a = 11
b = -8
E_X = a * E_R + b * E_B
print(f"Математическое ожидание E(X̄): {E_X}")

Var_X = a**2 * Var_R + b**2 * Var_B
print(f"Дисперсия Var(X): {Var_X}")

Var_X_bar = (1 / n) * ((N - n) / (N - 1)) * Var_X
print(f"Дисперсия Var(X̄): {Var_X_bar}")

sigma_X_bar = np.sqrt(Var_X_bar)
print(f"Стандартное отклонение σ(X̄): {sigma_X_bar}")'''
    pyperclip.copy(ans)
    pyperclip.paste()

def z_2_5():
    ans = '''
import scipy.stats as sts
n_coins = 11
n_comb = 257
X = sts.binom(n_coins,1/2)
N = 2**n_coins    
print('математическое ожидание ',n_coins/2)
print('дисперсия ',X.var() /n_comb * (N-n_comb)/(N-1))'''
    pyperclip.copy(ans)
    pyperclip.paste()

def z_2_6():
    ans = '''
import numpy as np
import pandas as pd

n = 7
data = {
    "X": [100,100,100,400,400,400],
    "Y": [1,2,3,1,2,3],
    "f": [11,32,11,24,11,11]
}

df = pd.DataFrame(data)

N = df["f"].sum()

E_X = (df["X"] * df["f"]).sum() / N
E_Y = (df["Y"] * df["f"]).sum() / N

Var_X = ((df["X"] - E_X)**2 * df["f"]).sum() / N
Var_Y = ((df["Y"] - E_Y)**2 * df["f"]).sum() / N

Cov_XY = ((df["X"] - E_X) * (df["Y"] - E_Y) * df["f"]).sum() / N

Var_X_bar = (1 / n) * ((N - n) / (N - 1)) * Var_X
Var_Y_bar = (1 / n) * ((N - n) / (N - 1)) * Var_Y

r_XY = Cov_XY / np.sqrt(Var_X * Var_Y)

print("Математическое ожидание", E_X)
print("Дисперсия", Var_Y_bar)
print("Коэффициент корреляции", r_XY)'''
    pyperclip.copy(ans)
    pyperclip.paste()

def z_2_7():
    ans = '''
import numpy as np
import pandas as pd
n = 6
data = {
    "X": [100,100,100,400,400,400],
    "Y": [1,2,3,1,2,3],
    "f": [11,32,11,24,11,11]
}
df = pd.DataFrame(data)
N = df["f"].sum()

E_X = (df["X"] * df["f"]).sum() / N
E_Y = (df["Y"] * df["f"]).sum() / N
E_XY = (df["Y"] * df["f"] * df["X"]).sum() / N

var_X = ((df["X"] - E_X)**2 * df["f"]).sum() / N
var_Y = ((df["Y"] - E_Y)**2 * df["f"]).sum() / N

cov_XY = E_XY - E_X*E_Y

sigma_X_bar = np.sqrt((1 / n) * ((N - n) / (N - 1)) * var_X)

cov_X_bar_Y_bar = (1 / n) * ((N - n) / (N - 1)) * cov_XY
print("математическое ожидание", E_Y)
print("стандартное отклонение", sigma_X_bar)
print("ковариация", cov_X_bar_Y_bar)'''
    pyperclip.copy(ans)
    pyperclip.paste()

def gip_sr_1():
    ans = '''
import numpy as np
from scipy.stats import norm
data = '0,189; -0,66; 0,218; -0,828; -0,65; 0,814; 2,846; 6,009; 1,634; -3,487; 1,606; -1,147; 0,615; 2,491; -1,091; 2,202; -1,503; 3,921; 2,095; -2,205; 3,671; -1,27; 6,15; 5,291; -2,73'
data = list(map(float,data.replace(',','.').split('; ')))
n = len(data)                  
mu0 = 1.22                      
alpha = 0.08                   
sigma = 2.7                   
sample_mean = np.mean(data)
standard_error = sigma / np.sqrt(n)
Z_obs = (sample_mean - mu0) / standard_error

print(f"1) Значение статистики критерия Z_obs: {Z_obs:.4f}")

alpha_half = alpha / 2          
A = norm.ppf(1 - alpha_half)   

print(f"2) Граница A критического множества: {A:.4f}")
p_value = 2 * (1 - norm.cdf(abs(Z_obs)))  

print(f"3) P-значение критерия: {p_value:.4f}")

if p_value < alpha:
    print("Вывод: Отвергаем основную гипотезу H0.")
else:
    print("Вывод: Нет оснований отвергать основную гипотезу H0.")
mu1 = 1.03                            
delta = (mu1 - mu0) / standard_error     
W = norm.cdf(-A + delta) + (1 - norm.cdf(A + delta))

print(f"4) Мощность критерия W при μ = {mu1}: {W:.4f}")'''
    pyperclip.copy(ans)
    pyperclip.paste()

def gip_sr_2():
    ans = '''
import numpy as np
from scipy import stats
data = '1,146; 2,958; -3,325; -0,534; 0,374; 5,293; 0,12; 1,185; 5,148; 5,351; 2,639; 1,47; -1,967; 4,96; 6,057; -0,542; 1,544; -0,243; -1,988; 2,844'
data = list(map(float,data.replace(',','.').split('; ')))
n = len(data)                     
mu0 = 1.10                        
alpha = 0.05                      
sample_mean = np.mean(data)
sample_std = np.std(data, ddof=1) 
standard_error = sample_std / np.sqrt(n)
t_stat = (sample_mean - mu0) / standard_error

print(f"1) Значение статистики критерия t = {t_stat:.4f}")
df = n - 1
alpha_half = alpha / 2
A = stats.t.ppf(1 - alpha_half, df)

print(f"2) Граница A критического множества: {A:.4f}")

p_value = 2 * stats.t.sf(np.abs(t_stat), df)

print(f"3) P-значение критерия: {p_value:.4f}")

if p_value < alpha:
    print("Вывод: Отвергаем основную гипотезу H0.")
else:
    print("Вывод: Нет оснований отвергать основную гипотезу H0.")

mu1 = 0.91

delta = (mu1 - mu0) / (sample_std / np.sqrt(n))
left_tail = stats.nct.cdf(-A, df, delta)
right_tail = 1 - stats.nct.cdf(A, df, delta)
W = left_tail + right_tail

print(f"4) Мощность критерия W при μ = {mu1}: {W:.4f}")'''
    pyperclip.copy(ans)
    pyperclip.paste()

def gip_3_sr():
    print('''Для трех групп финансовых показателей A: (X1;...;X20), B: (Y1;...;Y21), C: (Z1;...;Z22), которые по предположению независимы и распределены, соответственно, по трем нормальным законам N(μx,σ2), N(μy,σ2), N(μz,σ2) (с одинаковой неизвестной дисперсией σ2) на уровне значимости α=0,04 с помощью F-критерия (Фишера) проверяется гипотеза H0:μx=μy=μz о совпадении ожидаемых значений показателей. Конкретные значения всех показателей указаны ниже. 1) По данным значениям показателей найдите межгрупповую дисперсию. 2) По этим же данным найдите среднюю групповую дисперсию. 3) Найдите значение статистики F-критерия, критическое множество Kα и проверьте гипотезу H0. 4) Найдите P-значение критерия и сделайте выводы.
Значения показателей группы A: (3,645; 6,926; 5,956; -1,441; 3,57; 0,706; 0,832; 2,168; 1,475; 4,881; 3,079; 1,416; 2,254; 1,968; 4,985; 0,567; 1,914; -1,121; -5,538; 2,799). Значения показателей группы B: (3,348; -0,83; 7,001; -2,681; 1,219; 0,613; 5,085; 4,92; 1,503; 2,083; -1,208; -4,05; 0,195; 1,507; 4,299; 4,226; 0,093; 0,314; -1,626; -2,592; -3,336). Значения показателей группы C: (6,172; -0,225; -0,039; -2,157; 3,121; -3,096; 0,547; -1,228; 2,106; -0,228; -1,97; 1,027; 2,214; 1,273; 1,886; -0,549; 0,157; -0,648; 0,165; -1,014; -3,388; 1,561).''')
    ans = '''
k = 3
A = np.array([])

B = np.array([])

C = np.array([])

n1,n2,n3 = len(A),len(B),len(C)

ni = np.array((n1,n2,n3))
n = ni.sum()

Gr_sr = np.array((A.mean(),B.mean(),C.mean()))
Gr_var = np.array((A.var(),B.var(),C.var()))
all_sr = np.dot(Gr_sr,ni)/n

delta2 = np.dot((Gr_sr - all_sr)**2,ni)/n 

sigma2_sr = np.dot(Gr_var,ni)/n 

sigma2 =sigma2_sr + delta2
    
MSA = n * delta2 /(k-1)
MSW = n *sigma2_sr/(n - k)
MST = n * sigma2 / (n-1)

F_obs =  MSA/MSW

F_cr = sts.f.ppf(1 - alpha, k-1, n-k)
p_val = sts.f.sf(F_obs,k-1,n-k)
print('Межгрупповая дисперсия ',delta2)
print('Средняя групповая дисперсия ',sigma2_sr)
print('P-значение критерия ',p_val)
print('Значение статистики критерия ',F_obs)'''
    pyperclip.copy(ans)
    pyperclip.paste()

def gip_var_1():
    ans = '''
import numpy as np
from scipy.stats import chi2
data = '0,185; 1,269; 2,034; 1,356; 2,498; -0,185; 1,665; 0,436; 0,226; 0,556; 0,858; 1,273; -0,107; 2,228; 1,736; -0,526; 2,892; 3,352; 2,542; 1,007; 0,0; 2,402; 0,754; 2,591; 1,445; 2,314; 1,613; 2,008; 1,222; 3,228; 1,353; 1,664; 3,338; -0,313; -0,226; 2,305; -0,116; 3,406; 0,743; 0,365; 3,383; 2,883; 3,32; 2,234; 0,237'
data = np.array(list(map(float,data.replace(',','.').split('; '))))
n = len(data)
mu = 1.83
sigma0 = 1.13 

deviations = data - mu
sum_of_squares = np.sum(deviations ** 2)
chi_square_stat = sum_of_squares / sigma0 ** 2

print("1) Значение статистики критерия =", round(chi_square_stat, 4))

alpha = 0.03
df = n  
A = chi2.ppf(alpha / 2, df )
B = chi2.ppf(1 - alpha / 2, df)

print("2) Границы критического множества: A =", round(A, 4), "и B =", round(B, 4))

if chi_square_stat < A or chi_square_stat > B:
    decision = "Отвергаем H0"
else:
    decision = "Не отвергаем H0"

print("Решение:", decision)
p_value = 2 * min(chi2.cdf(chi_square_stat, df), 1 - chi2.cdf(chi_square_stat, df))

print("3) P-значение критерия =", round(p_value, 4))
sigma_1 = 1.23
sigma1_squared = sigma_1 ** 2
sigma0_squared = sigma0 ** 2
factor = sigma1_squared / sigma0_squared
c1 = A * factor
c2 = B * factor
beta = chi2.cdf(B, df=n, scale=sigma_1**2 / sigma0**2) - chi2.cdf(A, df=n, scale=sigma_1**2 / sigma0**2)
print("4) Вероятность ошибки второго рода =", round(beta, 4))'''
    pyperclip.copy(ans)
    pyperclip.paste()

def gip_var_2():
    ans = '''
import numpy as np
from scipy.stats import chi2

# Данные
x = np.array([])
n = len(x)  # Объем выборки
sigma_0 = 1.13  # Проверяемое значение стандартного отклонения
alpha = 0.03  # Уровень значимости

# 1. Найти значение статистики критерия χ^2
S2 = np.var(x, ddof=1)  # Выборочная дисперсия
chi2_stat = (n - 1) * S2 / sigma_0**2

# 2. Найти границы A и B критического множества
A = chi2.ppf(alpha / 2, df=n-1)  # Левая критическая граница
B = chi2.ppf(1 - alpha / 2, df=n-1)  # Правая критическая граница

# Проверка гипотезы H0
reject_H0 = chi2_stat < A or chi2_stat > B

# 3. Найти p-значение критерия
p_value = 2 * min(chi2.cdf(chi2_stat, df=n-1), 1 - chi2.cdf(chi2_stat, df=n-1))

# 4. Найти вероятность ошибки второго рода β для σ1 = 1.24
sigma_1 = 1.23
noncentral_chi2_stat = (n - 1) * sigma_1**2 / sigma_0**2

beta = chi2.cdf(B, df=n-1, scale=sigma_1**2 / sigma_0**2) - chi2.cdf(A, df=n-1, scale=sigma_1**2 / sigma_0**2)

# Вывод результатов
print(f"1. Значение статистики критерия χ^2: {chi2_stat:.4f}")
print(f"2. Границы критического множества: A = {A:.4f}, B = {B:.4f}")
print(f"Гипотеза H0 {'отвергается' if reject_H0 else 'не отвергается'}")
print(f"3. P-значение: {p_value:.4f}")
print(f"4. Вероятность ошибки второго рода β: {beta:.4f}")'''
    pyperclip.copy(ans)
    pyperclip.paste()

def dov_int_ro():
    print('надо условие сюда')
    ans = '''
import numpy as np
from scipy.stats import norm

# Данные
x = np.array([])
y = np.array([])

n = len(x)

# 1. Вычисление выборочного коэффициента корреляции
r_hat = np.corrcoef(x, y)[0, 1]

# 2. Преобразование Фишера
z_hat = 0.5 * np.log((1 + r_hat) / (1 - r_hat))

# 3. Стандартная ошибка
SE = 1/np.sqrt(n - 3)

# 4. Критическое значение для уровня 0.93
alpha = 1 - 0.93
z_critical = norm.ppf(1 - alpha/2)  # z_{0.965}

# 5. Доверительный интервал для z
z_lower = z_hat - z_critical * SE
z_upper = z_hat + z_critical * SE

# 6. Обратное преобразование Фишера для границ доверительного интервала
def fisher_inverse(z):
    return (np.exp(2*z) - 1) / (np.exp(2*z) + 1)

rho_lower = fisher_inverse(z_lower)
rho_upper = fisher_inverse(z_upper)

# Вывод результатов
print(f"1) Выборочный коэффициент корреляции ρ̂: {r_hat:.4f}")
print(f"2) Верхняя граница доверительного интервала θ̂₂ для ρ: {rho_upper:.4f}")'''
    pyperclip.copy(ans)
    pyperclip.paste()

def gip_2_sr():
    print('''
    1. Пусть x⃗ =(x1,…,x25) – реализация случайной выборки X⃗ =(X1,…,X25) из нормального распределения N(μx;0,72), а y⃗ =(y1,…,y30) – реализация случайной выборки Y⃗ =(Y1,…,Y30) из нормального распределения N(μy;1,42). Известно, что X⃗  и Y⃗  независимы. Проверяется гипотеза H0:μx=μy против альтернативной гипотезы H1:μx>μy. При уровне значимости α применяется критерий с критической областью {Z>A}, где статистика критерия Z=Z(X⃗ ,Y⃗ ) – это нормированная разность X¯−Y¯, A=Aα – зависящее от α критическое значение. Соответствующее критическое множество имеет вид Kα=(Aα;∞). 1) Найдите значение статистики критерия Zнабл.=Z(x⃗ ,y⃗ ). 2) Найдите P-значение критерия. 3) Найдите критическое значение A, критическое множество Kα и проверьте гипотезу H0 при α=0,02. 4) Найдите мощность критерия W в случае μx−μy=0,1 и α=0,02. Исходные данные: x⃗ = (3,842; 3,374; 4,18; 4,5; 4,247; 4,412; 3,756; 3,946; 3,729; 3,948; 3,631; 2,992; 4,324; 3,919; 3,059; 4,524; 3,565; 4,236; 4,71; 4,29; 4,998; 3,336; 4,482; 3,721; 3,59); y⃗ = (3,19; 3,564; 4,079; 2,369; 5,261; 4,652; 1,849; 6,084; 6,654; 5,65; 3,748; 2,501; 5,476; 3,436; 5,711; 4,292; 5,367; 4,499; 4,989; 4,015; 6,5; 4,178; 4,563; 6,636; 2,113; 2,221; 5,357; 2,358; 6,721; 3,421).
    ''')
    ans = '''
import scipy.stats as sts
import numpy as np
X = ''''''
Y = ''''''
sigma_x = 1.1
sigma_y = 1.3
alpha = 0.03
# mu_x - mu_y = delt
delt = 0.7
X = np.array([eval(i) for i in X.replace(',','.').split(sep = ';')])
Y = np.array([eval(i) for i in Y.replace(',','.').split(sep = ';')])
x_sr = X.mean()
y_sr = Y.mean()
m = len(X)
n = len(Y)


z_crit = sts.norm.ppf(1 - alpha)

z_obs = (x_sr - y_sr)/(sigma_x**2/m + sigma_y**2/n)**0.5

p_value = 1 - sts.norm.cdf(z_obs)

z_alt = delt / np.sqrt((sigma_x**2 / m) + (sigma_y**2 / n))
w = 1 - sts.norm.cdf(z_crit - z_alt)

print('Критическое значение A ', z_crit)
print('Мощность критерия ', w)
print('Значение статистики критерия ', z_obs)
print('P-значение критерия ', p_value)
'''
    pyperclip.copy(ans)
    pyperclip.paste()


