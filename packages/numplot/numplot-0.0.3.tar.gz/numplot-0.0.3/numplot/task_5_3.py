def task_5_3():
    text = """
    По результатам социологического исследования ответы респондентов на определенный вопрос анкеты представлены в виде выборки:
    {NA; Unkn; Less; More; Norm;
    
    ALPHA = 0.1  # уровень значимости для критерия Хи-квадрат
    CONFIDENCE_LEVEL = 0.99  # уровень доверия для интервала
    ANSWER_KOLICHESTVO = 'A' # что ищем, когда ищем КОЛИЧЕСТВО (Есть не в каждом варианте)
    ANSWER_DOLYA = 'B' # что ищем, когда ищем ДОЛЮ
    
    import numpy as np
    import pandas as pd
    from scipy.stats import chi2, norm
    import matplotlib.pyplot as plt

    # Вставить данные (могут быть другие слова\буквы)

    sample = [
        'C', 'D', 'C' ... ... ... 'A', 'A', 'D'
    ]
    
    cleaned_sample = [x for x in sample if x != 'NA']
    na_count = len(sample) - len(cleaned_sample)
    
    unique_answers = set(cleaned_sample)
    num_unique_answers = len(unique_answers)
    print(f"Количество различных вариантов ответов: {num_unique_answers}")
    
    sample_size = len(cleaned_sample)
    print(f"Объем очищенной выборки: {sample_size}")
    
    num_na = na_count
    print(f"Количество пропущенных данных 'NA': {num_na}")
    
    a_count = cleaned_sample.count(ANSWER_KOLICHESTVO)
    print(f"Количество респондентов, которые дали ответ 'A': {a_count}")
    
    y_count = cleaned_sample.count(ANSWER_DOLYA)
    y_ratio = y_count / sample_size
    print(f"Доля респондентов, которые дали ответ '{ANSWER_DOLYA}': {y_ratio:.4f}")
    
    z = norm.ppf(1 - (1 - CONFIDENCE_LEVEL) / 2)
    se = np.sqrt(y_ratio * (1 - y_ratio) / sample_size)
    lower_bound = y_ratio - z * se
    upper_bound = y_ratio + z * se
    print(f"Правая граница {CONFIDENCE_LEVEL} доверительного интервала: {upper_bound:.4f}")
    print(f"Левая граница {CONFIDENCE_LEVEL} доверительного интервала: {lower_bound:.4f}")
    
    observed_counts = pd.Series(cleaned_sample).value_counts().values
    expected_counts = [sample_size / num_unique_answers] * num_unique_answers
    chi2_stat = sum((obs - exp) ** 2 / exp for obs, exp in zip(observed_counts, expected_counts))
    df = num_unique_answers - 1
    critical_value = chi2.ppf(1 - ALPHA, df)
    reject_null = int(chi2_stat > critical_value)
    print(f"Критическое значение статистики хи-квадрат: {critical_value:.4f}")
    print(f"Количество степеней свободы: {df}")
    print(f"Наблюдаемое значение хи-квадрат: {chi2_stat:.4f}")
    print(f"Есть основания отвергнуть гипотезу: {reject_null}")
    
    plt.figure(figsize=(8, 5))
    plt.hist(cleaned_sample, bins=len(unique_answers), alpha=0.7, color='blue', rwidth=0.85)
    plt.xlabel('Ответы респондентов')
    plt.ylabel('Частота')
    plt.title('Гистограмма очищенной выборки')
    plt.grid(axis='y')
    plt.show()
    """
    return text