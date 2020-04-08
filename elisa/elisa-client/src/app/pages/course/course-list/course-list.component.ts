import {Component, OnInit, ViewChild} from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator, PageEvent } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import {Course} from '../../../models/course';
import {CourseService} from '../../../services/course.service';
import {TimetableService} from '../../../services/timetable.service';
import {zip} from 'rxjs';
import {DepartmentService} from '../../../services/department.service';
import {UserDetailsComponent} from '../../users/user-details/user-details.component';
import {CourseDetailsComponent} from '../course-details/course-details.component';
import { catchError } from 'rxjs/operators';
import { Department } from 'src/app/models/department';
import { SnackbarComponent } from 'src/app/common/snackbar/snackbar.component';
import { Period } from 'src/app/models/period.model';
import { BaseService } from 'src/app/services/base-service.service';

@Component({
  selector: 'app-course-list',
  templateUrl: './course-list.component.html',
  styleUrls: ['./course-list.component.less']
})
export class CourseListComponent implements OnInit {
  activeScheme: string;
  schemas;

  periods: Period[];

  pageSizeOptions = [15, 50, 100];
  lastPageIndex: number;
  lastPageSize: number;
  coursesLength: number;
  courses: Course[];
  departments: Department[];
  displayedColumns: string[] = ['id', 'name', 'code', 'teacher', 'department', 'completion', 'credits', 'actions'];
  loading: boolean;
  dataSource: MatTableDataSource<Course>;
  @ViewChild(MatSort) sort: MatSort;
  @ViewChild(MatPaginator) paginator: MatPaginator;

  constructor(
    private courseService: CourseService,
    private departmentService: DepartmentService,
    private timetableService: TimetableService,
    private baseService: BaseService,
    public dialog: MatDialog,
    private snackBar: SnackbarComponent
  ) { }

  ngOnInit() {
    this.activeScheme = !localStorage.getItem('active_scheme') ?
      'UNKNOWN PERIOD' : localStorage.getItem('active_scheme');
    this.getSchemeData();
    this.getDepartmentData();
  }

  getSchemeData() {
    this.timetableService.getCurrentSelectedPeriods().subscribe(
      (response) => {
        this.periods = response;
        this.loading = true;
        this.getCourseData(1, 15);
      }, (error) => {
        console.error('Failed to load periods list');
        catchError(error);
      }
    );
  }

  getDepartmentData() {
    this.departmentService.getCachedDepartments().subscribe(
      (departments) => {
        console.log('Received departments in courseList');
        this.departments = departments;
      }
    );
  }

  onPage(event: PageEvent) {
    this.loadingAction();
    this.getCourseData(event.pageIndex + 1, event.pageSize);
    console.log('page event emitter called');
    console.log(event);
  }

  // getSchemeData(){
  //   zip(
  //     this.courseService.getAll(),
  //     // this.departmentService.getAllMap(),
  //   ).subscribe(([coursesData,departmentsData]) =>{
  //     this.courses = coursesData;
  //     // this.departments = departmentsData;

  //     this.courses.forEach(course =>{
  //       let index = course.department;
  //       course.departmentObject = this.departments[index];
  //     });
  //     this.dataSource = new MatTableDataSource(this.courses);
  //     this.dataSource.sortingDataAccessor = (item, property) => {
  //       switch(property) {
  //         case 'department.name': return item.departmentObject.name;
  //         default: return item[property];
  //       }
  //     };
  //     this.dataSource.sort = this.sort;
  //     this.dataSource.paginator = this.paginator;
  //   });
  // }

  getCourseData(pageNum: number, pageSize: number) {
    this.lastPageIndex = pageNum;
    this.lastPageSize = pageSize;
    this.courseService.getAll(pageNum, pageSize).subscribe(
      (page) => {
        console.log(page);
        this.coursesLength = page.count;
        if (page.results) {
          this.courses = page.results;
          this.dataSource = new MatTableDataSource(this.courses);
        }
      }, (error) => {
        console.error('Failed to load all courses');
        catchError(error);
      }, () => this.loading = false
    );
  }

  applyFilter(filterValue: string) {
    filterValue = filterValue.trim();
    filterValue = filterValue.toLowerCase();
    this.dataSource.filter = filterValue;
  }

  // schemaChange(schema: string) {
  //   this.activeScheme = schema;
  //   this.getSchemeData();
  // }

  showDetails(row) {
    const dialogRef = this.dialog.open(CourseDetailsComponent, {
      width: '500px',
      data: {course: row, departments: this.departments, courseAction: 'edit'}
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        if (result === 'updated') {
          this.snackBar.openSnackBar('Course successfully updated!', 'Close', this.snackBar.styles.success);
          this.loadingAction();
          this.getCourseData(this.lastPageIndex, this.lastPageSize);
        } else if (result === 'failed') {
          this.snackBar.openSnackBar('Failed to update course!', 'Close', this.snackBar.styles.failure);
        }
      }
    });
  }

  removeCourse(row) {
    console.log('removing course');
    console.log(row);
    const dialogRef = this.dialog.open(CourseDetailsComponent, {
      width: '350px',
      data: { course: row, courseAction: 'remove' }
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        if (result === 'failed') { this.snackBar.openSnackBar('Course deletion failed!', 'Close', this.snackBar.styles.failure); } else {
          this.snackBar.openSnackBar('Course successfully deleted!', 'Close', this.snackBar.styles.success);
          this.loadingAction();
          this.getCourseData(this.lastPageIndex, this.lastPageSize);
        }
      }
    });
  }

  handlerTeachersButton(row) {
    console.log('addding teachers');
    console.log(row);
  }

  loadingAction() {
    this.loading = true;
    this.dataSource = null;
  }

  addCourse() {
    const dialogRef = this.dialog.open(CourseDetailsComponent, {
      width: '500px',
      data: { departments: this.departments , courseAction: 'add', periods: this.periods }
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        if (result === 'added') {
          this.snackBar.openSnackBar('Course successfully added!', 'Close', this.snackBar.styles.success);
          this.loadingAction();
          this.getCourseData(this.lastPageIndex, this.lastPageSize);
        } else if (result === 'failed') {
          this.snackBar.openSnackBar('Failed to add course!', 'Close', this.snackBar.styles.failure);
        }
      }
    });
  }
}
