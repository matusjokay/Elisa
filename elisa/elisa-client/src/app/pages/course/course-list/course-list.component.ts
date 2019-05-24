import {Component, OnInit, ViewChild} from '@angular/core';
import {MatDialog, MatPaginator, MatSort, MatTableDataSource} from '@angular/material';
import {Course} from '../../../models/course';
import {CourseService} from '../../../services/course.service';
import {TimetableService} from '../../../services/timetable.service';
import {zip} from 'rxjs';
import {DepartmentService} from '../../../services/department.service';
import {UserDetailsComponent} from '../../users/user-details/user-details.component';
import {CourseDetailsComponent} from '../course-details/course-details.component';

@Component({
  selector: 'app-course-list',
  templateUrl: './course-list.component.html',
  styleUrls: ['./course-list.component.less']
})
export class CourseListComponent implements OnInit {
  activeScheme;
  schemas;

  pageSizeOptions = [15,50,100];
  courses: Course[] = [];
  departments: any = [];
  displayedColumns: string[] = ['id', 'name', 'code', 'department'];
  dataSource: MatTableDataSource<Course>;
  @ViewChild(MatSort) sort: MatSort;
  @ViewChild(MatPaginator) paginator: MatPaginator;

  constructor(
    private courseService: CourseService,
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
      this.courseService.getAll(),
      this.departmentService.getAllMap(),
    ).subscribe(([coursesData,departmentsData]) =>{
      this.courses = coursesData;
      this.departments = departmentsData;

      this.courses.forEach(course =>{
        let index = course.department;
        course.departmentObject = this.departments[index];
      });
      this.dataSource = new MatTableDataSource(this.courses);
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
    const dialogRef = this.dialog.open(CourseDetailsComponent, {
      width: '500px',
      data: {course: row, departments: this.departments}
    });
    dialogRef.afterClosed().subscribe(result => {
      if(result){
        this.ngOnInit();
      }
    });
  }

  addCourse(){
    const dialogRef = this.dialog.open(CourseDetailsComponent, {
      width: '500px',
      data: {departments: this.departments}
    });
    dialogRef.afterClosed().subscribe(result => {
      if(result){
        this.ngOnInit();
      }
    });
  }
}
