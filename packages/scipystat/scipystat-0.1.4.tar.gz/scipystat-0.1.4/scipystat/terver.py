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

def z_5():
    print(f'''
1) Независимые наблюдения нормально распределенной случайной величины X, описывающей
приращение стоимости акций некоторой компании, представлены в виде выборки (campus.fa.ru).
Скопируйте и преобразуйте в столбец "A" данные выборки на лист "Лист1" Excel-файла и,
используя Excel, очистите исходную выборку от пропусков "NA", преобразуйте её в
вариационный ряд. Для полученного ряда вычислите требуемые далее величины: количество
пропущенных значений в исходной выборке, обозначенные как "NA"; объем очищенной от
пропусков выборки; среднее значение; стандартное отклонение (исправленное); несмещенную
дисперсию; первую и третью квартиль; медиану; максимальное и минимальное значение в
вариационном ряду; размах выборки; исправленный эксцесс и коэффициент асимметрии
(формулы по умолчанию в Excel); значение ошибки выборки; границы 0.95-доверительного
интервала для E(X) и Var(X); количество выбросов выше и ниже нормы. Постройте на листе
"Лист1" гистограмму и диаграмму "ящик с усиками" для исходной выборки, очищенной от "NA"
и выбросов.

z_5_1(data, gamma, yr_qvant)

2) По результатам социологического исследования ответы респондентов на определенный
вопрос анкеты представлены в виде выборки (campus.fa.ru). Скопируйте и преобразуйте в столбец
"A" данные выборки на лист "Лист1" Excel-файла. Используя Excel, очистите выборку от
пропусков, обозначенных как "NA", и вычислите требуемые далее величины: количество
различных вариантов ответов респондентов, встречающиеся в очищенной выборке; объем
очищенной от "NA" выборки; количество пропущенных данных "NA" в исходной выборке; доля
респондентов, которые дали ответ "M"; границs 0.95-доверительного интервала для истинной
доли ответов "M". На уровне значимости 0.1 проверьте критерием согласия (Хи-квадрат
критерием Пирсона) гипотезу о равновероятном распределении ответов респондентов.
Вычислите количество степеней свободы, критическое значение статистики хи-квадрат и
наблюдаемое значение хи-квадрат. Сделайте вывод: есть ли основания отвергнуть гипотезу о
равновероятном распределении ответов. Постройте на листе "Лист2" гистограмму для исходной
выборки, очищенной от "NA".

z_5_2(data='1',alpha1 = 0.05, alpha2 = 0.05)

3) Ряд совместных наблюдений независимых нормально распределенных случайных величин X
и Y, описывающих некоторый финансовый показатель двух фирм, задан двумерной выборкой
(campus.fa.ru). Скопируйте данную выборку на лист "Лист3" и преобразуйте ее в столбцы "A" и
"B" соответственно для первой и второй фирмы. При этом связанные значения показателей
должны располагаться в одной строке. Используя Excel, очистите исходную выборку от
пропущенных данных, обозначенных как "NA", и вычислите требуемые далее величины:
выборочный коэффициент корреляции Пирсона между X и Y; значение P-value в проверке
гипотезы о равенстве средних значений показателей фирм при альтернативной гипотезе об их
неравенстве (без каких-либо предположений о равенстве дисперсий); значение P-value в проверке
гипотезы о равенстве дисперсий показателей двух фирм при альтернативной гипотезе об их
неравенстве. Сделайте выводы: На уровне значимости 0.05 можно ли утверждать, что средние
значения показателей у фирм различны? На уровне значимости 0.05 можно ли утверждать, что
дисперсии показателей фирм различны?

z_5_3(data, flag1, alpha1, flag2, alpha2)
''')

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
