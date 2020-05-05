import { Component, OnInit } from '@angular/core';
import { RequirementService } from 'src/app/services/requirement.service';
import { Requirement } from 'src/app/models/requirement';
import { BaseService } from 'src/app/services/base-service.service';
import { Router } from '@angular/router';
import { FormControl, Validators } from '@angular/forms';
import { DepartmentService } from 'src/app/services/department.service';
import { Department } from 'src/app/models/department';

@Component({
  selector: 'app-requirement-list',
  templateUrl: './requirement-list.component.html',
  styleUrls: ['./requirement-list.component.less']
})
export class RequirementListComponent implements OnInit {

  listOfRequirements: Requirement[];
  empty: boolean;
  dateGroups = new Set<string>();
  loading: boolean;
  loadingText: string;
  currentUser: number;
  departmentControl: FormControl;
  departments: Department[];

  constructor(private requirementService: RequirementService,
    private departmentService: DepartmentService,
    private baseService: BaseService,
    private router: Router) { }

  ngOnInit() {
    this.fetchRequirements();
    this.currentUser = this.baseService.getUserId();
    this.departmentControl = new FormControl('', Validators.required);
  }

  fetchRequirements() {
    this.onRequestSent('Fetching requirements...');
    this.requirementService.getAll()
      .subscribe(
      (success) => {
        console.log(success);
        if (success.length > 0) {
          this.empty = false;
          success.forEach(
            r => {
              this.dateGroups.add(Requirement.toBasicDateFormat(r.last_updated));
            }
          );
          this.listOfRequirements = success;
        } else {
          this.empty = true;
          this.listOfRequirements = [];
        }
        this.fetchDepartments();
      },
      (error) => console.error(error)
    );
  }

  fetchDepartments() {
    this.onRequestSent('Fetching departments for requirement creation...');
    this.departmentService.getDepartmentsThatHaveUsers().subscribe(
      (success) => this.departments = success,
      (error) => console.error(error)
    ).add(() => this.onRequestDone());
  }

  getDepartmentName(depId: number): string {
    const dep = this.departments.find(d => d.id === depId);
    return dep ? `${dep.name} | ${dep.abbr}` : 'Unknown';
  }

  onRequestSent(msg: string) {
    this.loading = true;
    this.loadingText = msg;
  }

  onRequestDone() {
    this.loading = false;
    this.loadingText = '';
  }

  onEdit(reqId: number, depId: number) {
    this.router.navigate(['requirement-form'], { queryParams: { requirementId: reqId, departmentId: depId }});
  }

  onCreate() {
    const departmentId = this.departmentControl.value;
    this.router.navigate(['requirement-form'], { queryParams: { departmentId: departmentId }});
  }

}
