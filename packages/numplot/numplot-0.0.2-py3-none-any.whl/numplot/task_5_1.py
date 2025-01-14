def task_5_1():
    text = """Ряд совместных наблюдений независимых нормально распределенных случайных величин X и Y, описывающих некоторый финансовый показатель двух фирм, задан двумерной выборкой:
    {(-199.76, -175.45); (-219.72, -194.67);
    
    ALPHA_MEAN = 0.01  # Уровень значимости для теста средних
    APLHA_VARIANCE = 0.05  # Уровень значимости для теста дисперсий
    
    import pandas as pd
    import numpy as np
    from scipy.stats import pearsonr, ttest_ind, f
    
    raw_data = [(-195.996, -166.5), (-165.653, -176.5),]
    
    data = pd.DataFrame(raw_data, columns=["A", "B"])
    data = data.replace("NA", np.nan).dropna()
    
    correlation, _ = pearsonr(data["A"], data["B"])
    print(f"Коэффициент корреляции Пирсона: {correlation:.20f}")
    
    t_stat, p_value_ttest = ttest_ind(data["A"], data["B"], equal_var=False, alternative='less')
    print(f"P-значение (t-тест Уэлча): {p_value_ttest:.20f}")
          
    result_mean_test = int(p_value_ttest < ALPHA_MEAN)
    print(f"Результат теста средних (0.01): {result_mean_test}")
    
    var_a = np.var(data["A"], ddof=1)
    var_b = np.var(data["B"], ddof=1)
    df_a = len(data["A"]) - 1
    df_b = len(data["B"]) - 1
    
    if var_a > var_b:
        f_stat = var_a / var_b
        p_value_f_test = 2 * min(f.cdf(f_stat, df_a, df_b), 1 - f.cdf(f_stat, df_a, df_b))
    else:
        f_stat = var_b / var_a
        p_value_f_test = 2 * min(f.cdf(f_stat, df_b, df_a), 1 - f.cdf(f_stat, df_b, df_a))
    print(f"P-значение (F-тест): {p_value_f_test:.20f}")


    result_var_test = int(p_value_f_test < APLHA_VARIANCE)
    print(f"Результат теста дисперсий (0.05): {result_var_test}")
    """
    return text