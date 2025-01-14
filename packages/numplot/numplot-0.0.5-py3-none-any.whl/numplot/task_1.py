def task_1(var=1):
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
        text = """2. import sympy as sp
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
        return text