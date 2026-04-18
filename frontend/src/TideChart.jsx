import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';

// Chart.js modüllerini kaydediyoruz
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function TideChart() {
  // SAHTE VERİ ÜRETİMİ (Backend'den gerçek ML verisi gelene kadar)
  // X Ekseni: Zaman etiketleri (Geçmiş 12 saat, ŞU AN, Gelecek 12 saat)
  const labels = [
    '-12s', '-10s', '-8s', '-6s', '-4s', '-2s', 'ŞU AN', 
    '+2s', '+4s', '+6s', '+8s', '+10s', '+12s'
  ];

  // Tarihsel Veri (Geçmiş ve ŞU AN var, gelecek null)
  const historicalData = [165, 172, 190, 210, 205, 185, 170, null, null, null, null, null, null];
  
  // ML Tahmin Verisi (Geçmiş null, ŞU AN'dan başlıyor ve geleceği çiziyor)
  // ŞU AN noktasında (170) birleşmeleri için kesişim noktası aynı değer.
  const predictionData = [null, null, null, null, null, null, 170, 155, 140, 150, 180, 205, 215];

  const data = {
    labels,
    datasets: [
      {
        label: 'Tarihsel Gerçek Veri (cm)',
        data: historicalData,
        borderColor: 'rgb(59, 130, 246)', // Tailwind blue-500
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 3,
        pointBackgroundColor: 'rgb(59, 130, 246)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgb(59, 130, 246)',
        fill: true,
        tension: 0.4, // Çizgiyi yumuşatır (Dalga efekti)
      },
      {
        label: 'AI Tahmini (Gelecek 24 Saat)',
        data: predictionData,
        borderColor: 'rgb(168, 85, 247)', // Tailwind purple-500
        borderWidth: 3,
        borderDash: [5, 5], // KESİKLİ ÇİZGİ EFEKTİ BURASI!
        pointBackgroundColor: 'rgb(168, 85, 247)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgb(168, 85, 247)',
        fill: false,
        tension: 0.4,
      }
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#cbd5e1', // text-slate-300
          font: { family: 'Inter, sans-serif', size: 12, weight: 'bold' }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.9)', // Koyu arkaplan
        titleColor: '#fff',
        bodyColor: '#cbd5e1',
        borderColor: 'rgba(59, 130, 246, 0.3)',
        borderWidth: 1,
        padding: 12,
        boxPadding: 6
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(51, 65, 85, 0.3)' }, // border-slate-700
        ticks: { color: '#94a3b8' } // text-slate-400
      },
      y: {
        grid: { color: 'rgba(51, 65, 85, 0.3)' },
        ticks: { color: '#94a3b8', callback: function(value) { return value + ' cm'; } }
      }
    }
  };

  return (
    <div className="w-full h-full min-h-[350px]">
      <Line data={data} options={options} />
    </div>
  );
}