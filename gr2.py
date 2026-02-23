import matplotlib.pyplot as plt
import numpy as np

# Настройка стиля (Светлая тема)
plt.style.use('default')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
fig.patch.set_facecolor('white')

# ЦВЕТОВАЯ ПАЛИТРА
color_purple = '#6200ea'  # Доходы / Гранты
color_yellow = '#ffab00'  # Расходы / B2B
color_gray = '#9e9e9e'
text_color = '#212121'

# --- ГРАФИК 1: Точка безубыточности (Unit Economics) ---
# Данные
users = np.linspace(0, 1000, 100)
# Расходы: База 2500 + 3.5 рубля за каждого юзера (нагрузка)
costs = 2500 + (users * 3.5) 
# Доходы: Конверсия 5%, цена 299р (1000 юзеров * 0.05 * 299 = 14950)
revenue = users * 0.05 * 299 

# Рисуем линии
ax1.plot(users, revenue, color=color_purple, linewidth=3, label='Доходы (Sub 299₽)')
ax1.plot(users, costs, color=color_yellow, linewidth=3, linestyle='--', label='Расходы (Server)')

# Закрашиваем зону прибыли
ax1.fill_between(users, revenue, costs, where=(revenue > costs), 
                 interpolate=True, color='#4caf50', alpha=0.1)
ax1.text(800, 8000, 'ЗОНА\nПРИБЫЛИ', color='#2e7d32', fontweight='bold', fontsize=12)

# Точка безубыточности (примерно 170 пользователей)
break_even_idx = np.argwhere(revenue > costs)[0][0]
be_users = users[break_even_idx]
be_val = costs[break_even_idx]

ax1.scatter(be_users, be_val, color='red', zorder=5, s=100)
ax1.annotate(f'Окупаемость:\n~{int(be_users)} юзеров', xy=(be_users, be_val), xytext=(be_users+50, be_val-4000),
             arrowprops=dict(facecolor='black', arrowstyle='->'), fontsize=11, fontweight='bold')

ax1.set_title('UNIT-ЭКОНОМИКА (1-й год)', fontsize=16, color=text_color, fontweight='bold', pad=20)
ax1.set_xlabel('Активные пользователи (MAU)', fontsize=12)
ax1.set_ylabel('Рубли (₽)', fontsize=12)
ax1.legend(loc='upper left', frameon=False)
ax1.grid(True, linestyle=':', alpha=0.6)

# Убираем рамки сверху и справа
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)


# --- ГРАФИК 2: Модель монетизации и финансирования ---
# Откуда деньги?
labels = ['B2C Подписка\n(Recurrent)', 'Гранты и\nАкселераторы', 'B2B Лицензии\n(ВУЗы)']
sizes = [40, 40, 20] # Доли в бюджете первого года
colors = [color_purple, '#b388ff', color_yellow]
explode = (0.05, 0, 0)  # Выдвигаем подписку

wedges, texts, autotexts = ax2.pie(sizes, explode=explode, labels=labels, colors=colors,
                                   autopct='%1.0f%%', startangle=90, pctdistance=0.80,
                                   textprops={'color': text_color, 'fontsize': 12, 'weight': 'bold'})

# Белый круг в центре
centre_circle = plt.Circle((0,0), 0.65, fc='white')
ax2.add_artist(centre_circle)

ax2.set_title('ИСТОЧНИКИ ФИНАНСИРОВАНИЯ', fontsize=16, color=text_color, fontweight='bold', pad=20)
ax2.text