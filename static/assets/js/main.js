fetch('/analyze')
  .then(res => res.json())
  .then(data => {
    console.log("Received data:", data);

    const labels = data.map(row => row.Date);
    const close = data.map(row => row.Close);
    const sma10 = data.map(row => row.SMA10);
    const sma30 = data.map(row => row.SMA30);

    // Buy/Sell markers
    const buySignals = data.map(row => row.Action === 'BUY' ? row.Close : null);
    const sellSignals = data.map(row => row.Action === 'SELL' ? row.Close : null);

    const ctx = document.getElementById('crossoverChart').getContext('2d');
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Close',
            data: close,
            borderColor: 'gray',
            borderWidth: 1.5,
            tension: 0.2
          },
          {
            label: 'SMA10',
            data: sma10,
            borderColor: 'blue',
            borderWidth: 1.5,
            tension: 0.2
          },
          {
            label: 'SMA30',
            data: sma30,
            borderColor: 'orange',
            borderWidth: 1.5,
            tension: 0.2
          },
          {
            label: 'BUY Signal',
            data: buySignals,
            borderColor: 'green',
            pointBackgroundColor: 'green',
            pointRadius: 6,
            showLine: false,
            type: 'scatter'
          },
          {
            label: 'SELL Signal',
            data: sellSignals,
            borderColor: 'red',
            pointBackgroundColor: 'red',
            pointRadius: 6,
            showLine: false,
            type: 'scatter'
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Stock Price with Moving Average Crossover Signals'
          }
        },
        interaction: {
          mode: 'index',
          intersect: false
        },
        scales: {
          x: {
            title: { display: true, text: 'Date' }
          },
          y: {
            title: { display: true, text: 'Price' }
          }
        }
      }
    });
  })
  .catch(error => {
    console.error("Error loading chart data:", error);
  });