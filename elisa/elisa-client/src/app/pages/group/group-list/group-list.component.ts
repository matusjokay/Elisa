import {Component, OnInit, ViewChild} from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import {GroupService} from '../../../services/group.service';
import {Group} from '../../../models/group';
import {GroupDetailsComponent} from '../group-details/group-details.component';

@Component({
  selector: 'app-group-list',
  templateUrl: './group-list.component.html',
  styleUrls: ['./group-list.component.less']
})
export class GroupListComponent implements OnInit {
  activeScheme;
  schemas;

  pageSizeOptions = [15,50,100];
  groups: Group[] = [];
  displayedColumns: string[] = ['id', 'name', 'abbr', 'parent'];
  dataSource: MatTableDataSource<Group>;
  @ViewChild(MatSort) sort: MatSort;
  @ViewChild(MatPaginator) paginator: MatPaginator;

  constructor(
    private groupService: GroupService,
    public dialog: MatDialog,
  ) { }

  ngOnInit() {
    this.groupService.getAll().subscribe(
      response =>{
        this.groups = response;
        this.dataSource = new MatTableDataSource(this.groups);
        this.dataSource.sort = this.sort;
        this.dataSource.paginator = this.paginator;
      }
    )
  }

  applyFilter(filterValue: string) {
    filterValue = filterValue.trim();
    filterValue = filterValue.toLowerCase();
    this.dataSource.filter = filterValue;
  }

  schemaChange(schema: string) {
    this.activeScheme = schema;
    // this.getSchemeData();
  }

  showDetails(row){
    const dialogRef = this.dialog.open(GroupDetailsComponent, {
      width: '500px',
      data: {group: row, groups: this.groups}
    });
    dialogRef.afterClosed().subscribe(result => {
      if(result){
        this.ngOnInit();
      }
    });
  }

  addGroup(){
    const dialogRef = this.dialog.open(GroupDetailsComponent, {
      width: '500px',
      data: {groups: this.groups}
    });
    dialogRef.afterClosed().subscribe(result => {
      if(result){
        this.ngOnInit();
      }
    });
  }
}
