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

