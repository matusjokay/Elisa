import {Component, OnInit, ViewChild} from '@angular/core';
import {User} from '../../../models/user';
import {UserService} from '../../../services/user.service';
import {MatDialog, MatPaginator, MatSort, MatTableDataSource} from '@angular/material';
import {UserDetailsComponent} from '../user-details/user-details.component';

@Component({
  selector: 'app-user-list',
  templateUrl: './user-list.component.html',
  styleUrls: ['./user-list.component.less']
})
export class UserListComponent implements OnInit {

  pageSizeOptions = [15,50,100];
  users: User[] = [];
  displayedColumns: string[] = ['id', 'name'];
  dataSource: MatTableDataSource<User>;
  @ViewChild(MatSort) sort: MatSort;
  @ViewChild(MatPaginator) paginator: MatPaginator;

  constructor(
    private userService: UserService,
    public dialog: MatDialog,
  ) {
  }

  ngOnInit() {
    this.userService.getAll().subscribe(
      response =>{
        this.users = response;
        this.dataSource = new MatTableDataSource(this.users);
        this.dataSource.sort = this.sort;
        this.dataSource.paginator = this.paginator;
      }
    )
  }

  showDetails(row){
    const dialogRef = this.dialog.open(UserDetailsComponent, {
      width: '500px',
      data: row
    });
    dialogRef.afterClosed().subscribe(result => {
      if(result){
        this.ngOnInit();
      }
    });
  }

  addUser(){
    const dialogRef = this.dialog.open(UserDetailsComponent, {
      width: '500px',
    });
    dialogRef.afterClosed().subscribe(result => {
      if(result){
        this.ngOnInit();
      }
    });
  }

  applyFilter(filterValue: string) {
    filterValue = filterValue.trim(); // Remove whitespace
    filterValue = filterValue.toLowerCase(); // Datasource defaults to lowercase matches
    this.dataSource.filter = filterValue;
  }

}
