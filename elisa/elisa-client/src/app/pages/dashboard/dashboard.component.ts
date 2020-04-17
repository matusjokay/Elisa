import { PeriodService } from './../../services/period.service';
import { Component, OnInit } from '@angular/core';
import { DepartmentService } from 'src/app/services/department.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.less']
})
export class DashboardComponent implements OnInit {

  activeSchema: string;

  constructor(private departmentService: DepartmentService,
    private periodService: PeriodService) { }

  ngOnInit() {
    this.activeSchema = localStorage.getItem('active_scheme');
    this.initData();
  }


  // TODO: initialize some cachable data
  // or have different purpose for this whole component
  // probably to show requirements, collisions etc.
  initData() {
    this.departmentService.getCachedDepartments();
    this.periodService.getCurrentSelectedPeriods();
    // this.userService.getCachedAllUsers();
  }
}
