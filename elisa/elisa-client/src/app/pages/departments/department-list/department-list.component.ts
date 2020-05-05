import { Component, OnInit } from '@angular/core';
import { Department, DepartmentNode } from '../../../models/department';
import { MatTreeNestedDataSource } from '@angular/material/tree';
import { NestedTreeControl } from '@angular/cdk/tree';
import { DepartmentService } from 'src/app/services/department.service';
import { MatDialog } from '@angular/material/dialog';
import { DepartmentUserDetailComponent } from '../department-user-detail/department-user-detail.component';

@Component({
  selector: 'app-department-list',
  templateUrl: './department-list.component.html',
  styleUrls: ['./department-list.component.less']
})
export class DepartmentListComponent implements OnInit {
  departments: Department[];

  treeControl = new NestedTreeControl<DepartmentNode>(node => !node.parent ? node.children : null);
  dataSource = new MatTreeNestedDataSource<DepartmentNode>();

  displayedColumns: string[] = ['id', 'name', 'abbr', 'parent'];

  loadingText: string;
  loading: boolean;

  constructor(private departmentService: DepartmentService,
    public dialog: MatDialog) {
  }

  ngOnInit() {
    this.fetchDepartments();
  }

  fetchDepartments() {
    this.onRequestSent('Fetching departments...');
    this.departmentService.getDepartmentsFei().subscribe(
      (success) => {
        this.departments = success;
        this.dataSource.data = this.createTree(success);
      },
      (error) => console.error(error)
    ).add(() => this.onRequestDone());
  }

  // Lets assume for now that the tree has depth of just 2 levels
  createTree(departments: Department[]): DepartmentNode[] {
    const result = [];
    departments.forEach(dep => {
      if (!dep.parent) {
        if (!result.some(department => department.id === dep.id)) {
          result.push({
            id: dep.id,
            name: dep.name,
            abbr: dep.abbr,
            parent: dep.parent,
            children: []
          });
        }
      } else {
        let parent = result.find(node => node.id === dep.parent);
        if (!parent) {
          const parentData = this.departments.find(node => node.id === dep.parent);
          parent = {
            id: parentData.id,
            name: parentData.name,
            abbr: parentData.abbr,
            parent: null,
            children: []
          };
          const chd = {
            id: dep.id,
            name: dep.name,
            abbr: dep.abbr,
            parent: dep.parent
          };
          parent.children.push(chd);
          result.push(parent);
        } else {
          const index = result.indexOf(parent);
          const child = {
            id: dep.id,
            name: dep.name,
            abbr: dep.abbr,
            parent: dep.parent
          };
          parent.children.push(child);
          result[index] = parent;
        }
      }
    });
    return result;
  }

  onRequestSent(msg: string) {
    this.loadingText = msg;
    this.loading = true;
  }

  onRequestDone() {
    this.loadingText = '';
    this.loading = false;
  }

  onDepartmentPersonManage(node: DepartmentNode) {
    console.log(node);
    this.dialog.open(DepartmentUserDetailComponent, {
      width: '75vw',
      height: '25vh',
      data: { department: {
        id: node.id,
        name: node.name,
        abbr: node.abbr,
        parent: node.parent
      }}
    });
  }

  hasChild = (_: number, node: Department) => !node.parent;
}
