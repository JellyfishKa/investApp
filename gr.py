import matplotlib.pyplot as plt

# Настройка для светлой темы
plt.style.use('default') 
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
fig.patch.set_facecolor('white') # Белый фон всего изображения

# ЦВЕТОВАЯ ПАЛИТРА (Адаптировано для белого фона)
color_purple = '#6200ea'  # Глубокий фиолетовый
color_yellow = '#ffab00'  # Насыщенный желтый (янтарный)
color_gray = '#9e9e9e'    # Серый
text_color = '#212121'    # Почти черный для текста

# --- ГРАФИК 1: Распределение усилий (Fullstack) ---
roles = ['Frontend (Flutter)', 'Backend (FastAPI)', 'ML Engineering', 'QA & DevOps']
effort = [40, 30, 20, 10]

# Рисуем бары
bars = ax1.barh(roles, effort, color=[color_purple, color_purple, color_yellow, color_gray])

ax1.set_title('РАСПРЕДЕЛЕНИЕ КОМПЕТЕНЦИЙ (1 чел.)', fontsize=16, color=text_color, pad=20, fontweight='bold')
ax1.set_xlim(0, 50)
ax1.invert_yaxis() 

# Убираем рамки
for spine in ax1.spines.values():
    spine.set_visible(False)

ax1.get_xaxis().set_visible(False) 
ax1.tick_params(axis='y', colors=text_color, labelsize=14)

# Цифры внутрь или рядом с барами
for bar in bars:
    width = bar.get_width()
    ax1.text(width + 1, bar.get_y() + bar.get_height()/2, 
             f'{int(width)}%', ha='left', va='center', color=text_color, fontsize=14, fontweight='bold')

# --- ГРАФИК 2: Ежемесячный бюджет (Burn Rate) ---
# Расчет на 2025 год:
# 1. Hosting (Render/Amvera) ~700 руб
# 2. Stores (Apple $99/год + Google $25) ~1000 руб/мес (амортизация)
# 3. Domain & Services ~800 руб
labels = ['Hosting\n(Backend)', 'App Stores\n(License)', 'Domain &\nMisc', 'Database\n(Free Tier)']
sizes = [700, 1000, 800, 0] 
colors = [color_purple, color_yellow, color_gray, '#4caf50']

# Рисуем пончик
wedges, texts, autotexts = ax2.pie(sizes[:-1], labels=labels[:-1], colors=colors[:-1], 
                                   autopct='%1.0f%%', startangle=140, pctdistance=0.85,
                                   textprops={'color': text_color, 'fontsize': 12, 'weight': 'bold'})

# Белый круг в центре
centre_circle = plt.Circle((0,0), 0.70, fc='white')
ax2.add_artist(centre_circle)

ax2.set_title('СТРУКТУРА РАСХОДОВ (~2500₽/мес)', fontsize=16, color=text_color, pad=20, fontweight='bold')

# Итоговая надпись в центре
ax2.text(0, 0, 'Low\nCost', ha='center', va='center', fontsize=20, color=color_purple, fontweight='bold')

plt.tight_layout()
plt.show()