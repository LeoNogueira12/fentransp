import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import lfilter, freqz

T = 1E-6
Fs = 1 / T
t = np.arange(0, 1E-3 + T, T)

x = np.sin(2 * np.pi * 1000 * t) + np.sin(2 * np.pi * 100000 * t)

b = [0.03046, 0.03046]
a = [1, -0.93986]

y = np.zeros_like(t)

for n in range(1, len(t)):
    y[n] = 0.93986 * y[n - 1] + 0.03046 * x[n] + 0.03046 * x[n - 1]

plt.figure()
plt.plot(t, x, label='x(t) - Sinal Original')
plt.plot(t, y, label='y(t) - Sinal Filtrado')
plt.xlabel('Tempo (s)')
plt.ylabel('Amplitude')
plt.legend()
plt.grid(True)
plt.title('Sinal Original vs. Sinal Filtrado')
plt.show()

w, h = freqz(b, a, fs=Fs)
plt.figure()
plt.plot(w, 20 * np.log10(abs(h)))
plt.title('Resposta em Frequência do Filtro')
plt.xlabel('Frequência (Hz)')
plt.ylabel('Magnitude (dB)')
plt.grid(True)
plt.show()
