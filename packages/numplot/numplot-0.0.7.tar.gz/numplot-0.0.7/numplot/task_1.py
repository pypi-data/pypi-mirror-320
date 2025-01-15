"""import openai


class GPTClient:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo-instruct-0914"):
        self.api_key = api_key
        self.model = model
        openai.api_key = self.api_key

    def send_request(self, prompt: str, max_tokens: int = 100, temperature: float = 0.7):
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"Ошибка при запросе: {str(e)}"
"""

def t_1(var=1, prompt=""):
    if var == 1:
        text = """
        1. Абсолютно непрерывная случайная величина X может принимать значения только в отрезке [4,7]. На этом отрезке плотность распределения случайной величины X имеет вид: f(x)=C(1+3x0,5+6x0,7+9x0,9)1,5, где C – положительная константа. Найдите: 1) константу C; 2) математическое ожидание E(X); 3) стандартное отклонение σX; 4) квантиль уровня 0,8 распределения X.
        import sympy as sp
        
        l, r = [4, 7]
        
        # Определение переменных
        x = sp.symbols('x')
        C = sp.symbols('C')
        
        # Плотность вероятности
        f_x = C * (1 + 3 * x**0.5 + 6 * x**0.7 + 9 * x**0.9)**1.5
        
        
        # 1. Нахождение константы C
        normalization_integral = sp.integrate(f_x, (x, l, r))
        C_value = sp.solve(normalization_integral - 1, C)[0]
        
        # 2. Математическое ожидание E(X)
        f_x_with_C = f_x.subs(C, C_value)
        E_X = sp.integrate(x * f_x_with_C, (x, l, r))
        
        # 3. Стандартное отклонение σX
        E_X2 = sp.integrate(x**2 * f_x_with_C, (x, l, r))
        variance_X = E_X2 - E_X**2
        std_dev_X = sp.sqrt(variance_X)
        
        # 4. Квантиль уровня 0.9
        quantile_eq = sp.integrate(f_x_with_C, (x, l, x)) - 0.8
        quantile_90 = sp.nsolve(quantile_eq, x, l + 1)  # Начальное приближение x=5
        
        print("Нахождение константы C", round(C_value, 5))
        print("Математическое ожидание E(X)", round(E_X.evalf(), 3))
        print("Стандартное отклонение σX", round(std_dev_X.evalf(), 3))
        print("Квантиль уровня 0.9", round(quantile_90, 3))")"""
    if var == 2:
        text = """2. 
       Запишите условие нормировки: ∫∫_D f(x, y) dx dy = 1.
       Подставьте выражение для плотности f(x, y) и определите пределы интегрирования.
       Вычислите внутренний интеграл по одной из переменных (например, по y).
       Затем вычислите внешний интеграл по оставшейся переменной (например, по x).
       Установите равенство к 1 и решите уравнение для нахождения константы C.
       Определите, какую вероятность необходимо найти (например, P(X > a) или P(Y < b)).
       Запишите соответствующий интеграл: P(X > a) = ∫_a^∞ ∫_c^d f(x, y) dy dx, где [a, b] и [c, d] — это пределы интегрирования для переменных x и y.
       Полученное значение будет искомой вероятностью.
        import sympy as sp
        def compute_probability_and_constant(f, x_limits, y_limits, a):
                Вычисляет нормирующую константу C и вероятность P(X > a) для заданной функции плотности.
                
                :param f: Символьная функция плотности, принимающая переменные x, y и C.
                :param x_limits: Кортеж с ограничениями для x (x_min, x_max).
                :param y_limits: Кортеж с ограничениями для y (y_min, y_max).
                :param a: Значение для вычисления вероятности P(X > a).
                :return: Кортеж (C, P(X > a)).
                # Определяем переменные
                x, y, C = sp.symbols('x y C')
                
                # Шаг 1: Нормировка плотности
                # Вычисляем двойной интеграл
                integral = sp.integrate(sp.integrate(
                    f, (y, y_limits[0], y_limits[1])), (x, x_limits[0], x_limits[1]))
                
                # Устанавливаем уравнение для нормировки
                normalization_eq = sp.Eq(integral, 1)
                
                # Решаем уравнение для C
                C_value = sp.solve(normalization_eq, C)[0]
                
                # Подставляем значение C в функцию плотности
                f_with_C = f.subs(C, C_value)
                
                # Шаг 2: Вычисление вероятности P(X > a)
                probability = sp.integrate(sp.integrate(
                    f_with_C, (y, y_limits[0], y_limits[1])), (x, a, x_limits[1]))
                
                # Шаг 2: Вычисление вероятности P(X < a)
                # probability = sp.integrate(sp.integrate(f_with_C, (y, y_limits[0], y_limits[1])), (x, x_limits[0], a))
                
                return C_value, probability
        
        
        # Пример использования
        x_limits = (0, 2)
        y_limits = (0, 3)
        a = 1
        
        # Определяем функцию плотности
        C, x, y = sp.symbols('C x y')
        density_function = C * x * y * (2 - x)
        
        # Вызываем функцию
        C_value, probability = compute_probability_and_constant(
            density_function, x_limits, y_limits, a)
        
        print(f"Найдена константа C: {C_value}")
        print(f"P(X > {a}): {probability}")
        """
    if var == 3:
        text = """
        Количество опоздавших на самолет пассажиров для каждого рейса описывается случайной величиной Х, распределенной по закону Пуассона с параметром А = 4.
        При этом стоимость билета, который не подлежит возврату, описывается нормально
        распределенной случайной величиной У с параметрами m=4300 и o=133.2.
        Вычислите среднюю сумму стоимости пропавших билетов и её 
        среднеквадратическое отклонение, приходящиеся на каждый рейс
        Дано:
        Количество опоздавших пассажиров X ~ Poisson(λ = 4)
        Стоимость билета Y ~ N(4300, 133.2^2)
        
        Решение:
        
        1. Математическое ожидание суммы стоимости пропавших билетов:
        E(S) = E(X) * E(Y)
        E(X) = λ = 4
        E(Y) = 4300
        E(S) = 4 * 4300 = 17200
        
        2. Дисперсия суммы стоимости пропавших билетов:
        Var(S) = E(X) * Var(Y) + (E(Y))^2 * Var(X)
        Var(X) = λ = 4
        Var(Y) = 133.2^2 = 17733.44
        Var(S) = 4 * 17733.44 + 4300^2 * 4
        Var(S) = 70933.76 + 73960000 = 74030933.76
        
        3. Среднеквадратическое отклонение суммы стоимости пропавших билетов:
        σ(S) = sqrt(Var(S)) = sqrt(74030933.76) ≈ 8602.97
        
        Ответ:
        Средняя сумма стоимости пропавших билетов: 17200
        Среднеквадратическое отклонение: 8602.97
"""
#    if var == 30:
#        API_KEY = "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"
#        gpt_client = GPTClient(api_key=API_KEY)
#        text = gpt_client.send_request(prompt=prompt)"""
    return text