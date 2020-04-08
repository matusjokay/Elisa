import {Component, OnInit} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../../../environments/environment';
import {Department} from '../../../models/department';
import {Observable} from 'rxjs';
import {map} from 'rxjs/operators';
import { MatTreeNestedDataSource } from '@angular/material/tree';
import {NestedTreeControl} from '@angular/cdk/tree';

@Component({
  selector: 'app-department-list',
  templateUrl: './department-list.component.html',
  styleUrls: ['./department-list.component.less']
})
export class DepartmentListComponent implements OnInit {
  departments: Department[];

  // treeControl = new NestedTreeControl<Department>(node => node.children);
  dataSource = new MatTreeNestedDataSource<Department>();

  displayedColumns: string[] = ['id', 'name', 'abbr', 'parent'];

  constructor(private httpClient: HttpClient) {
  }

  ngOnInit() {
    // this.getData().subscribe(data => {
    //   this.departments = data;
    //   this.dataSource.data = this.createTree(this.departments,null);;
    // });
    console.log('todo fetch data and create tree??');
  }

  // getData(): Observable<Department[]>{
  //   return this.httpClient.get<Department[]>(environment.APIUrl + 'departments/').pipe(map((data: any[]) => data.map((item: any) =>
  //       new Department(
  //         item.id,
  //         item.name,
  //         item.abbr,
  //         item.parent
  //       ))));
  // }

  createTree(data, parent){
    var out = [];
    for(var i in data) {
      if(data[i].parent == parent) {
        var children = this.createTree(data, data[i].id)

        if(children.length) {
          data[i].children = children
        }
        out.push(data[i])
      }
    }
    return out;
  }
  // onSelect(department: Department): void {
  //   this.selectedDepartment = department;
  // }

  // hasChild = (_: number, node: Department) => !!node.children && node.children.length > 0;

  save(department: Department): void{
    this.httpClient.post(environment.APIUrl + "postDepartment/", department).subscribe();
  }
}
