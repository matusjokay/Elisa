import {Component, Inject, OnInit} from '@angular/core';
import {FormControl, FormGroup, Validators, FormBuilder} from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import {Course} from '../../../models/course';
import {CourseService} from '../../../services/course.service';
import { Department } from 'src/app/models/department';

@Component({
  selector: 'app-course-details',
  templateUrl: './course-details.component.html',
  styleUrls: ['./course-details.component.less']
})
export class CourseDetailsComponent implements OnInit {

  courseForm: FormGroup;
  selectedDepartment: Department;
  dialogLabel: string;
  completionTypes = [
    { name: 'Exam', value: 's'},
    { name: 'State Exam', value: 'st_s'},
    { name: 'Credit', value: 'z'},
    { name: 'Classified Credit', value: 'kz'},
  ];

  constructor(
    public dialogRef: MatDialogRef<CourseDetailsComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any,
    private courseService: CourseService,
    private fb: FormBuilder
  ) { }

  ngOnInit() {
    // this is probably called when a new course is to be made
    if (this.data.courseAction === 'add') {
      this.dialogLabel = 'Add Course';
      // this has to be changed
      // this.data.course = new Object();
      this.courseForm = this.fb.group({
        code: ['', [Validators.required]],
        name: ['', [Validators.required]],
        department: ['', [Validators.required]],
        completion: ['', [Validators.required]],
        credits: ['', [Validators.pattern(/^\d{1,2}$/), Validators.min(1)]],
        teacher: [null],
        period: [null, [Validators.required]]
      });
    } else if (this.data.courseAction === 'edit') {
      this.dialogLabel = 'Edit Course';
      const filteredSelectedDep = this.data.departments.filter(dep => dep.id === this.data.course.department.id);
      this.selectedDepartment = filteredSelectedDep.length > 0 ? filteredSelectedDep[0] : null;
      this.courseForm = this.fb.group({
        code: [this.data.course.code, [Validators.required]],
        name: [this.data.course.name, [Validators.required]],
        department: [this.selectedDepartment.id, [Validators.required]],
        completion: [this.data.course.completion, [Validators.required]],
        credits: [this.data.course.credits, [Validators.pattern(/^\d{1,2}$/)]],
        teacher: [this.data.course.teacher.id]
      });
    } else {
      this.dialogLabel = 'Remove Course';
    }
  }


  onSubmit() {
    // const courseToSubmit: Course = new Course(this.courseForm.value);
    let courseToSubmit = new Course();
    if (this.data.courseAction === 'add') {
      Object.assign(courseToSubmit, this.courseForm.value);
      this.courseService.createCourse(courseToSubmit).subscribe(
        (success) => this.dialogRef.close('added'),
        (error) => this.dialogRef.close('failed')
      );
    } else if (this.data.courseAction === 'edit') {
      courseToSubmit = this.data.course;
      Object.assign(courseToSubmit, this.courseForm.value);
      this.courseService.updateCourse(courseToSubmit).subscribe(
        (success) => this.dialogRef.close('updated'),
        (error) => this.dialogRef.close('failed')
      );
    } else {
      this.courseService.deleteCourse(this.data.course.id).subscribe(
        (success) => this.dialogRef.close(true),
        (error) => this.dialogRef.close('failed')
      );
    }
  }

  onClose() {
    console.log('close dialog');
    this.dialogRef.close(false);
  }
}
