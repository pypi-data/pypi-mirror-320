def imports():
    """import numpy as np
from scipy.stats import *
import pandas as pd
import matplotlib.pyplot as plt
from scipy.integrate import quad
from scipy.integrate import dblquad
from sympy import *"""

def num51():
    """## 5.1

# 1
data_old = 'L2; L2; L2; L1; L3; L3; L3; L1; L1; L2; NA; L1; L2; L1; NA; L1; L1; L2; L1; L2; NA; L1; L1; L2; L3; L2; L1; NA; L1; L2; L2; L1; L3; L2; L1; L2; L3; L1; L1; L1; L1; L2; L1; NA; L1; NA; L2; L3; L2; L2; L2; L1; L1; L2; L1; L1; NA; L3; L1; L2; L1; L2; L1; NA; L3; L1; L2; L1; L3; L2; L2; L1; L1; NA; L2; L1; L2; L3; L1; L1; L2; L3; L3; L3; L1; L3; L3; L2; L1; L2; L2; L2; L2; L1; L3; L2; NA; L2; L1; L2; NA; L1; NA; L1; L3; L2; L3; L1; NA; L3; NA; L2; NA; NA; NA; L2; L3; L1; L1; L1; L3; L3; L2; L3; L2; L2; NA; L3; NA; L1; L3; L2; L3; L2; L2; L3; L2; NA; L3; L2; L1; L1; NA; L2; L2; L1; L3; L3; L2; L1; L1; L2; L3; L2; L1; L2; L2; L1; NA; L2; L1; L2; L1; NA; NA; L3; NA; L2; L3; NA; NA; L2; L2; L2; L1; L2; L2; L3; L3; L2; L2; NA; L1; L2; L1; L1; L2; L2; L2; L2; L2; L1; L1; L2; L1; L2; L2; L3; L2; NA; NA; L2; L1; L1; L2; L3; L1; L1; L1; L3; L2; L1; L1; L3; L1; NA; L2; L3; L3; L2; L3; L3; L2; L3; L2; L2; L2; L2; NA; L3; L2; L2; L3; L3; L3; L2; L1; NA; NA; L2; L2; L3; L2; L2; L2; L2; L2; L2; L3; L2; L1; L2; L3; NA; NA; L1; L2; L3; L3; L2; L1; NA; L2; L2; L2; L2; L2; L3; L1; L3; NA; L2; L1; L1; L1; L3; L2; L1; L1; L3; L1; L3; NA; L3; L1; L2; L2; L2; L1; L2; L2; L2; L3; L2; L2; L2; L2; L3; L2; L3; NA; L2; NA; L3; L2; L1; L1; L1; NA; L2; L1; NA; L2; NA; L1; L2; L2; L2; L2; L2'
data = data_old.replace('NA; ', '').split('; ')
num_unique_answers = len(set(data))
print(f"1. Введите количество различных вариантов ответов респондентов, встречающиеся в очищенной выборке {num_unique_answers}")

# 2
n_clean = len(data)
print(f'2. Введите объем очищенной от "NA" выборки {n_clean}')

# 3
print(f'3. Введите количество пропущенных данных "NA" в исходной выборке {data_old.count("NA")}')

# 4
proportion_f = data.count("L2") / len(data)
print(f'4. Введите долю респондентов, которые дали ответ "Four" {proportion_f})')

# 5
z_99 = 2.576  # Z-значение для 99%-го доверительного интервала
# z_90 = 1.645
# z_95 = 1.96
# z_99 = 2.576
error_margin = z_99 * np.sqrt(proportion_f * (1 - proportion_f) / n_clean)
upper_bound = proportion_f + error_margin
print("5. Правая граница 99%-го доверительного интервала для доли 'L2':", upper_bound)

# 6
lower_bound = proportion_f - error_margin
print("6. Левая граница 99%-го доверительного интервала для доли 'L2':", lower_bound)

# 8
df = num_unique_answers - 1
print("8. Количество степеней свободы:", df)

# 7
chi_critical = chi2.ppf(0.99, df) # На уровне значимости 0.01
print("7. Критическое значение статистики хи-квадрат:", chi_critical)

# 9
observed_counts = pd.Series(data).value_counts().values
expected_counts = [n_clean / num_unique_answers] * num_unique_answers
chi_squared = sum((observed_counts - expected_counts) ** 2 / expected_counts)
print("9. Наблюдаемое значение хи-квадрат:", chi_squared)

# 10
reject_hypothesis = int(chi_squared > chi_critical)
print("10. Отвергается ли гипотеза о равновероятном распределении? (1 - да, 0 - нет):", reject_hypothesis)

# 11 - гистограмма
plt.figure(figsize=(10, 6))
pd.Series(data).value_counts().plot(kind='bar', color='skyblue', edgecolor='black')
plt.title("Гистограмма для очищенной выборки", fontsize=16)
plt.xlabel("Ответы", fontsize=12)
plt.ylabel("Частота", fontsize=12)
plt.xticks(rotation=0)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()"""

def num52():
    """# 5.2

# Исходные данные
data_old = '206.369; 208.157; 133.424; NA; 205.983; 175.193; 170.905; 150.949; 188.806; 165.025; NA; 133.842; 165.418; 159.939; 166.963; 177.326; 192.664; 177.554; 167.226; 151.958; 169.303; 169.447; NA; NA; 133.502; 155.825; 124.861; NA; 159.725; 144.353; 181.489; NA; 178.939; 152.91; NA; NA; 160.405; 192.797; NA; 189.444; 177.315; 201.411; 167.953; 141.539; NA; 191.113; NA; 163.899; 39.04225; 157.948; 217.112; 170.452; 177.438; 168.106; 125.031; 167.66; 116.091; 138.596; 152.05; 184.279; NA; 154.124; 182.121; 117.519; 152.717; 181.611; 180.755; 149.823; 181.811; 184.284; 176.162; NA; 142.698; 153.022; 164.028; 185.367; 158.815; 168.493; 170.562; 158.54; 180.97; 159.19; 152.207; 147.214; 167.93; 158.415; 198.106; 148.451; 154.121; 161.832; 108.537; 143.366; 164.972; 177.881; NA; 263.84175; 195.88; 141.228; 160.386; 134.649; 169.224; 126.416; 174.525; 170.31; 176.095; 128.244; 146.315; 152.884; NA; 174.807; 138.284; 188.477; 175.793; 183.801; 160.441; 221.43; 146.247; 69.924; 149.882; 166.204; 175.895; 165.074; 186.8; 136.091; 153.276; 133.551; 219.683; NA; NA; NA; 183.381; 170.075; 170.351; 181.388; 154.638; 143.753; 156.614; 122.162; 227.82; 145.923; 148.569; 168.591; 170.114; 176.304; 291.586; 162.43; 177.87; 156.656; 185.544; 181.392; 178.111; 133.455; NA; 176.59; 194.207; 189.53; 186.943; 194.099; 147.297; 157.708; 194.889; 129.903; 187.555; 164.758; 189.037; 146.204; 155.568; 192.353; 193.882; NA; 180.307; 143.942; 205.744; NA; 177.082; 122.171; 130.29; NA; 138.433; 159.228; 150.947; 151.182; 178.227; 186.135; 123.018; 163.292; 167.882; 170.091; NA; 128.712; 188.431; 158.965; 147.104; 152.171; 199.208; NA; 132.673; NA; 109.958; 146.972; 138.278; 171.939; 152.572; 114.973; 138.909; 173.88; 168.185; NA; NA; 171.359; 171.811; 167.161; 149.089; 158.741; 157.529; 215.589; 115.954; 170.654; NA; 114.889; 157.129; 198.889; 136.875; 161.253; 129.793; 173.823; 132.632; 208.427; NA; 196.843; 149.543; 165.311; 136.66; 149.271; 160.539; 171.746; 144.282; NA; NA; 165.887; NA; 101.81; 172.648; 209.675; 127.283; 191.889; 159.258; 153.896; 179.672; 144.206; NA; 125.339; 166.822; 185.79; 164.901; 186.227; 185.246; 139.061; 323.252; 147.884; 148.375; 170.103; 136.64; 208.728; 199.571; 204.467; 153.097; 155.101; 151.42; 156.641; 166.24; 118.352; 168.1; 195.179; 158.711; 166.27; 152.106; NA; 171.696; 190.565; NA; 149.561; NA; 174.242; NA; 137.165; 172.907; 175.011; 197.128; 192.695'

# 1. Количество пропущенных значений
na_count = data_old.count('NA')
print(f'1. Количество пропущенных значений: {na_count}')

# Очистка данных от пропусков
data = data_old.replace('NA', 'nan').split(';')  # Заменяем 'NA' на 'nan'
data_new = np.array([float(x.strip()) for x in data if x.strip() != 'nan'])  # Удаляем пропуски и преобразуем в числа

# 2. Объем очищенной выборки
cleaned_count = len(data_new)
print(f'2. Объем очищенной выборки: {cleaned_count}')

# 3. Среднее значение
mean_value = np.mean(data_new)
print(f'3. Среднее значение: {mean_value}')

# 4. Стандартное отклонение (исправленное)
std_value = np.std(data_new, ddof=1)
print(f'4. Стандартное отклонение: {std_value}')

# 5. Несмещенная дисперсия
variance_value = np.var(data_new, ddof=1)
print(f'5. Несмещенная дисперсия: {variance_value}')

# 6. Первая квартиль (Q1)
q1_value = np.percentile(data_new, 25)
print(f'6. Первая квартиль: {q1_value}')

# 7. Третья квартиль (Q3)
q3_value = np.percentile(data_new, 75)
print(f'7. Третья квартиль: {q3_value}')

# 8. Медиана
median_value = np.median(data_new)
print(f'8. Медиана: {median_value}')

# 9. Максимальное значение
max_value = np.max(data_new)
print(f'9. Максимальное значение: {max_value}')

# 10. Минимальное значение
min_value = np.min(data_new)
print(f'10. Минимальное значение: {min_value}')

# 11. Размах выборки
range_value = max_value - min_value
print(f'11. Размах выборки: {range_value}')

# 12. Эксцесс
kurtosis_value = kurtosis(data_new, bias=False)
print(f'12. Эксцесс: {kurtosis_value}')

# 13. Коэффициент асимметрии
skewness_value = skew(data_new)
print(f'13. Коэффициент асимметрии: {skewness_value}')

# 14. Ошибка выборки (стандартная ошибка среднего)
sem_value = sem(data_new)
print(f'14. Ошибка выборки: {sem_value}')

# 15-16. 95%-доверительный интервал для E(X)
confidence_interval = t.interval(0.95, len(data_new)-1, loc=mean_value, scale=sem_value)
print(f'15. Левая граница 95%-доверительного интервала для E(X): {confidence_interval[0]}')
print(f'16. Правая граница 95%-доверительного интервала для E(X): {confidence_interval[1]}')

# 17-18. 95%-доверительный интервал для Var(X)
chi2_lower = chi2.ppf(0.975, len(data_new)-1)
# для 90%: 0.95
# для 99%:  0.995
chi2_upper = chi2.ppf(0.025, len(data_new)-1)
# для 90%: 0.05
# для 99%: 0.005
ci_var_lower = (len(data_new) - 1) * variance_value / chi2_lower
ci_var_upper = (len(data_new) - 1) * variance_value / chi2_upper
print(f'17. Левая граница 95%-доверительного интервала для Var(X): {ci_var_lower}')
print(f'18. Правая граница 95%-доверительного интервала для Var(X): {ci_var_upper}')

# 19-20. Количество выбросов (по правилу 1.5 * IQR)
iqr = q3_value - q1_value
lower_bound = q1_value - 1.5 * iqr
upper_bound = q3_value + 1.5 * iqr
outliers_lower = len(data_new[data_new < lower_bound])
outliers_upper = len(data_new[data_new > upper_bound])
print(f'19. Количество выбросов ниже нормы: {outliers_lower}')
print(f'20. Количество выбросов выше нормы: {outliers_upper}')

# 21
# график 1
cleaned_data = data_new[(data_new >= lower_bound) & (data_new <= upper_bound)]
plt.figure(figsize=(12, 8))
plt.boxplot(cleaned_data)
plt.show()
# график 2
plt.hist(cleaned_data, bins=10, color='orange', alpha=0.7)
plt.show()

# допы:
Q1 = np.quantile(data_new, 0.25)
Q2 = np.quantile(data_new, 0.5)
Q3 = np.quantile(data_new, 0.75)
RQ = Q3 - Q1

st_max = Q3 + 1.5 * RQ
st_min = Q1 - 1.5 * RQ

f"19. Введите нижнюю границу нормы: {st_min}. 20. Введите верхнюю границу нормы: {st_max}\""""

def num53():
    """## 5.3

# 1
data = '(192.535, 268); (259.476, 216.4); (200.788, NA); (212.875, 224.3); (155.587, 186.9); (211.361, 174.9); (229.93, 255.6); (NA, 260); (211.41, 236.7); (263.296, 263.1); (200.147, 240); (231.161, 175.7); (235.885, 214.9); (NA, 259.1); (NA, 187.8); (134.123, 220.6); (213.608, 253.6); (225.689, NA); (202.889, 166.3); (246.978, 215.6); (180.788, 241.2); (NA, 218.3); (277.288, 185.2); (172.021, 177.5); (169.985, 245.2); (201.641, 189.5); (233.882, 197.7); (201.334, 220.2); (150.806, 192.2); (NA, 222.3); (172.528, 218.3); (204.581, 210.7); (256.693, 193.9); (205.555, 195.8); (266.668, 240.8); (221.539, 255.7); (211.897, 189.1); (217.566, 164.2); (189.411, NA); (234.746, 257.1); (196.854, 248.7); (212.411, 173.4); (213.035, 245); (255.89, 209.8); (217.797, 183.8); (176.479, 224.2); (221.081, 239.6); (244.333, 201.3); (181.463, 184.3); (154.768, 182.5); (184.385, 271.1); (226.954, 181.9); (249.209, 199.3); (199.683, 226.6); (NA, 241.1); (NA, 224.1); (271.298, 200.7); (202.962, NA); (195.659, 206.6); (208.262, 186.4); (220.927, 257.6); (207.178, 190.1); (187.436, 242.7); (209.902, NA); (162.677, 225.1); (238.061, NA); (NA, 258.4); (185.012, 158.3); (209.515, 234.3); (195.94, 202.7); (245.422, 208.5); (209.15, 212); (182.148, 217.2); (190.21, 181.6); (NA, 212.1); (203.297, 196.3); (235.701, 221.6); (256.118, 229.6); (185.102, 227.5); (251.268, 192.8); (144.612, 160.6); (229.033, NA); (184.285, NA); (221.844, 218.2); (188.502, NA); (237.296, 204.7); (198.662, 253); (234.746, 185.8); (191.385, 199.8); (198.221, 220.7); (202.43, 185.9); (170.753, 222.1); (173.744, 270.8); (NA, 177.5); (158.337, 206.7); (194.209, 189.3); (153.225, 243.3); (223.666, 179.8); (172.476, 192.4); (210.025, 243); (249.269, 194.6); (233.658, 244.2); (238.985, 200.2); (226.416, 147.4); (181.726, 198.9); (217.899, 213.6); (244.965, 262.2); (210.466, 206.5); (238.59, 192.3); (166.985, 194.1); (238.103, 216); (197.04, 209.1); (177.859, NA); (165.441, 250.2); (NA, 135.1); (208.004, 196.9); (205.035, 232.1); (218.992, 227.7); (206.353, 207.9); (259.291, 231.5); (159.835, 178.3); (242.361, 213.1); (212.803, 234.5); (NA, 203.7); (206.764, 191.1); (186.156, 199.8); (226.474, 229.8); (207.202, 238.6); (234.159, 225.5); (211.025, NA); (221.323, 260.3); (224.339, 185.1); (174.607, 204.2); (192.81, 190.4); (198.015, 233.5); (228.978, 210.9); (181.377, 260.6); (278.023, 194.9); (209.898, 194.2); (231.784, 239.4); (226.611, 209.8); (252.241, 248.1); (224.147, 242.4); (NA, 200.9); (267.561, 215.8); (218.007, 175.8); (219.587, 187.9); (235.915, 183.9); (214.621, 222.8); (156.367, 233.8)'.replace('NA', 'None').split('; ')
data = [eval(i) for i in data]
df = pd.DataFrame(data, columns=["Firm1", "Firm2"])
df_clean = df.dropna()
correlation, _ = pearsonr(df_clean["Firm1"], df_clean["Firm2"])
print("1. Коэффициент корреляции Пирсона между X и Y:", correlation)

# 2.1
t_stat, p_value = ttest_ind(df_clean["Firm1"], df_clean["Firm2"], equal_var=False) # equal_var=False или alternative='less'. при альтернативной гипотезе, если они не равны equal_var=False, если альтернативная гипотеза, что 2 > 1, то alternative='less', less(Firm1<Firm2), greater(Firm1>Firm2)
print("2.1. P-value для проверки гипотезы о равенстве средних:", p_value)

# 2.2
reject_mean_null = 1 if p_value < 0.1 else 0 # уровень значимости 0.1
print("2.2. Можно ли утверждать, что среднее значение больше у второй фирмы? (0 - нет, 1 - да):", reject_mean_null)

# 3.1
# для альтернативной гипотезе о том, что дисперсия показателя больше у первой фирмы
var_A = np.var(df_clean['Firm1'], ddof=1)
var_B = np.var(df_clean['Firm2'], ddof=1)

F = var_A / var_B if var_A > var_B else var_B / var_A

df1 = len(df_clean['Firm1']) - 1
df2 = len(df_clean['Firm2']) - 1
p_value_F = 1 - f.cdf(F, df1, df2)

print(f"F-статистика: {F}")
print(f"P-value для одностороннего теста: {p_value_F}")

# при альтернативной гипотезе об их неравенстве
var_A = np.var(df_clean['Firm1'], ddof=1)
var_B = np.var(df_clean['Firm2'], ddof=1)

F = var_A / var_B if var_A > var_B else var_B / var_A

df1 = len(df_clean['Firm1']) - 1
df2 = len(df_clean['Firm2']) - 1

p_value_F = 2 * min(f.cdf(F, df1, df2), 1 - f.cdf(F, df1, df2))

print(f"F-статистика: {F}")
print(f"P-value (F-тест): {p_value_F}")

# 3.2
alpha = 0.05
if p_value_F < alpha:
    print("3.2 Дисперсии показателей фирм различны (1)")
else:
    print("3.2 Дисперсии показателей фирм не различны (0)")"""

def num1():
    """## 1


# №4
# 1 прототип
def integrand(x, y):
    return np.e ** (-2 * x - y)
x_lower = 0
x_upper = np.inf
y_lower = 0
y_upper = np.inf
res, _ = dblquad(integrand, x_lower, x_upper, y_lower, y_upper)
C = 1 / res
print(f'C: {C}')
# Вычисляем P(X < 1)
def prob_integrand(y, x):
    return C * np.exp(-2*x - y)
x_lower_prob = 0
x_upper_prob = 1
y_lower_prob = 0
y_upper_prob = np.inf
P_X, _ = dblquad(prob_integrand, x_lower_prob, x_upper_prob, y_lower_prob, y_upper_prob)
print(f'P(X < 1): {P_X}')

# 2 прототип (C руками находим)
def integrand(x, y):
    return 2 / x + y * C
def y_lower(x):
    return max(0, 1 - x)
def y_upper(x):
    return 2
C = 1 / 4
P_X, _ = dblquad(integrand, 0, 1, y_lower, y_upper)
print(f"P(X + Y > 1) = {P_X}")


# №5
# f(x,y) = 1/2*pi * e^(-q/2). т.е. наше выражение над e равно -q/2, ищем q
x, y = symbols('x y')
q = 5*x**2 + 4*x*y + y**2 # + Rational(85, 12)
eq_1 = diff(q, x)
eq_2 = diff(q, y)
print('E(x), E(y):',solve({eq_1, eq_2}, {x, y}))
E_X, E_Y = 0, 0

5 2
2 1 - это [5, 2], [2, 1]

Cinv = Matrix([[5, 2], [2, 1]])

Var(X) Cov(X, Y)    Sigma(X)**2  Cov(X, Y)
Cov(X, Y) Var(Y)    Cov(X, Y)    Sigma(Y)**2     - это Cinv**-1

Cinv_1 = Cinv**(-1)
print(Cinv_1)
Sigma_X = Cinv_1[0]**0.5
Sigma_Y = Cinv_1[3]**0.5
Cov_XY = Cinv_1[1]
ro = Cov_XY / (Sigma_X * Sigma_Y)
# E(X|Y) = E(X) + ro*Sigma_X/Sigma_Y * (y - E(Y))
# Var(X|Y) = Sigma_X**2 * (1 - ro**2)
E_X_given_Y = E_X + ro * (Sigma_X / Sigma_Y) * (y - E_Y)
print('E(X|Y=y):', E_X_given_Y)"""

def form():
    """# формулы
Var(X) = E(X**2) - E(X)**2
Cov(X,Y) = E(XY) - E(X)*E(Y)
Sigma = Var(X)**0.5
ro = Cov_XY / (Sigma_X * Sigma_Y)

      Y=1   Y=2   Y=3
X=1   1/3   1/3   1/27
X=2   1/27  3/27  1/27
E(XY) = 1 * 1 * 1/3 + 1 * 2 * 1/3 + 1 * 3 * 1/27 + 2 * 1 * 1/27 + 2 * 2 * 3/27 + 2 * 3 * 1/27

независимые: P(AB) = P(A) * P(B)
условная P: P(A|B) = P(AB) / P(B)

E(X) = E[E(X|Y)]
E(Y|X) = Y * P(YX) / P(X)
Var(Y) = E[Var(Y|X)] + Var[E(Y|X)]
h_x|y(корреляционное отклонение) = Sigma[E(X|Y)] / Sigma(X)
h**2 = Sigma меняется на Var

равномерное распределение (события равновероятны):
f(x) = 1 / (b-a)
E(X) = (a+b) / 2
Var(X) = (b-a)**2 / 12

биномиальное распределение (2 исхода):
X ~ Bin(n, p); q = 1-p
E(X) = np; Var(X) = npq

геометрическое распределение (до какого-то события):
X ~ Geom(n)
E(X) = 1/p; Var(X) = q/p**2

Пуассон (маловероятные):
X ~ П(lambda); p_k = P(X=k) = lambda**k * e^-lambda / k!
E(X) = Var(X) = lambda

Непрерывные СВ:
P(a<=X<=b) = quad[f(x), a, b]. F(x) = P(X<=x) = quad[f(t), -inf, x].
quad[f(x), -inf, inf] = 1. E(X) = x * quad[f(x), -inf, inf]
Var(X) = (x**2 * quad[f(x), -inf, inf]) - E(X)**2"""