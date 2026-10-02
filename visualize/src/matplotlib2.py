import matplotlib.pyplot as plt

plt.rc('font', family='Malgun Gothic')

years = ['2019', '2020', '2021', '2022', '2023']
license_percent = [10.22, 11.1, 11.91, 12.85, 13.79]
accident_percent = [14.48, 14.82, 15.68, 17.60, 19.98]


plt.figure(figsize=(12, 7))

plt.fill_between(years, license_percent, accident_percent, color='gray', alpha=0.2, label='격차')

plt.plot(years, license_percent, color='blue', marker='o', linewidth=3, markersize =10, label='면허비율')
plt.plot(years, accident_percent, color='red', marker='s', linewidth=3, markersize =10, linestyle='--',  label='사고비율')

for i in range(5):

    plt.text(years[i], license_percent[i] - 0.8, f'{license_percent[i]}%', color='blue', fontsize=11, fontweight='bold')


    plt.text(years[i], accident_percent[i] + 0.8, f'{accident_percent[i]}%', color='red', fontsize=11,fontweight='bold')

    gap = accident_percent[i] - license_percent[i]
    mid_y = (accident_percent[i] +license_percent[i]) / 2

    plt.text(years[i], mid_y, f'{gap: .2f}%'
             , color='green', fontweight='bold'
             , ha='center', va='center', bbox=dict(facecolor='white'
             , edgecolor='none', alpha=0.7
             )
             )

plt.title("고령운전자 면허 비율 과 사고 유발 비율 추이" , fontsize=18, pad=20)
plt.grid(True, linestyle='--', alpha=0.5) #alpha = 투명도
plt.ylim(8, 23)
plt.ylabel('비율(%)', fontsize = 13)

plt.legend(loc='upper left', fontsize =12)
plt.show()





