import { Component, OnInit } from '@angular/core';
import {TimetableService} from '../../services/timetable.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.less']
})
export class DashboardComponent implements OnInit {

  constructor(private timetableService: TimetableService) { }

  ngOnInit() {
    if(!localStorage.getItem('active_scheme')){
      this.timetableService.getLastScheme().subscribe(result=>{
        localStorage.setItem('active_scheme',result);
      });
    }
  }
}
