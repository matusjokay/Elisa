import { Component, OnInit } from '@angular/core';
import {TimetableService} from '../../services/timetable.service';
import { DepartmentService } from 'src/app/services/department.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.less']
})
export class DashboardComponent implements OnInit {

  constructor(private timetableService: TimetableService,
    private departmentService: DepartmentService) { }

  ngOnInit() {
    if (!localStorage.getItem('active_scheme')) {
      this.timetableService.getLastScheme().subscribe(schema => {
        // returns scheme object which contains DB data as following
        // id, name, status
        // for now name will suffice
        console.log('setting latest schema');
        console.log(schema);
        localStorage.setItem('active_scheme', schema['name']);
      });
    }
  }

  initData() {
    this.departmentService.getCachedDepartments().subscribe(
      (next) => {
        console.log('received departments');
        console.log(next);
      }
    );

    this.timetableService.getCurrentSelectedPeriods().subscribe(
      (success) => {
        console.log('received current periods');
        console.log(success);
      }
    );
  }
}
