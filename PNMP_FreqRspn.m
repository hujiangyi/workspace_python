
clear;
clc;

a = [-1+0j, 0+1j, -2-3j, 3+4j, -6-5j, 8+9j, -16-22j, 494+0j, -17-20j,...
    56-40j, 85-41j, -30+3j, 31-27j, -4-6j, 1-2j, 1-9j, -2+2j, -1-3j,...
    -1+0j, 0+0j, -1+0j, 0+0j, 0+0j, 0+0j].';

b = [0-1j, -1+1j, 0-2j, -1+2j, 1-6j, -2+10j, -2-27j, 510+0j, -1-29j,...
    5-11j, -2+4j, -1-3j, 0+2j, -1-2j, -1+2j, -1-1j, 0+1j, 0-2j, 0+0j,...
    -3-1j, -1-1j, -1+0j, 0+1j, -1+0j].';

%power normalize
a_n = a/sqrt(sum(abs(a).^2));
b_n = b/sqrt(sum(abs(b).^2));

fftSize = 512;

a_padding = [zeros(fftSize-length(a), 1); a_n];
a_fft = fft(a_padding, fftSize);
mag_a_dB = 20*log10(abs(fftshift(a_fft)));
fft_bin = -fftSize/2:1:fftSize/2-1;
bandWidth = 5.12*1.25;
freq_a = fft_bin/fftSize*bandWidth;

b_padding = [zeros(fftSize-length(b), 1); b_n];
b_fft = fft(b_padding, fftSize);
mag_b_dB = 20*log10(abs(fftshift(b_fft)));
fft_bin = -fftSize/2:1:fftSize/2-1;
bandWidth = 5.12*1.25;
freq_b = (-1/2:1/fftSize:1/2-1/fftSize)*bandWidth;

plot(freq_a, mag_a_dB, 'm-', 'LineWidth', 2);
hold on;
plot(freq_b, mag_b_dB, 'g-', 'LineWidth', 2);
grid on;
hold off;
xlim([-bandWidth/2 bandWidth/2]);
ylim([-3.5 3.5]);
xlabel('Relative Frequency (MHz)');
ylabel('Magnitude (dB)');
legend('Field','Short Plant');

