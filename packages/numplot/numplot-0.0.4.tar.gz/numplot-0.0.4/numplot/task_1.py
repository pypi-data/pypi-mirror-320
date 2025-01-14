def task_1():
        text = """
        Абсолютно непрерывная случайная величина X может принимать значения только в отрезке [4,7]. На этом отрезке плотность распределения случайной величины X имеет вид: f(x)=C(1+3x0,5+6x0,7+9x0,9)1,5, где C – положительная константа. Найдите: 1) константу C; 2) математическое ожидание E(X); 3) стандартное отклонение σX; 4) квантиль уровня 0,8 распределения X.
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

        print(text)