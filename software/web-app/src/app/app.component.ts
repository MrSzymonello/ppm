import { Component } from '@angular/core';
import { DataService } from './data.service';
import { Chart } from 'angular-highcharts';
import { Response } from '@angular/http';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {

  chart = new Chart({
    chart: {
      type: 'line',
      zoomType: 'x'
    },
    title: {
      text: 'Magnetic field'
    },
    credits: {
      enabled: false
    },
    xAxis: {
      type: 'datetime',
      title: {
        text: 'UTC'
      }
    },
    yAxis: {
      title: {
        text: 'Magnetic field [nT]'
      }
    },
    legend: {
      enabled: false
    }
  });

  constructor(private dataService: DataService) {}

  ngOnInit() {
    this.dataService.latestPpmData()
      .subscribe((res: Response) => {
        const data = res.json();
        
        var plotData = []
        data.forEach(element => {
          plotData.push({x: (new Date(element.takenAt * 1e3)).getTime(), y: element.b});
        });

        this.chart.addSerie({
          name: 'Magnetic field',
          data: plotData
        });
    });
  }
}
