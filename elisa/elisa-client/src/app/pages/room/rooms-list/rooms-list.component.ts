import {Component, OnInit, ViewChild} from '@angular/core';
import {DepartmentService} from '../../../services/department.service';
import {TimetableService} from '../../../services/timetable.service';
import {RoomService} from '../../../services/room.service';
import {Course} from '../../../models/course';
import {MatDialog, MatPaginator, MatSort, MatTableDataSource} from '@angular/material';
import {zip} from 'rxjs';
import {Room} from '../../../models/room';
import {CourseDetailsComponent} from '../../course/course-details/course-details.component';
import {RoomDetailsComponent} from '../room-details/room-details.component';

@Component({
  selector: 'app-rooms-list',
  templateUrl: './rooms-list.component.html',
  styleUrls: ['./rooms-list.component.less']
})
export class RoomsListComponent implements OnInit {
  activeScheme;
  schemas;

  pageSizeOptions = [15,50,100];
  rooms: Room[] = [];
  departments: any = [];
  displayedColumns: string[] = ['id', 'name', 'capacity', 'category', 'department'];
  dataSource: MatTableDataSource<Room>;
  @ViewChild(MatSort) sort: MatSort;
  @ViewChild(MatPaginator) paginator: MatPaginator;

  constructor(
    private roomService: RoomService,
    private departmentService: DepartmentService,
    private timetableService: TimetableService,
    public dialog: MatDialog,
  ) { }

  ngOnInit() {
    this.timetableService.getAllSchemas().subscribe(
      response =>{
        this.schemas = response;
        this.getSchemeData();
      }
    );
  }

  getSchemeData(){
    zip(
      this.roomService.getAll(),
      this.departmentService.getAllMap(),
    ).subscribe(([roomsData,departmentsData]) =>{
      this.rooms = roomsData;
      this.departments = departmentsData;

      this.rooms.forEach(room =>{
        let index = room.department;
        room.departmentObject = this.departments[index];
      });
      this.dataSource = new MatTableDataSource(this.rooms);
      this.dataSource.sortingDataAccessor = (item, property) => {
        switch(property) {
          case 'department.name': return item.departmentObject.name;
          default: return item[property];
        }
      };
      this.dataSource.sort = this.sort;
      this.dataSource.paginator = this.paginator;
    });
  }

  applyFilter(filterValue: string) {
    filterValue = filterValue.trim();
    filterValue = filterValue.toLowerCase();
    this.dataSource.filter = filterValue;
  }

  schemaChange(schema: string) {
    this.activeScheme = schema;
    this.getSchemeData();
  }

  showDetails(row){
    const dialogRef = this.dialog.open(RoomDetailsComponent, {
      width: '500px',
      data: {room: row, departments: this.departments}
    });
    dialogRef.afterClosed().subscribe(result => {
      if(result){
        this.ngOnInit();
      }
    });
  }

  addRoom(){
    const dialogRef = this.dialog.open(RoomDetailsComponent, {
      width: '500px',
      data: {departments: this.departments}
    });
    dialogRef.afterClosed().subscribe(result => {
      if(result){
        this.ngOnInit();
      }
    });
  }

  roomsImport(){
    this.roomService.importCategoryRooms().subscribe();
  }
}
